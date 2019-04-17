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

GRAEDAL_DB_FOLDER = 'csvs_zinc_cycle_graedal_2005'

dao = DataAccessObject(GRAEDAL_DB_FOLDER)


def write_data():
    norm_120 = normal_uncertainty_string(120, 12)
    norm_110 = normal_uncertainty_string(110, 11)
    norm_5 = normal_uncertainty_string(5, 0.5)
    norm_19 = normal_uncertainty_string(19, 1.9)
    norm_4 = normal_uncertainty_string(4, 0.4)
    norm_170 = normal_uncertainty_string(170, 17)
    norm_49 = normal_uncertainty_string(49, 4.9)
    norm_43 = normal_uncertainty_string(43, 4.3)
    norm_130 = normal_uncertainty_string(130, 13)
    norm_23 = normal_uncertainty_string(23, 2.3)
    norm_68 = normal_uncertainty_string(68, 6.8)
    norm_22 = normal_uncertainty_string(22, 2.2)
    norm_6 = normal_uncertainty_string(6, 0.6)

    unknown_0_300 = uniform_uncertainty_string(0, 300)

    dao.insert_data(
        quantity=120,
        unit='Gg/yr',
        material_id='1',
        staf_id='1',
        stock_type='Flow',
        uncertainty_json=norm_120
    )

    dao.insert_data(
        quantity=110,
        unit='Gg/yr',
        material_id='1',
        staf_id='2',
        stock_type='Flow',
        uncertainty_json=norm_110
    )

    dao.insert_data(
        quantity=150,
        unit='Gg/yr',
        material_id='1',
        staf_id='3',
        stock_type='Flow',
        uncertainty_json=unknown_0_300
    )

    dao.insert_data(
        quantity=150,
        unit='Gg/yr',
        material_id='1',
        staf_id='4',
        stock_type='Flow',
        uncertainty_json=unknown_0_300
    )

    dao.insert_data(
        quantity=110,
        unit='Gg/yr',
        material_id='1',
        staf_id='5',
        stock_type='Flow',
        uncertainty_json=norm_110
    )

    dao.insert_data(
        quantity=5,
        unit='Gg/yr',
        material_id='1',
        staf_id='6',
        stock_type='Flow',
        uncertainty_json=norm_5
    )

    dao.insert_data(
        quantity=5,
        unit='Gg/yr',
        material_id='1',
        staf_id='7',
        stock_type='Net',
        uncertainty_json=norm_5
    )

    dao.insert_data(
        quantity=150,
        unit='Gg/yr',
        material_id='1',
        staf_id='8',
        stock_type='Flow',
        uncertainty_json=unknown_0_300
    )

    dao.insert_data(
        quantity=19,
        unit='Gg/yr',
        material_id='1',
        staf_id='9',
        stock_type='Flow',
        uncertainty_json=norm_19
    )

    dao.insert_data(
        quantity=4,
        unit='Gg/yr',
        material_id='1',
        staf_id='10',
        stock_type='Flow',
        uncertainty_json=norm_4
    )

    dao.insert_data(
        quantity=170,
        unit='Gg/yr',
        material_id='1',
        staf_id='11',
        stock_type='Flow',
        uncertainty_json=norm_170
    )

    dao.insert_data(
        quantity=49,
        unit='Gg/yr',
        material_id='1',
        staf_id='12',
        stock_type='Flow',
        uncertainty_json=norm_49
    )

    dao.insert_data(
        quantity=150,
        unit='Gg/yr',
        material_id='1',
        staf_id='13',
        stock_type='Flow',
        uncertainty_json=unknown_0_300
    )

    dao.insert_data(
        quantity=43,
        unit='Gg/yr',
        material_id='1',
        staf_id='14',
        stock_type='Net',
        uncertainty_json=norm_43
    )

    dao.insert_data(
        quantity=130,
        unit='Gg/yr',
        material_id='1',
        staf_id='15',
        stock_type='Flow',
        uncertainty_json=norm_130
    )

    dao.insert_data(
        quantity=150,
        unit='Gg/yr',
        material_id='1',
        staf_id='16',
        stock_type='Flow',
        uncertainty_json=unknown_0_300
    )

    dao.insert_data(
        quantity=23,
        unit='Gg/yr',
        material_id='1',
        staf_id='17',
        stock_type='Flow',
        uncertainty_json=norm_23
    )

    dao.insert_data(
        quantity=68,
        unit='Gg/yr',
        material_id='1',
        staf_id='18',
        stock_type='Flow',
        uncertainty_json=norm_68
    )

    dao.insert_data(
        quantity=22,
        unit='Gg/yr',
        material_id='1',
        staf_id='19',
        stock_type='Flow',
        uncertainty_json=norm_22
    )

    dao.insert_data(
        quantity=6,
        unit='Gg/yr',
        material_id='1',
        staf_id='20',
        stock_type='Flow',
        uncertainty_json=norm_6
    )

    dao.insert_data(
        quantity=150,
        unit='Gg/yr',
        material_id='1',
        staf_id='21',
        stock_type='Flow',
        uncertainty_json=unknown_0_300
    )

    dao.insert_data(
        quantity=150,
        unit='Gg/yr',
        material_id='1',
        staf_id='22',
        stock_type='Flow',
        uncertainty_json=unknown_0_300
    )


write_data()
