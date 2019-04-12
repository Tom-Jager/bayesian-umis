""" Factory class to construct a stock or flow object from staf_id """

import json
from typing import List

from ..bayesumis.umis_data_models import (
    Flow,
    LognormalUncertainty,
    Material,
    NormalUncertainty,
    Process,
    Space,
    StafReference,
    Stock,
    Timeframe,
    UmisProcess,
    UniformUncertainty,
    Value
)

from stafdb_access_objects import (
    DataAccessObject,
    MaterialAccessObject,
    ProcessAccessObject,
    ReferenceSpaceAccessObject,
    ReferenceTimeframeAccessObject,
    StafAccessObject)


class StafFactory():

    def __init__(self):
        self.dao = DataAccessObject()
        self.mao = MaterialAccessObject()
        self.pao = ProcessAccessObject()
        self.rsao = ReferenceSpaceAccessObject()
        self.tao = ReferenceTimeframeAccessObject()
        self.stao = StafAccessObject()

    def build_flow(self, flow_id):
        staf_record = self.stao.get_staf_by_id(flow_id)

        staf_name = staf_record['name']

        reference_material_id = staf_record['material_id_reference_material']
        reference_timeframe_id = staf_record['reference_timeframe']

        staf_reference = self.build_staf_reference(
            reference_material_id, reference_timeframe_id)

        stock_type, material_values_dict = \
            self.build_materials_values_dict(flow_id)

        assert(stock_type == 'Flow')

        process_id_origin = staf_record['process_id_origin']
        reference_space_id_origin = staf_record['reference_space_id_origin']

        origin_process = self.build_process(
            process_id_origin, reference_space_id_origin)

    def build_flows(self, flow_ids: List[str]):

        flows = [self.build_flow(flow_id) for flow_id in flow_ids]
        return flows

    def build_material(self, material_id: str):
        material_record = self.mao.get_material_by_id(material_id)

        code = material_record['code']
        name = material_record['name']
        parent_name = material_record['material_id_parent']
        is_separator = material_record['is_separator']

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
        is_separator = process_record['is_separator']
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

    def build_material_values_dict(self, staf_id: str):
        data_records = self.dao.get_data_by_stafid(staf_id)
        material_values_dict = {}

        stock_types = []
        for data_record in data_records:
            stock_type = data_record['stock_type']
            stock_types.append(stock_type)

            material_id = data_record['material_id']
            material = self.build_material(material_id)

            value = self.build_value_from_data_record(data_record)

            material_values_dict[material] = value

        first_stock_type = stock_types[0]
        for i, stock_type in enumerate(stock_types):
            if stock_type != first_stock_type:
                raise ValueError("Value #{} has a different stock type: {}"
                                 .format(i, stock_type))

        return first_stock_type, material_values_dict

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

        timeframe = Timeframe(timeframe_id, start_time, end_time)
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

