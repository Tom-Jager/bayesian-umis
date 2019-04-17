import json

from stafdb_access_objects import (
    DataAccessObject,
    MaterialAccessObject,
    ProcessAccessObject,
    ReferenceSpaceAccessObject,
    ReferenceTimeframeAccessObject,
    StafAccessObject
)


def reset_tables(db_folder):
    dao = DataAccessObject(db_folder)
    mao = MaterialAccessObject(db_folder)
    pao = ProcessAccessObject(db_folder)
    rsao = ReferenceSpaceAccessObject(db_folder)
    stao = StafAccessObject(db_folder)
    tao = ReferenceTimeframeAccessObject(db_folder)

    dao.reset_table()
    mao.reset_table()
    pao.reset_table()
    rsao.reset_table()
    stao.reset_table()
    tao.reset_table()


def uniform_uncertainty_string(lower, upper):
    lower = float(lower)
    upper = float(upper)
    assert lower < upper

    uncert_dict = {
        'distribution': 'Uniform',
        'lower': lower,
        'upper': upper,
    }

    return json.dumps(uncert_dict)


def normal_uncertainty_string(mean, standard_deviation):
    mean = float(mean)
    standard_deviation = float(standard_deviation)
    assert standard_deviation > 0

    uncert_dict = {
        'distribution': 'Normal',
        'mean': mean,
        'standard_deviation': standard_deviation,
    }

    return json.dumps(uncert_dict)


def lognormal_uncertainty_string(mean, standard_deviation):
    mean = float(mean)
    standard_deviation = float(standard_deviation)

    uncert_dict = {
        'distribution': 'Logormal',
        'mean': mean,
        'standard_deviation': standard_deviation,
    }

    return json.dumps(uncert_dict)


def print_dict(d):
    for key, value in d.items():
        print("{}: {}".format(key, d[key]))


