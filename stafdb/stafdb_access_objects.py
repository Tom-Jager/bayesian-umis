""" Classes to access the prototype stafdb, write and read data from it """
from pathlib import Path

import pandas as pd

# import db_writer_helpers as db_helpers

# PATH_TO_CSVS = Path(
#     '/home/FourthYear/Thesis/Code/bayesian-umis/bayesumis/stafdb/csvs')


PATH_TO_MODULE = Path(
    'stafdb')


# PATH_TO_CSVS = Path(
#     'csvs')


class StafdbAccessObject():

    def __init__(
            self,
            db_folder,
            columns,
            table_path):

        self.columns = columns
        self.table_path = \
            PATH_TO_MODULE.joinpath(db_folder).joinpath(table_path)

    def _load_table(self):

        df = pd.read_csv(self.table_path)
        return df

    def _write_table(self, table: pd.DataFrame):
        table.to_csv(self.table_path, index=False)

    def _reset_table(self):
        new_table = pd.DataFrame([], columns=self.columns)
        self._write_table(new_table)

    def _get_by_id(self, row_id: str, table: pd.DataFrame):
        row_id = int(row_id) - 1
        row_df: pd.DataFrame = table.iloc[row_id, :]
        return row_df.to_dict()


class StafAccessObject(StafdbAccessObject):
    """
    Accesses stafdb_staf.csv, offers operations over it
    """
    
    def __init__(self, db_folder):
        columns = [
            'name',
            'is_stock_or_is_flow',
            'reference_space_id_origin',
            'reference_space_id_destination',
            'reference_timeframe',
            'material_id_reference_material',
            'process_id_origin',
            'process_id_destination']

        table_path = 'stafdb_staf.csv'

        super(StafAccessObject, self).__init__(
            db_folder, columns, table_path)

    def __load_table(self):
        return super(StafAccessObject, self)._load_table()

    def __write_table(self, table):
        return super(StafAccessObject, self)._write_table(table)

    def get_staf_by_id(self, val_id: str):
        table = self.__load_table()
        return super(StafAccessObject, self)._get_by_id(val_id, table)

    def insert_staf(
            self,
            staf_name: str,
            staf_type: str,
            origin_space_id: str,
            dest_space_id: str,
            timeframe_id: str,
            material_id: str,
            origin_id: str,
            destination_id: str):

        name = staf_name
        is_stock_or_flow = staf_type
        reference_space_origin = origin_space_id
        reference_space_destination = dest_space_id
        reference_timeframe = timeframe_id
        material_id_reference_material = material_id
        process_id_origin = origin_id
        process_id_destination = destination_id

        staf_params = [
            name,
            is_stock_or_flow,
            reference_space_origin,
            reference_space_destination,
            reference_timeframe,
            material_id_reference_material,
            process_id_origin,
            process_id_destination]

        table: pd.DataFrame = self.__load_table()

        row = pd.DataFrame([staf_params], columns=self.columns)
        table = table.append(row, ignore_index=True, sort=False)
        self.__write_table(table)

    def reset_table(self):
        return super(StafAccessObject, self)._reset_table()


class ProcessAccessObject(StafdbAccessObject):
    """
    Accesses stafdb_process.csv, offers operations over it
    """

    def __init__(self, db_folder):
        columns = [
            'name',
            'code',
            'process_id_parent',
            'is_separator',
            'process_classification'
        ] 

        table_path = 'stafdb_process.csv'

        super(ProcessAccessObject, self).__init__(
            db_folder, columns, table_path)

    def __load_table(self):
        return super(ProcessAccessObject, self)._load_table()

    def __write_table(self, table):
        return super(ProcessAccessObject, self)._write_table(table)

    def get_process_by_id(self, val_id: str):
        table = self.__load_table()
        return super(ProcessAccessObject, self)._get_by_id(val_id, table)

    def insert_process(
            self,
            process_name: str,
            process_type: str):

        name = process_name
        code = name[:3]
        process_id_parent = 'None'
        is_separator = False

        assert (process_type == 'Transformation'
                or process_type == 'Distribution'
                or process_type == 'Storage')

        process_classification = process_type

        table: pd.DataFrame = self.__load_table()

        process_params = [
            name,
            code,
            process_id_parent,
            is_separator,
            process_classification]

        row = pd.DataFrame([process_params], columns=self.columns)
        table = table.append(row, ignore_index=True, sort=False)
        self.__write_table(table)

    def reset_table(self):
        return super(ProcessAccessObject, self)._reset_table()


class DataAccessObject(StafdbAccessObject):
    """
    Accesses stafdb_data.csv, offers operations over it
    """

    def __init__(self, db_folder):
        columns = [
            'quantity',
            'unit',
            'material_id',
            'name',
            'staf_id',
            'stock_type',
            'uncertainty_json'
        ]

        table_path = 'stafdb_data.csv'

        super(DataAccessObject, self).__init__(
            db_folder, columns, table_path)

    def __load_table(self):
        return super(DataAccessObject, self)._load_table()

    def __write_table(self, table):
        return super(DataAccessObject, self)._write_table(table)

    def get_data_by_stafid(self, staf_id: str):
        table = self.__load_table()
        rows = table.loc[table['staf_id'] == int(staf_id), :]

        dict_list = []
        for index, row in rows.iterrows():
            row_dict = row.to_dict()
            row_dict['datum_id'] = str(index+1)
            dict_list.append(row_dict)

        return dict_list

    def insert_data(
            self,
            quantity: float,
            unit: str,
            material_id: str,
            staf_id: str,
            stock_type: str,
            uncertainty_json: str):
        quantity = float(quantity)
        assert stock_type in ['Net', 'Total', 'Flow']

        name = 'Data_M:{}_Q:{}'.format(material_id, quantity)

        data_params = [
            quantity,
            unit,
            material_id,
            name,
            staf_id,
            stock_type,
            uncertainty_json]

        table: pd.DataFrame = self.__load_table()

        row = pd.DataFrame([data_params], columns=self.columns)
        table = table.append(row, ignore_index=True, sort=False)
        self.__write_table(table)

    def reset_table(self):
        return super(DataAccessObject, self)._reset_table()


class MaterialAccessObject(StafdbAccessObject):
    """
    Accesses stafdb_material.csv, offers operations over it
    """

    def __init__(self, db_folder):
        columns = [
            'name',
            'code',
            'material_id_parent',
            'is_separator'
        ]

        table_path = 'stafdb_material.csv'

        super(MaterialAccessObject, self).__init__(
            db_folder, columns, table_path)

    def __load_table(self):
        table = super(MaterialAccessObject, self)._load_table()
        return table

    def __write_table(self, table):
        return super(MaterialAccessObject, self)._write_table(table)

    def get_material_by_id(self, val_id: str):
        table = self.__load_table()
        return super(MaterialAccessObject, self)._get_by_id(val_id, table)

    def insert_material(
            self,
            name: str):

        code = name[:3]
        material_id_parent = 'None'
        is_separator = False

        material_params = [
            name,
            code,
            material_id_parent,
            is_separator
        ]

        table: pd.DataFrame = self.__load_table()
        row = pd.DataFrame([material_params], columns=self.columns)
        table = table.append(row, ignore_index=False, sort=False)
        self.__write_table(table)

    def reset_table(self):
        return super(MaterialAccessObject, self)._reset_table()


class ReferenceSpaceAccessObject(StafdbAccessObject):
    """
    Accesses stafdb_reference_space.csv, offers operations over it
    """

    def __init__(self, db_folder):
        columns = [
            'name',
        ]

        table_path = 'stafdb_reference_space.csv'

        super(ReferenceSpaceAccessObject, self).__init__(
            db_folder, columns, table_path)

    def __load_table(self):
        table = super(ReferenceSpaceAccessObject, self)._load_table()
        return table

    def __write_table(self, table):
        return super(ReferenceSpaceAccessObject, self)._write_table(table)

    def get_space_by_id(self, val_id: str):
        table = self.__load_table()
        
        return super(
            ReferenceSpaceAccessObject, self)._get_by_id(val_id, table)

    def insert_space(
            self,
            name: str):

        space_params = [
            name,
        ]

        table: pd.DataFrame = self.__load_table()
        row = pd.DataFrame([space_params], columns=self.columns)
        table = table.append(row, ignore_index=False, sort=False)
        self.__write_table(table)

    def reset_table(self):
        return super(ReferenceSpaceAccessObject, self)._reset_table()


class ReferenceTimeframeAccessObject(StafdbAccessObject):
    """
    Accesses stafdb_reference_timeframe.csv, offers operations over it
    """

    def __init__(self, db_folder):
        columns = [
            'name',
            'timeframe_start',
            'timeframe_end'
        ]

        table_path = 'stafdb_reference_timeframe.csv'

        super(ReferenceTimeframeAccessObject, self).__init__(
            db_folder, columns, table_path)

    def __load_table(self):
        table = super(ReferenceTimeframeAccessObject, self)._load_table()
        return table

    def __write_table(self, table):
        return super(ReferenceTimeframeAccessObject, self)._write_table(table)

    def get_timeframe_by_id(self, val_id: str):
        table = self.__load_table()

        return super(
            ReferenceTimeframeAccessObject, self)._get_by_id(val_id, table)

    def insert_timeframe(
            self,
            name: str,
            timeframe_start: int,
            timeframe_end: int):

        space_params = [
            name,
            timeframe_start,
            timeframe_end
        ]

        table: pd.DataFrame = self.__load_table()
        row = pd.DataFrame([space_params], columns=self.columns)
        table = table.append(row, ignore_index=False, sort=False)
        self.__write_table(table)

    def reset_table(self):
        return super(ReferenceTimeframeAccessObject, self)._reset_table()


# sao = StafAccessObject()
# sao.reset_table()
# sao.insert_flow('Test Flow1', '1', '2', '3', '4', '5', '66')
# sao.insert_flow('Test Flow2', '8', '9', '10', '11', '12', '100')
# print(sao.get_staf_by_id("1"))
# print(sao.get_staf_by_id("2"))

# pao = ProcessAccessObject()
# pao.reset_table()
# pao.insert_process("Test Process 121", "Transformation")
# pao.insert_process("Test Process 222", "Distribution")

# print(pao.get_process_by_id("2"))
# print(pao.get_process_by_id("1"))

# dao = DataAccessObject()
# dao.reset_table()

# uncert_string = db_helpers.uniform_uncertainty_string(0, 150)
# dao.insert_data(10, 'g', '1', '99', 'Net', uncert_string)

# norm_string = db_helpers.normal_uncertainty_string(20, 3)
# dao.insert_data(20, 'kg', '1', '99', 'Flow', norm_string)

# dao.insert_data(30, 'g', '1', '99', 'Flow', norm_string)

# dao.insert_data(40, 'g', '1', '100', 'Flow', norm_string)

# dao.insert_data(50, 'g', '1', '99', 'Flow', norm_string)

# dao.insert_data(60, 'g', '1', '100', 'Net', norm_string)

# dao.insert_data(70, 'g', '1', '99', 'Flow', norm_string)

# dao.insert_data(80, 'g', '1', '99', 'Flow', norm_string)

# print(dao.get_data_by_stafid('100'))
# mao = MaterialAccessObject()
# mao.reset_table()
# mao.insert_material('Cannabis')
# mao.insert_material('Water')
# print(mao.get_material_by_id("1"))
# print(mao.get_material_by_id("2"))


# rsao = ReferenceSpaceAccessObject()
# rsao.reset_table()
# rsao.insert_space('United Kingdom')
# rsao.insert_space('Austria')
# print(rsao.get_space_by_id("1"))
# print(rsao.get_space_by_id("2"))


# tao = ReferenceTimeframeAccessObject()
# tao.reset_table()
# tao.insert_timeframe('1994', 1994, 1994)
# tao.insert_timeframe('2005', 2005, 2005)
# print(tao.get_timeframe_by_id("1"))
# print(tao.get_timeframe_by_id("2"))
