""" Helper functions for umis_diagram.py """
from bayesumis.umis_data_models import Flow


def check_flow_type(flow):
    if not isinstance(flow, Flow):
        raise TypeError(
            "Tried to add {}, when should be adding a Flow"
            .format(flow))
