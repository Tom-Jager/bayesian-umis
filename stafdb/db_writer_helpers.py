import json


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


