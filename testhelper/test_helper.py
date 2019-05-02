""" Stub class simulating database for constructing values """

from time import time
from typing import Dict

from bayesumis.umis_data_models import (
    Flow,
    Material,
    Space,
    Stock,
    StockValue,
    StafReference,
    Timeframe,
    UmisProcess,
    Uncertainty,
    Value
)


def end_timer(start_time):
    time_elapsed = time() - start_time
    print("Task finished, time elapsed: {}".format(time_elapsed))


class DbStub():

    def __init__(self):
        self._flow_id_c = 1
        self._stock_id_c = 1
        self._process_id_c = 1
        self._space_id_c = 1
        self._material_id_c = 1
        self._time_id_c = 1
        self._value_id_c = 1

    def get_flow(
            self,
            reference: StafReference,
            material_val: Dict[Material, Value],
            origin: UmisProcess,
            destination: UmisProcess,
            name_prefix: str = ''):

        stafdb_id = "F{}".format(self._flow_id_c)
        name = "{}Flow{}".format(name_prefix, self._flow_id_c)
        flow = Flow(
            stafdb_id,
            name,
            reference,
            origin,
            destination,
            material_val)
        print("|{}|".format(stafdb_id))
        self._flow_id_c += 1
        return flow

    def get_stock(
            self,
            reference: StafReference,
            material_val: Dict[Material, Value],
            origin_process: UmisProcess,
            stock_type: str,
            name_prefix: str = ''):

        stafdb_id = "St{}".format(self._stock_id_c)
        name = "{}Stock{}".format(name_prefix, self._stock_id_c)

        storage_process = self.get_umis_process(
            origin_process.reference_space,
            "Storage")

        stock = Stock(
            stafdb_id,
            name,
            reference,
            origin_process,
            storage_process,
            material_val)

        self._stock_id_c += 1
        print("|{}|".format(stafdb_id))
        return stock

    def get_stock_value(
            self,
            quantity: float,
            uncertainty: Uncertainty):

        value_id = "V{}".format(self._value_id_c)

        self._value_id_c += 1
        print("|{}|".format(value_id))
        return StockValue(value_id, quantity, uncertainty, "g", "Net")

    def get_umis_process(
            self,
            reference_space: Space,
            process_type: str,
            name_prefix: str = ''):

        stafdb_id = "P{}".format(self._process_id_c)
        code = "Code{}".format(self._process_id_c)
        name = "{}Process{}".format(name_prefix, self._process_id_c)

        process = UmisProcess(
            stafdb_id,
            code,
            name,
            reference_space,
            False,
            "parent",
            process_type)

        self._process_id_c += 1
        print("|{}|".format(stafdb_id))
        return process

    def get_space_by_num(self, num: int):        
        stafdb_id = "Sp3"
        name = "London"

        if num == 1:
            stafdb_id = "Sp1"
            name = "Bristol"

        if num == 2:
            stafdb_id = "Sp2"
            name = "Edinburgh"

        print("|{}|".format(stafdb_id))
        return Space(stafdb_id, name)

    def get_time_by_num(self, num: int):

        if num == 1:
            print("|T1|")
            return Timeframe("T1", 2000, 2000)

        print("|T2|")        
        return Timeframe("T2", 2001, 2001)

    def get_material_by_num(self, num: int):
        if num == 1:
            print("|M1|")
            return Material("M1", "CodeM1", "Iron", "Parent", False)

        print("|M2|")
        return Material("M2", "CodeM2", "Nickel", "Parent", False)

    def get_value(
            self,
            quantity: float,
            uncertainty: Uncertainty):

        value_id = "V{}".format(self._value_id_c)

        self._value_id_c += 1
        print("|{}|".format(value_id))
        return Value(value_id, quantity, uncertainty, "g")




