"""
Module for building and running MCMC sampling over a mathematical model
representation of stocks and flows data
"""

import sys
from typing import Dict, Set

import pymc3 as pm

from bayesumis.umis_data_models import (
    Flow,
    UmisProcess,
    Stock)
from bayesumis.umis_diagram import UmisDiagram


class UmisMathModel():
    """
    Model that builds and runs MCMC sampling over a mathematical model
    to perform data reconciliation and error propagation

    Attributes
    ----------
    pm_model (pm.Model): Model holding random variables to run MCMC sampling
        over
    
    math_processes (dict(str, MathProcess)): Dict of process_ids processes in
        the model

    umis_math_process_link (dict(str, str)): Dict mapping id of a umis process
        to the id of a math process
    """

    def __init__(
            self,
            umis_process_store: Dict[str, UmisProcess],
            process_outflows_dict: Dict[str, Set[Flow]],
            external_inflows: Set[Flow],
            external_outflows: Set[Flow]):
        """
        Args
        ----
        process_store (dict(str, UmisProcess)): Dictionary mapping process_id
            to UmisProcess

        process_outflows_dict (dict(str, set(Flow)): Dictionary mapping
            process_id to the process' outflows

        external_inflows (set(flow)): The inflows from outside the model to a
            process in the model

        external_outflows (set(flow)): The outflows from inside the model to a
            process outside the model
        """

        self.str_model = ""


class MathProcess():
    """
    Parent class for calculating mathematical models of processes

    Attributes
    ----------
    math_id (str): Id for the process in the mathematical model
    name (str): Name of the process
    inflows (list(str)): Parameters for flows into the process
    """

    def __init__(self, math_id: str, name: str):
        """
        Args
        ----
        math_id (str): Id for the process in the mathematical model
        name (str): Name of the process
        """

        self.math_id = math_id
        self.name = name
        self.inflows = []
        
    def add_inflow(self, inflow: Flow):
        """
        Add weak prior random variable for an inflow

        Args
        ----
        inflow (Flow): Flow to be converted to RV
        """
        

if __name__ == '__main__':
    sys.exit(1)
