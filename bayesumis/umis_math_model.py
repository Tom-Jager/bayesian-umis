"""
Module for building and running MCMC sampling over a mathematical model
representation of stocks and flows data

Adapted from Lupton, R. C. and Allwood, J. M. (2018), Incremental Material Flow
Analysis with Bayesian Inference. Journal of Industrial Ecology, 22: 1352-1364.
doi:10.1111/jiec.12698

https://github.com/ricklupton/bayesian-mfa-paper
"""

import sys
from typing import Dict, List, Set, Tuple

import numpy as np
import pymc3 as pm
import theano.tensor as T

from bayesumis.umis_data_models import (
    Flow,
    Material,
    Stock,
    Timeframe,
    UmisProcess,
    UniformUncertainty,
    NormalUncertainty)
import bayesumis.umis_math_model_helper as math_helper
from bayesumis.umis_diagram import UmisDiagram


class UmisMathModel():
    """
    Model that builds and runs MCMC sampling over a mathematical model
    to perform data reconciliation and error propagation

    Attributes
    ----------
    pm_model (pm.Model): Model holding random variables to run MCMC sampling
        over
    
    name_math_process_dict (dict(str, MathProcess)): Dict of process names to
        math processes in the model

    """

    def __init__(
            self,
            umis_processes: Set[UmisProcess],
            process_outflows_dict: Dict[str, Set[Flow]],
            external_inflows: Set[Flow],
            external_outflows: Set[Flow],
            reference_material: Material,
            reference_time: Timeframe):
        """
        Args
        ----
        umis_processes (Set[UmisProcess]): Set of the UmisProcesses in the
            model

        process_outflows_dict (dict(str, set(Flow)): Dictionary mapping
            process_id to the process' outflows

        external_inflows (set(flow)): The inflows from outside the model to a
            process in the model

        external_outflows (set(flow)): The outflows from inside the model to a
            process outside the model

        reference_material (Material): The material being balanced

        reference_time (Timeframe): The timeframe over which the stocks and
            flows are modeled
        """

        self.reference_material = reference_material
        self.reference_time = reference_time

        # Assigns a new index to each process
        self.__index_counter = 0

        self.__name_math_process_dict: Dict[str, MathProcess] = {}
        """ Maps a math process name to its math process """

        self.__create_math_processes(
            umis_processes,
            process_outflows_dict,
            external_inflows,
            external_outflows)

    def __create_math_process(
            self,
            process_name: str,
            process_type: str,
            outflow_names: Set[str] = set()) -> int:
        """
        Create a mathematical process and increments index counter

        Args
        ----
        process_name (str):
        process_type (str):
        outflow_names (set(Flow)): Names of output processes
        """
        if process_type == 'Transformation':
            math_process = MathTransformationProcess(
                process_name,
                self.__index_counter,
                outflow_names)
        else:
            if process_type == 'Distribution':
                math_process = MathDistributionProcess(
                    process_name,
                    self.__index_counter,
                    outflow_names)
            else:
                if process_type == 'Storage':
                    math_process = MathStorageProcess(
                        process_name,
                        self.__index_counter)
                else:
                    raise ValueError("Process type was invalid, received {}"
                                     .format(process_type))

        self.__name_math_process_dict[process_name] = math_process
        self.__index_counter += 1

    def __create_math_processes(
            self,
            umis_processes: Set[UmisProcess],
            process_outflows_dict: Dict[str, Set[Flow]],
            external_inflows: Set[Flow],
            external_outflows: Set[Flow]):
        """ Generates the math models of processes from stocks and flows """

        self.__create_math_processes_from_stocks(umis_processes)

    def __create_math_processes_from_internal_flows(
            self,
            intenal_flows: Set[Flow]):
        """
        Take the flows and creates internal_flows from them

        Args
        ----
        internal_flows (set(Flow)): Flows internal to the diagram
        """
        for flow in internal_flows:
            # Checks flow is about correct reference time
            if flow.reference.time == self.reference_time:

                # Checks flow has an entry for the reference material
                if flow.get_value(self.reference_material):
                    value = flow.get_value(self.reference_material)
                    # TODO Unit reconciliation
                    origin_name = math_helper \
                        .get_process_name(
                            flow.origin.code,
                            flow.reference.space)

                    destination_name = math_helper \
                        .get_process_name(
                            flow.destination.code,
                            flow.reference.space)

                    # If origin process has not been created yet then
                    # create it
                    if (not self.__name_math_process_dict
                                .__contains__(origin_name)):
                        self.__create_math_process(
                            origin_name,
                            flow.origin.process_type,
                            {destination_name})
                    # Otherwise add the outflow to the existing process
                    else:
                        self.__name_math_process_dict[origin_name] \
                            .add_outflow(destination_name)

                    # If destination process has not been created yet then
                    # create it
                    if (not self.__name_math_process_dict
                                .__contains__(destination_name)):
                        self.__create_math_process(
                            destination_name,
                            flow.destination.process_type)

                else:
                    # TODO do material reconciliation stuff
                    continue

    def __create_math_processes_from_external_outflows(
            self,
            outflows: Set[Flow]):
        """
        Take the flows and creates internal_flows from them

        Args
        ----
        internal_flows (set(Flow)): Flows internal to the diagram
        """
        for flow in outflows:
            # Checks flow is about correct reference time
            if flow.reference.time == self.reference_time:

                # Checks flow has an entry for the reference material
                if flow.get_value(self.reference_material):
                    value = flow.get_value(self.reference_material)
                    # TODO Unit reconciliation
                    origin_name = math_helper \
                        .get_process_name(
                            flow.origin.code,
                            flow.reference.space)

                    destination_name = math_helper \
                        .get_process_name(
                            flow.destination.code,
                            flow.reference.space)

                    # If origin process has not been created yet then
                    # create it
                    if (not self.__name_math_process_dict
                                .__contains__(origin_name)):
                        self.__create_math_process(
                            origin_name,
                            flow.origin.process_type,
                            {destination_name})
                    # Otherwise add the outflow to the existing process
                    else:
                        self.__name_math_process_dict[origin_name] \
                            .add_outflow(destination_name)

                    # If destination process has not been created yet then
                    # create it
                    if (not self.__name_math_process_dict
                                .__contains__(destination_name)):
                        self.__create_math_process(
                            destination_name,
                            flow.destination.process_type)

                else:
                    # TODO do material reconciliation stuff
                    continue

    def __create_math_processes_from_stocks(
            self,
            umis_processes: Set[UmisProcess],
            index_counter: int) -> int:
        """
        Take the stocks assigned to processes and create mathematical
        processes from them

        Args
        ----
        umis_processes (list(UmisProcess)):
        index_counter (int): Counter to assign a process an index in the
            process matrix
        """

        for process in umis_processes:
            if process.get_stock('Net'):

                # Check if process has a stock
                stock = process.get_stock('Net')

                if stock.


class TransformationCoefficient():
    """
    TC for a transformation process with storage, modelled as normally
    distributed. Represent the proportion going into storage

    Attributes
    ----------
    mean (np.float): Expected value of TC
    sd (np.float): Standard deviation of TC
    """

    def __init__(
            self,
            mean: float,
            lower_uncertainty: float,
            upper_uncertainty: float):
        """
        Log shifts the mean and standard deviation values to ensure they don't
        pass 0 or 1

        Args
        ----
        mean (float): Expected value of TC
        lower_uncertainty (float):  Lower uncertainty value of TC
        upper_uncertainty (float): Upper uncertainty value of TC
        """

        def logit(x):
            return -np.log(1/x - 1)

        def logit_range_sd(a, b):
            return (logit(b) - logit(a)) / 4

        self.mean = logit(mean)
        self.sd = logit_range_sd(lower_uncertainty, upper_uncertainty)


class DistributionCoefficients():
    """
    TC(s) for a distribution process with storage, modelled as normally
    distributed

    Attributes
    ----------
    shares (List[float]): Expected values of TCs
    """

    def __init__(self, shares: List[float]):
        """
        Args
        ----------
        shares (List[float]): Expected values of TCs
        """

        self.shares = shares


class MathProcess():
    """
    Parent class for calculating mathematical models of processes

    Attributes
    ----------
    process_name (str): Name of the process
    process_ind (int): Index of process in the matrix
    outflow_processes_names (list(str)): Names of each process receiving a flow
    n_outflows (int): Number of outflows of the process
    """

    def __init__(
            self,
            process_name: str,
            process_ind: int,
            outflow_processes_names: Set[str]):
        """
        Args
        ----
        name (str): Name of the process
        process_ind (int): Index of process in the matrix
        outflow_processes_names (list(str)): Names of each process receiving a
            flow
        """
        self.process_name = process_name
        self.process_ind = process_ind
        self.outflow_processes_names = outflow_processes_names
        self.n_outflows = len(outflow_processes_names)


class MathDistributionProcess(MathProcess):
    """
    Represents a distribution process in the mathematical model

    Parent Attributes
    ----------
    process_name (str): Name of the process
    process_ind (int): Index of process in the matrix
    outflow_processes_names (list(str)): Names of each process receiving a flow
    n_outflows (int): Number of outflows of the process
    """

    def __init__(
            self,
            process_name: str,
            process_ind: int,
            outflow_processes_names: Set[str]):
        """
        Args
        ----
        process_name (str): Process name
        process_ind (int): Index of process in the matrix
        outflow_processes_names (list(str)): Names of each process receiving a
            flow
        """

        super().__init__(process_name, process_ind, outflow_processes_names)

    def add_outflow(self, outflow_process_name: str):
        """
        Add an outflow to the process

        Args
        ----
        outflow_process_name (str):
        """
        if self.outflow_processes_names.__contains__(outflow_process_name):
            raise ValueError(
                "Process {} already contains outflow to process {}"
                .format(self.process_name, outflow_process_name))

        self.outflow_processes_names.add(outflow_process_name)
        self.n_outflows += 1

    def create_param_rv(
            self,
            dist_coeffs: DistributionCoefficients = None):
        """
        Create RVs for transfer coefficients for the process

        Args
        ----
        dist_coeffs (DistributionCoefficients): known transfer coefficients
        """

        assert (self.n_outflows == len(self.outflow_processes_names) and
                self.n_outflows > 0)

        if not dist_coeffs:
            # If no coefficients supplied, model as a uniform dirichlet
            # distribution
            shares = np.ones(self.n_outflows, dtype=np.dtype(float))
        else:
            shares = dist_coeffs.shares

        if(len(shares) != self.n_outflows):
            raise ValueError(
                "Must supply a transfer_coefficient for each outflow or None")
        
        if self.n_outflows == 1:
            return pm.Deterministic(self.process_name, T.ones(1,))
        else:
            return pm.Dirichlet(self.process_name, shares)

    @staticmethod
    def transfer_functions(transfer_coeff_rv):
        """
        Logistic function applied to first transfer coefficient to ensure it
        doesn't exceed 1 or fall below 0

        Args
        ----
        transfer_coeff_rv (pm.Continuous): RV representing transfer
            coefficients
        """
        logistic_tc_1 = (T.exp(transfer_coeff_rv[0]) /
                         1 + T.exp(transfer_coeff_rv[0]))

        return T.stack(logistic_tc_1, 1 - logistic_tc_1) 


class MathTransformationProcess(MathProcess):
    """
    Represents a transformation process in the mathematical model

    Parent Attributes
    ----------
    process_name (str): Name of the process
    process_ind (int): Index of process in the matrix
    outflow_processes_names (list(str)): Names of each process receiving a flow
    n_outflows (int): Number of outflows of the process
    """

    def __init__(
            self,
            process_name: str,
            process_ind: int,
            outflow_processes_names: Set[str]):
        """
        Args
        ----
        process_name (str): Process name
        process_ind (int): Index of process in the matrix
        outflow_processes_names (list(str)): Names of each process receiving a
            flow
        """

        if len(outflow_processes_names) > 2:
            raise ValueError(
                "A transformation process can have at most 2 outflows")

        super().__init__(process_name, process_ind, outflow_processes_names)

    def add_outflow(self, outflow_process_name: str):
        """
        Add an outflow to the process

        Args
        ----
        outflow_process_name (str):
        """
        if self.outflow_processes_names.__contains__(outflow_process_name):
            raise ValueError(
                "Process {} already contains outflow to process {}"
                .format(self.process_name, outflow_process_name))

        if self.n_outflows >= 2:
            raise ValueError(
                "A transformation process can have at most 2 outflows")

        self.outflow_processes_names.add(outflow_process_name)
        self.n_outflows += 1

    def create_param_rv(
            self,
            transform_coeff: TransformationCoefficient = None):
        """
        Create RV for the transfer coefficient for the process

        Args
        ----
        transform_coeff (TransformationCoefficient): Known mean and standard
        deviation for transfer coefficient to storage process
        """

        assert (self.n_outflows == len(self.outflow_processes_names) and
                self.n_outflows > 0)

        if self.n_outflows == 1:
            return pm.Deterministic(self.process_name, T.ones(1,))

        if not transform_coeff:
            # If no tc supplied, model as a uniform distribution
            return pm.Uniform(self.process_name, lower=0, upper=1)
        else:

            if ((transform_coeff.sd and not transform_coeff.mean) or
                    (transform_coeff.mean and not transform_coeff.sd)):
                raise ValueError(
                    "Must supply either both mean and standard deviation or " +
                    "no tranfer coefficient")

            return pm.Normal(
                self.process_name,
                mu=transform_coeff.mean,
                sd=transform_coeff.sd)

    @staticmethod
    def transfer_functions(transfer_coeff_rv):
        """
        Function applied to transfer coefficients to convert into correct
        theano values

        Args
        ----
        tranfer_coeff_rv (pm.Continuous): RV representing transfer coefficients
        """
        return transfer_coeff_rv


class MathStorageProcess(MathProcess):
    """
    Represents a storage process in the mathematical model

    Parent Attributes
    ----------
    process_name (str): Name of the process
    process_ind (int): Index of process in the matrix
    outflow_processes_names (list(str)): Names of each process receiving a flow
    n_outflows (int): Number of outflows of the process
    """

    def __init__(self, process_name: str, process_ind: int):
        """
        Args
        ----
        process_name (str): Name of the process
        process_ind (int): Index of process in the matrix
        """
        # Does not provide any outflows as storage process in math model should
        # not have outflows
        super().__init__(process_name, process_ind, set())

    def create_param_rv(self):
        """
        No random variable associated with process as there are no outflows
        """
        return None

    @staticmethod
    def transfer_functions(tranfer_coeff_rv):
        """
        Function applied to transfer coefficients to convert into correct
        theano values

        Args
        ----
        tranfer_coeff_rv (pm.Continuous): RV representing transfer coefficients
        """
        return T.dvector()
