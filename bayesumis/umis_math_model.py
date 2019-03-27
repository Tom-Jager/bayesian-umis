"""
Module for building and running MCMC sampling over a mathematical model
representation of stocks and flows data

Adapted from Lupton, R. C. and Allwood, J. M. (2018), Incremental Material Flow
Analysis with Bayesian Inference. Journal of Industrial Ecology, 22: 1352-1364.
doi:10.1111/jiec.12698

https://github.com/ricklupton/bayesian-mfa-paper
"""

import sys
from typing import Dict, List, Set

import numpy as np
import pymc3 as pm
import theano.tensor as T

from bayesumis.umis_data_models import (
    Flow,
    LognormalUncertainty,
    NormalUncertainty,
    Material,
    Stock,
    Timeframe,
    UmisProcess,
    Uncertainty,
    UniformUncertainty,
    Value)
import bayesumis.umis_math_model_helper as math_helper

class UmisMathModel():
    """
    Model that builds and runs MCMC sampling over a mathematical model
    to perform data reconciliation and error propagation

    Attributes
    ----------
    pm_model (pm.Model): Model holding random variables to run MCMC sampling
        over
    """

    def __init__(
            self,
            umis_processes: Set[UmisProcess],
            process_outflows_dict: Dict[str, Set[Flow]],
            external_inflows: Set[Flow],
            external_outflows: Set[Flow],
            transfer_coefficient_obs: List['TCObs'],
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

        self.__id_math_process_dict: Dict[str, MathProcess] = {}
        """ Maps a math process id to its math process """

        self.__input_priors: Set[InputPrior] = set()

        self.__normal_observations: Set[StafParameter] = set()
        """ Collection of normally distributed observations of Staf values """

        self.__lognormal_observations: Set[StafParameter] = set()
        """ Collection of lognormally distributed observations of Staf values """

        self.__flow_observations: Set[StafParameter] = set()
        # Set of relevant flows with random variable and index information

        self.__create_math_processes(
            umis_processes,
            process_outflows_dict,
            external_inflows,
            external_outflows)

    def __create_math_process(
            self,
            process_id: str,
            process_type: str,
            outflow_ids: Set[str] = set()):
        """
        Create a mathematical process and increments index counter

        Args
        ----
        process_id: (str): Unique identifier of math process
        process_type (str):
        outflow_ids (set(Flow)): Ids of output processes
        """
        if process_type == 'Transformation':
            math_process = MathTransformationProcess(
                process_id,
                self.__index_counter,
                outflow_ids)
        else:
            if process_type == 'Distribution':
                math_process = MathDistributionProcess(
                    process_id,
                    self.__index_counter,
                    outflow_ids)
            else:
                if process_type == 'Storage':
                    math_process = MathStorageProcess(
                        process_id,
                        self.__index_counter)
                else:
                    raise ValueError("Process type was invalid, received {}"
                                     .format(process_type))

        self.__id_math_process_dict[process_id] = math_process
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
            internal_flows: Set[Flow]):
        """
        Take the flows and creates internal_flows from them

        Args
        ----
        internal_flows (set(Flow)): Flows internal to the diagram
        """
        for flow in internal_flows:
            # Checks flow is about correct reference time
            if flow.reference.time == self.reference_time:
                
                value = flow.get_value(self.reference_material)
                # Checks flow has an entry for the reference material
                if value:

                    # TODO Unit reconciliation
                    # Would involve getting value and checking unit

                    origin_id = self.__get_process_math_id(
                        flow.origin.uuid,
                        flow.reference.space.id)

                    destination_id = self.__get_process_math_id(
                        flow.destination.uuid,
                        flow.reference.space.uuid)

                    # If origin process has not been created yet then
                    # create it
                    if (not self.__id_math_process_dict
                                .__contains__(origin_id)):
                        self.__create_math_process(
                            origin_id,
                            flow.origin.process_type,
                            {destination_id})
                    # Otherwise add the outflow to the existing process
                    else:
                        self.__id_math_process_dict[origin_id] \
                            .add_outflow(destination_id)

                    # If destination process has not been created yet then
                    # create it
                    if (not self.__id_math_process_dict
                                .__contains__(destination_id)):
                        self.__create_math_process(
                            destination_id,
                            flow.destination.process_type)

                else:
                    # TODO do material reconciliation stuff
                    continue

    def __create_math_processes_from_external_outflows(
            self,
            outflows: Set[Flow]):
        """
        Take the external outflows and creates processes from them

        Args
        ----
        external_outflows (set(Flow)): Flows from the diagram out
        """
        for flow in outflows:
            # Checks flow is about correct reference time
            if flow.reference.time == self.reference_time:
                
                value = flow.get_value(self.reference_material) 
                # Checks flow has an entry for the reference material
                if value:

                    # TODO Unit reconciliation

                    origin_id = self.__get_process_math_id(
                        flow.origin.uuid,
                        flow.reference.space.id)

                    destination_id = self.__get_process_math_id(
                        flow.destination.uuid,
                        flow.reference.space.uuid)

                    # If origin process has not been created yet then
                    # create it
                    if (not self.__id_math_process_dict
                                .__contains__(origin_id)):
                        self.__create_math_process(
                            origin_id,
                            flow.origin.process_type,
                            {destination_id})
                    # Otherwise add the outflow to the existing process
                    else:
                        self.__id_math_process_dict[origin_id] \
                            .add_outflow(destination_id)

                    # If destination process has not been created yet then
                    # create it as a storage process
                    if (not self.__id_math_process_dict
                                .__contains__(destination_id)):
                        self.__create_math_process(
                            destination_id,
                            'Storage')

                else:
                    # TODO do material reconciliation stuff
                    continue

    def __create_math_processes_from_stocks(
            self,
            umis_processes: Set[UmisProcess]):
        """
        Take the stocks assigned to processes and create mathematical
        processes from them

        Args
        ----
        umis_processes (list(UmisProcess)):
        """

        for process in umis_processes:
            # TODO dealing with total stock
            if process.get_stock('Net'):

                # Check if process has a stock
                stock = process.get_stock('Net')

                # Check stock is about correct reference time
                if stock.reference.time == self.reference_time:
                    
                    value = stock.get_value(self.reference_material)
                    # Check if stock has value for reference material
                    if value:
   
                        if value > 0:
                            # Model as a flow to a storage process
                            origin_id = self.__get_process_math_id(
                                process.uuid,
                                stock.reference.space.uuid)

                            dest_id = self.__get_process_storage_math_id(
                                process.uuid,
                                stock.reference.space.uuid)

                            # If origin process has not been created yet then
                            # create it
                            if (not self.__id_math_process_dict
                                        .__contains__(origin_id)):
                                self.__create_math_process(
                                    origin_id,
                                    stock.origin.process_type,
                                    {dest_id})
                            # Otherwise add the outflow to the existing process
                            else:
                                self.__id_math_process_dict[origin_id] \
                                    .add_outflow(dest_id)

                            # If destination process has not been created yet then
                            # create it as a storage process
                            if (not self.__id_math_process_dict
                                        .__contains__(dest_id)):
                                self.__create_math_process(
                                    dest_id,
                                    'Storage')

                        else:
                            # Model as an internal flow
                            
                        # find process id
                        pass

                    else:
                        # TODO more material reconciliation stuff
                        continue

    def __create_staf_observation(
            self,
            val_uncertainty: Uncertainty,
            origin_process_id: str,
            dest_process_id: str):
        """
        Check if staf value is an observation and create observation
        object if so

        Args
        ----
        val_uncertainty (Uncertainty): Uncertainty of staf value
        origin_process_id (str):
        dest_process_id (str): Id of destination process
        """

        if (isinstance(val_uncertainty, NormalUncertainty)):
            row_ind = self.__get_process_ind(origin_process_id)
            col_ind = self.__get_process_ind(dest_process_id)

            observation = StafParameter(
                row_ind,
                col_ind,
                val_uncertainty.mean,
                val_uncertainty.standard_deviation)

            self.__normal_observations.add(observation)

        if (isinstance(val_uncertainty, LognormalUncertainty)):
            row_ind = self.__get_process_ind(origin_process_id)
            col_ind = self.__get_process_ind(dest_process_id)

            observation = StafParameter(
                row_ind,
                col_ind,
                val_uncertainty.mean,
                val_uncertainty.standard_deviation)

            self.__lognormal_observations.add(observation)
        
    def __get_process_ind(self, process_id: str) -> int:
        """ Returns the index of the process in the matrix if id exists """

        ind = self.__id_math_process_dict[process_id]
        if not ind:
            raise ValueError("Process id {} does not exist"
                             .format(process_id))

        return ind

    def __get_process_math_id(
            self,
            process_stafdb_id: str,
            space_stafdb_id: str) -> str:
        """
        Makes a math id from process and space stafdb ids
        
        Args
        ----
        process_stafdb_id (str): Id of process in stafdb
        space_stafdb_id (str): Process space's id in stafdb
        """
        process_math_id = "{}_{}".format(
            process_stafdb_id, space_stafdb_id)

        return process_math_id

    def __get_process_storage_math_id(
            self,
            process_stafdb_id: str,
            space_stafdb_id: str) -> str:
        """
        Makes a math id for storage to a process
        
        Args
        ----
        process_stafdb_id (str): Id of process in stafdb
        space_stafdb_id (str): Process space's id in stafdb
        """
        process_math_id = "{}_{}_STORAGE".format(
            process_stafdb_id, space_stafdb_id)

        return process_math_id


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
    process_id (str): Id for the process in the math model
    process_ind (int): Index of process in the matrix
    outflow_processes_ids (list(str)): Math ids of each process receiving a
        flow
    n_outflows (int): Number of outflows of the process
    """

    def __init__(
            self,
            process_id: str,
            process_ind: int,
            outflow_processes_ids: Set[str]):
        """
        Args
        ----
        process_id (str): Id for the process in the math model
        process_ind (int): Index of process in the matrix
        outflow_processes_ids (list(str)): Ids of each process receiving a
            flow
        """
        self.process_id = process_id
        self.process_ind = process_ind
        self.outflow_processes_ids = outflow_processes_ids
        self.n_outflows = len(outflow_processes_ids)


class MathDistributionProcess(MathProcess):
    """
    Represents a distribution process in the mathematical model

    Parent Attributes
    ----------
    process_id (str): Id of process in math model
    process_ind (int): Index of process in the matrix
    outflow_processes_ids (list(str)): Ids of each process receiving a flow
    n_outflows (int): Number of outflows of the process
    """

    def __init__(
            self,
            process_id: str,
            process_ind: int,
            outflow_processes_ids: Set[str]):
        """
        Args
        ----
        process_id (str): Id of process in math model
        process_ind (int): Index of process in the matrix
        outflow_processes_ids (list(str)): Ids of each process receiving a
            flow
        """

        super().__init__(process_id, process_ind, outflow_processes_ids)

    def add_outflow(self, outflow_process_id: str):
        """
        Add an outflow to the process

        Args
        ----
        outflow_process_id (str):
        """
        if self.outflow_processes_ids.__contains__(outflow_process_id):
            raise ValueError(
                "Process {} already contains outflow to process {}"
                .format(self.process_id, outflow_process_id))

        self.outflow_processes_ids.add(outflow_process_id)
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

        assert (self.n_outflows == len(self.outflow_processes_ids) and
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
            return pm.Deterministic("P_{}".format(self.process_id), T.ones(1,))
        else:
            return pm.Dirichlet("P_{}".format(self.process_id), shares)

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
    process_id (str): Id of the process in math mod
    process_ind (int): Index of process in the matrix
    outflow_processes_ids (list(str)): Ids of each process receiving a flow
    n_outflows (int): Number of outflows of the process
    """

    def __init__(
            self,
            process_id: str,
            process_ind: int,
            outflow_processes_ids: Set[str]):
        """
        Args
        ----
        process_id (str): Process math id
        process_ind (int): Index of process in the matrix
        outflow_processes_ids (list(str)): Ids of each process receiving a
            flow
        """

        if len(outflow_processes_ids) > 2:
            raise ValueError(
                "A transformation process can have at most 2 outflows")

        super().__init__(process_id, process_ind, outflow_processes_ids)

    def add_outflow(self, outflow_process_id: str):
        """
        Add an outflow to the process

        Args
        ----
        outflow_process_id (str): Math id of receiving process
        """
        if self.outflow_processes_ids.__contains__(outflow_process_id):
            raise ValueError(
                "Process {} already contains outflow to process {}"
                .format(self.process_id, outflow_process_id))

        if self.n_outflows >= 2:
            raise ValueError(
                "A transformation process can have at most 2 outflows")

        self.outflow_processes_ids.add(outflow_process_id)
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

        assert (self.n_outflows == len(self.outflow_processes_ids) and
                self.n_outflows > 0)

        if self.n_outflows == 1:
            return pm.Deterministic("P_{}".format(self.process_id), T.ones(1,))

        if not transform_coeff:
            # If no tc supplied, model as a uniform distribution
            return pm.Uniform("P_{}".format(self.process_id), lower=0, upper=1)
        else:

            if ((transform_coeff.sd and not transform_coeff.mean) or
                    (transform_coeff.mean and not transform_coeff.sd)):
                raise ValueError(
                    "Must supply either both mean and standard deviation or " +
                    "no tranfer coefficient")

            return pm.Normal(
                "P_{}".format(self.process_id),
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
    process_id (str): Math id of the process
    process_ind (int): Index of process in the matrix
    outflow_processes_ids (list(str)): Math ids of each process receiving a flow
    n_outflows (int): Number of outflows of the process
    """

    def __init__(self, process_id: str, process_ind: int):
        """
        Args
        ----
        process_id (str): Math id of the process
        process_ind (int): Index of process in the matrix
        """
        # Does not provide any outflows as storage process in math model should
        # not have outflows
        super().__init__(process_id, process_ind, set())

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


class StafParameter():
    """
    Represents a stock or flow parameter in the math model

    Attributes
    ----------
    row_ind (int): Row index for the random variable in the matrix
    col_ind (int): Column index for the random variable in the matrix
    mean (float): Mean of the parameter value
    sd (float): sd of the parameter value
    """

    def __init__(
            self,
            row_ind: int,
            col_ind: int,
            mean: float,
            sd: float):

        """
        Attributes
        ----------
        row_ind (int): Row index for the random variable in the matrix
        col_ind (int): Column index for the random variable in the matrix
        mean (float): Mean of the parameter value
        sd (float): Standard deviation of the parameter value
        """

        self.row_ind = row_ind
        self.col_ind = col_ind
        self.mean = mean
        self.sd = sd

    def __hash__(self):
        ind_string = "{}_{}".format(self.row_ind, self.col_ind)
        return ind_string.__hash__()


class InputPrior():
    """
    Prior knowledge of flow of material into the mathematical model

    Attributes
    ----------
    destination_process_id (str): Math id of the receiving process
    uncertainty (Uncertainty): Quantity of flow and its uncertainty
    """

    def __init__(
            self,
            destination_process_id: str,
            uncertainty: Uncertainty):
        """
        Args
        ----------
        destination_process_id (str): Math id of the receiving process
        uncertainty (Uncertainty): Quantity of flow and its uncertainty
        """

        self.destination_process_id = destination_process_id
        self.uncertainty = uncertainty

    def create_param_rv(self):
        """
        Create random variable for this parameter
        """

        param_name = "IF_{}".format(self.destination_process_id)

        if isinstance(self.uncertainty, UniformUncertainty):
            return pm.Uniform(
                param_name,
                lower=self.uncertainty.lower,
                upper=self.uncertainty.upper)

        else:
            if isinstance(self.uncertainty, NormalUncertainty):
                return pm.Normal(
                    param_name,
                    mu=self.uncertainty.mean,
                    sd=self.uncertainty.standard_deviation)

            else:
                if isinstance(self.uncertainty, LognormalUncertainty):
                    return pm.Lognormal(
                        param_name,
                        mu=self.uncertainty.mean,
                        sd=self.uncertainty.standard_deviation)
                else:
                    raise ValueError(
                        "Uncertainty parameter is of unknown distribution")
                