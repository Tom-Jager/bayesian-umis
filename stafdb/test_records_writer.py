from db_writer_helpers import (
    lognormal_uncertainty_string,
    normal_uncertainty_string,
    reset_tables,
    uniform_uncertainty_string
)
from stafdb_access_objects import (
    DataAccessObject,
    MaterialAccessObject,
    ProcessAccessObject,
    ReferenceSpaceAccessObject,
    ReferenceTimeframeAccessObject,
    StafAccessObject
)

dao = DataAccessObject()
mao = MaterialAccessObject()
pao = ProcessAccessObject()
rsao = ReferenceSpaceAccessObject()
stao = StafAccessObject()
tao = ReferenceTimeframeAccessObject()


def write_processes():
    pao.insert_process('TP1: Test Process 1', 'Distribution')
    pao.insert_process('TP2: Test Process 2', 'Transformation')
    pao.insert_process('TP3: Test Process 3', 'Storage')
    pao.insert_process('TP4: Test Process 4', 'Distribution')


def write_spaces():
    rsao.insert_space('Sp1')
    rsao.insert_space('Sp2')
    

def write_materials():
    mao.insert_material('Test Material')


def write_timeframe():
    tao.insert_timeframe('Test TF', 1994, 1995)


def write_stafs():
    stao.insert_staf(
        staf_name='Flow1',
        staf_type='Flow',
        origin_space_id='2',
        dest_space_id='1',
        timeframe_id='1',
        material_id='1',
        origin_id='1',
        destination_id='2')

    stao.insert_staf(
        staf_name='Stock1',
        staf_type='Stock',
        origin_space_id='1',
        dest_space_id='1',
        timeframe_id='1',
        material_id='1',
        origin_id='2',
        destination_id='3')

    stao.insert_staf(
        staf_name='Flow2',
        staf_type='Flow',
        origin_space_id='1',
        dest_space_id='2',
        timeframe_id='1',
        material_id='1',
        origin_id='2',
        destination_id='4')


def write_data():
    norm_100 = normal_uncertainty_string(100, 10)
    dao.insert_data(
        quantity=100,
        unit='g',
        material_id='1',
        staf_id='1',
        stock_type='Flow',
        uncertainty_json=norm_100
    )

    norm_30 = normal_uncertainty_string(30, 3)
    dao.insert_data(
        quantity=30,
        unit='g',
        material_id='1',
        staf_id='2',
        stock_type='Net',
        uncertainty_json=norm_30
    )

    norm_70 = normal_uncertainty_string(70, 7)
    dao.insert_data(
        quantity=70,
        unit='g',
        material_id='1',
        staf_id='3',
        stock_type='Net',
        uncertainty_json=norm_70
    )

reset_tables()
write_processes()
write_spaces()
write_materials()
write_timeframe()
write_stafs()
write_data()
