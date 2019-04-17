""" Factory class to construct a stock or flow object from staf_id """

import json
from typing import List

from bayesumis.umis_data_models import (
    Flow,
    LognormalUncertainty,
    Material,
    NormalUncertainty,
    Space,
    StafReference,
    Stock,
    StockValue,
    Timeframe,
    UmisProcess,
    UniformUncertainty,
    Value
)

from stafdb.stafdb_access_objects import (
    DataAccessObject,
    MaterialAccessObject,
    ProcessAccessObject,
    ReferenceSpaceAccessObject,
    ReferenceTimeframeAccessObject,
    StafAccessObject)


class StafFactory():

    def __init__(self, db_folder):
        self.dao = DataAccessObject(db_folder)
        self.mao = MaterialAccessObject(db_folder)
        self.pao = ProcessAccessObject(db_folder)
        self.rsao = ReferenceSpaceAccessObject(db_folder)
        self.tao = ReferenceTimeframeAccessObject(db_folder)
        self.stao = StafAccessObject(db_folder)

    def build_staf(self, staf_id: str):
        staf_record = self.stao.get_staf_by_id(staf_id)

        staf_name = staf_record['name']

        reference_material_id = staf_record['material_id_reference_material']
        reference_timeframe_id = staf_record['reference_timeframe']

        staf_reference = self.build_staf_reference(
            reference_material_id, reference_timeframe_id)

        stock_or_flow = staf_record['is_stock_or_is_flow']

        process_id_origin = staf_record['process_id_origin']
        reference_space_id_origin = staf_record['reference_space_id_origin']

        origin_process = self.build_process(
            process_id_origin, reference_space_id_origin)

        process_id_destination = staf_record['process_id_destination']
        
        reference_space_id_destination = \
            staf_record['reference_space_id_destination']

        destination_process = self.build_process(
            process_id_destination, reference_space_id_destination)

        if stock_or_flow == 'Flow':
            material_value_dict = \
                self.build_material_value_dict(staf_id)

            flow = Flow(
                staf_id,
                staf_name,
                staf_reference,
                origin_process,
                destination_process,
                material_value_dict)

            return flow
        else:
            if stock_or_flow == 'Stock':
                material_stock_value_dict = \
                    self.build_material_stock_value_dict(staf_id)

                stock = Stock(
                    staf_id,
                    staf_name,
                    staf_reference,
                    origin_process,
                    destination_process,
                    material_stock_value_dict)

                return stock
            else:
                raise ValueError("stock_or_flow value must be either 'Stock'"
                                 + "or 'Flow', was {} instead"
                                 .format(stock_or_flow))

    def build_stafs(self, staf_ids: List[str]):

        stafs = [self.build_staf(staf_id) for staf_id in staf_ids]
        return stafs

    def build_material(self, material_id: str):
        material_record = self.mao.get_material_by_id(material_id)

        code = material_record['code']
        name = material_record['name']
        parent_name = material_record['material_id_parent']
        is_separator = bool(material_record['is_separator'])

        material = Material(
            str(material_id),
            code,
            name,
            parent_name,
            is_separator)

        return material

    def build_process(self, process_id: str, space_id: str):
        space = self.build_space(space_id)
        
        process_record = self.pao.get_process_by_id(process_id)
        code = process_record['code']
        name = process_record['name']
        is_separator = bool(process_record['is_separator'])
        parent_name = process_record['process_id_parent']
        process_type = process_record['process_classification']

        process = UmisProcess(
            str(process_id),
            code,
            name,
            space,
            is_separator,
            parent_name,
            process_type)

        return process

    def build_space(self, space_id: str):
        space_record = self.rsao.get_space_by_id(space_id)

        space_name = space_record['name']
        space = Space(str(space_id), space_name)
        return space

    def build_material_stock_value_dict(self, staf_id: str):
        data_records = self.dao.get_data_by_stafid(staf_id)
        material_stock_value_dict = {}

        for data_record in data_records:
            material_id = data_record['material_id']
            material = self.build_material(material_id)

            stock_value = self.build_stock_value_from_data_record(data_record)

            material_stock_value_dict[material] = stock_value

        return material_stock_value_dict

    def build_material_value_dict(self, staf_id: str):
        data_records = self.dao.get_data_by_stafid(staf_id)
        material_values_dict = {}

        for data_record in data_records:
            material_id = data_record['material_id']
            material = self.build_material(material_id)

            value = self.build_value_from_data_record(data_record)

            material_values_dict[material] = value

        return material_values_dict

    def build_staf_reference(
            self,
            reference_material_id: str,
            reference_timeframe_id: str):

        material = self.build_material(reference_material_id)
        timeframe = self.build_timeframe(reference_timeframe_id)

        staf_reference = StafReference(timeframe, material)
        return staf_reference

    def build_timeframe(self, timeframe_id):
        timeframe_record = self.tao.get_timeframe_by_id(timeframe_id)

        start_time = int(timeframe_record['timeframe_start'])
        end_time = int(timeframe_record['timeframe_end'])

        timeframe = Timeframe(str(timeframe_id), start_time, end_time)
        return timeframe

    def build_uncertainty_from_string(self, uncertainty_string):
        uncertainty_dict = json.loads(uncertainty_string)
        if uncertainty_dict['distribution'] == 'Uniform':
            lower = float(uncertainty_dict['lower'])
            upper = float(uncertainty_dict['upper'])

            return UniformUncertainty(lower, upper)

        if uncertainty_dict['distribution'] == 'Normal':
            mean = float(uncertainty_dict['mean'])
            standard_deviation = float(uncertainty_dict['standard_deviation'])

            return NormalUncertainty(mean, standard_deviation)

        if uncertainty_dict['distribution'] == 'Lognormal':
            mean = float(uncertainty_dict['mean'])
            standard_deviation = float(uncertainty_dict['standard_deviation'])

            return LognormalUncertainty(mean, standard_deviation)

        raise ValueError("Uncertainty distribution: {} is unknown"
                         .format(uncertainty_dict['distribution']))
    
    def build_value_from_data_record(self, data_record):
        stafdb_id = data_record['datum_id']
        quantity = float(data_record['quantity'])

        uncertainty_string = data_record['uncertainty_json']
        uncertainty = self.build_uncertainty_from_string(uncertainty_string)

        unit = data_record['unit']

        value = Value(
            stafdb_id,
            quantity,
            uncertainty,
            unit)

        return value

    def build_stock_value_from_data_record(self, data_record):
        stafdb_id = data_record['datum_id']
        quantity = float(data_record['quantity'])

        uncertainty_string = data_record['uncertainty_json']
        uncertainty = self.build_uncertainty_from_string(uncertainty_string)

        unit = data_record['unit']

        stock_type = data_record['stock_type']

        stock_value = StockValue(
            stafdb_id,
            quantity,
            uncertainty,
            unit,
            stock_type)

        return stock_value

