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
from theano.tensor.nlinalg import matrix_inverse

from ..bayesumis.umis_data_models import (
    Flow,
    LognormalUncertainty,
    NormalUncertainty,
    Material,
    Stock,
    Timeframe,
    UmisProcess,
    Uncertainty,
    UniformUncertainty)


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
            reference_material: Material,
            reference_time: Timeframe,
            transformation_coeff_obs: Dict[str, 'TransformationCoefficient']
            = {},
            distribution_coeff_obs: Dict[str, 'DistributionCoefficients']
            = {}):
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

        tranformation_coeff_obs (dict(str, TransformationCoefficient)): Maps a
            transformation process id to its transfer coefficient observation

        distribution_coeff_obs (dict(str, DistributionCoefficient)): Maps a
            distribution process id to its transfer coefficient observation

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

        self.__input_priors = InputPriors()

        self.__create_math_processes(
            umis_processes,
            process_outflows_dict,
            external_outflows)

        self.__create_input_priors(external_inflows)

        normal_staf_obs, lognormal_staf_obs = \
            self.__create_staf_observations(
                umis_processes,
                process_outflows_dict,
                external_outflows)

        normal_staf_matrix, normal_staf_means, normal_staf_sds = \
            self.__create_staf_matrices(normal_staf_obs)

        lognormal_staf_matrix, lognormal_staf_means, lognormal_staf_sds = \
            self.__create_staf_matrices(lognormal_staf_obs)

        with pm.Model() as self.pm_model:
            num_processes = len(self.__id_math_process_dict.keys())
            tc_matrix = self.__create_transfer_coefficient_matrix(
                transformation_coeff_obs,
                distribution_coeff_obs)

            tc_matrix = pm.Deterministic('TCs', tc_matrix)

            # input_matrix, ones_matrix = self.__create_input_matrix()

            input_matrix = pm.Deterministic('Inputs', input_matrix)

            input_sums = pm.Deterministic(
                'Input Sums', T.dot(input_matrix, ones_matrix))

            process_throughputs = pm.Deterministic(
                'X',
                T.dot(matrix_inverse(
                    T.eye(num_processes) - tc_matrix.T), input_sums))

            stafs = pm.Deterministic(
                'Stafs', tc_matrix * process_throughputs[:, None])

            if len(normal_staf_means > 0):
                normal_staf_obs_eqs = pm.Deterministic(
                    'Fobs_norm', T.tensordot(normal_staf_matrix, stafs))

                pm.Normal(
                    'normal_staf_observations',
                    mu=normal_staf_obs_eqs,
                    sd=normal_staf_sds,
                    observed=normal_staf_means)
            if len(lognormal_staf_means > 0):
                lognormal_staf_obs = T.tensordot(lognormal_staf_matrix, stafs)

                pm.Lognormal(
                    'lognormal_staf_observations',
                    mu=np.log(lognormal_staf_obs),
                    sd=lognormal_staf_sds,
                    observed=lognormal_staf_means)

    def get_inflow_inds(self, inflow: Flow):
        """ Gets the process index of the destination of the inflow """
        dest_id = inflow.destination.diagram_id
        dest_math_process = self.__id_math_process_dict.get(dest_id)

        if not dest_math_process:
            raise ValueError("Process with id: {} ".format(dest_id) +
                             "is not in this math model")

        dest_index = dest_math_process.process_ind

        input_priors_list = self.__input_priors.get_input_priors_list(dest_id)
        if not input_priors_list:
            raise ValueError("Process {} has no external inflows"
                             .format(dest_id))
        col_ind = -1
        for i, input_prior in enumerate(input_priors_list):
            input_prior: InputPrior = input_prior
            if input_prior.origin_process_id == inflow.origin.diagram_id:
                col_ind = i

        if col_ind == -1:
            raise ValueError("Inflow {} not in model".format(inflow.stafdb_id))

        return dest_index, col_ind

    def get_process_ind(self, process_id: str):
        """ Gets the process index from process id """
        math_process = self.__id_math_process_dict.get(process_id)

        if not math_process:
            raise ValueError("Process with id: {} ".format(process_id) +
                             "is not in this math model")

        process_index = math_process.process_ind
        return process_index

    def get_outflow_inds(self, outflow: Flow):
        """ Gets the indices of a given stock """
        origin_id = outflow.origin.diagram_id
        origin_math_process = self.__id_math_process_dict.get(origin_id)

        if not origin_math_process:
            raise ValueError("Process with id: {} ".format(origin_id) +
                             "is not in this math model")

        origin_index = origin_math_process.process_ind

        dest_id = outflow.destination.diagram_id
        dest_math_process = self.__id_math_process_dict.get(dest_id)

        if not dest_math_process:
            raise ValueError("Process with id: {} ".format(dest_id) +
                             "is not in this math model")

        dest_index = dest_math_process.process_ind
        return origin_index, dest_index

    def get_stock_inds(self, stock: Stock):
        """ Gets the indices of a given stock """
        origin_process_id = UmisProcess.create_diagram_id(
            stock.process_stafdb_id, stock.reference.origin_space)
        origin_math_process = self.__id_math_process_dict.get(
            origin_process_id)

        if not origin_math_process:
            raise ValueError("Stock is not in this math model")

        origin_index = origin_math_process.process_ind

        storage_id = self.__get_storage_process_id(origin_process_id)

        storage_process = self.__id_math_process_dict.get(storage_id)

        if not storage_process:
            raise ValueError("Stock is not in this math model")

        storage_index = storage_process.process_ind

        return origin_index, storage_index

    def __add_staf_observation(
            self,
            origin_id: str,
            destination_id: str,
            uncertainty: Uncertainty,
            normal_staf_obs: List['StafObservation'],
            lognormal_staf_obs: List['StafObservation']):
        """
        Creates and stores a staf observation of a stock or flow

        Args
        ---------
        origin_id (str): Math Id of origin process of stock or flow
        destination_id (str): Math Id of destination process of stock or flow
        uncertainty (Uncertainty): Uncertainty around observed staf value

        normal_staf_obs (List[StafObservation]): List of all normally
            distributed flow observations

        lognormal_staf_obs (List[StafObservation]): List of all lognormally
            distributed flow observations

        Returns
        -------
        normal_staf_obs, lognormal_staf_obs
            (tuple(list(StafObservations), list(StafObservations)): Updated
            lists of normally and lognormally distributed staf observations
        """
        if isinstance(uncertainty, UniformUncertainty):
            return normal_staf_obs, lognormal_staf_obs
        else:

            staf_ob = StafObservation(
                    origin_id,
                    destination_id,
                    uncertainty.mean,
                    uncertainty.standard_deviation)

            if isinstance(uncertainty, LognormalUncertainty):
                lognormal_staf_obs.append(staf_ob)
            else:
                if isinstance(uncertainty, NormalUncertainty):

                    normal_staf_obs.append(staf_ob)
                else:
                    raise ValueError(
                        "Unsupported uncertainty type")

            return normal_staf_obs, lognormal_staf_obs

    def __create_input_matrix(self):
        """
        Builds input matrix from input priors """
        num_processes = self.__id_math_process_dict.keys().__len__()
        input_matrix_width = self.__input_priors.get_width_of_input_matrix()

        input_matrix = T.zeros((num_processes, input_matrix_width))

        for process_id, inputs in \
                self.__input_priors.external_inputs_dict.items():

            process_index = self.__id_math_process_dict[process_id].process_ind

            for i, inp in enumerate(inputs):
                input_rv = inp.create_input_rv()
                input_matrix = T.set_subtensor(
                    input_matrix[process_index, i], input_rv)

        # matrix of ones to sum inputs for an internal process
        ones_matrix = T.ones((input_matrix_width, 1))

        return input_matrix, ones_matrix

    def __create_input_priors(self, external_inflows: Set[Flow]):
        """
        Add observations of inflows to the model as prior distributions

        Args
        ----
        external_inflows (set(Flow)): Flows to processes inside the model from
            outside the model

        """

        for flow in external_inflows:

            flow: Flow = flow
            if flow.reference.time == self.reference_time:

                value = flow.get_value(self.reference_material)

                if value:

                    # TODO unit reconciliation
                    origin_id = flow.origin.diagram_id

                    destination_id = flow.destination.diagram_id

                    if destination_id not in self.__id_math_process_dict:
                        raise ValueError("This diagram does not contain" +
                                         " destination process with id {}"
                                         .format(destination_id))

                    input_prior = InputPrior(
                        origin_id, destination_id, value.uncertainty)

                    self.__input_priors.add_external_input(
                        destination_id, input_prior)

                else:
                    # TODO material reconciliation
                    continue

    def __create_math_process(
            self,
            process_id: str,
            process_type: str):
        """
        Create a mathematical process and increments index counter

        Args
        ------------
        process_id: (str): Unique identifier of math process
        process_type (str):
        outflow_ids (set(Flow)): Ids of output processes
        """
        if process_type == 'Transformation':
            math_process = MathTransformationProcess(
                process_id,
                self.__index_counter)
        else:
            if process_type == 'Distribution':
                math_process = MathDistributionProcess(
                    process_id,
                    self.__index_counter)
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
            external_outflows: Set[Flow]):
        """
        Generates the math models of processes from stocks and flows

        Args
        ------------
        umis_processes (Set[UmisProcess]): Set of the UmisProcesses in the
            model

        process_outflows_dict (dict(str, set(Flow)): Dictionary mapping
            process_id to the process' outflows

        external_outflows (set(flow)): The outflows from inside the model to a
            process outside the model
        """

        self.__create_math_processes_from_internal_flows(process_outflows_dict)
        self.__create_math_processes_from_external_outflows(external_outflows)
        self.__create_math_processes_from_stocks(umis_processes)

    def __create_math_processes_from_internal_flows(
            self,
            process_outflows_dict: Dict[str, Set[Flow]]):
        """
        Take the flows and creates internal_flows from them

        Args
        ------------
        process_outflows_dict (dict(str, set(Flow))): Maps a process to its
            outflows
        """

        for origin_id, outflows in process_outflows_dict.items():

            for flow in outflows:
                # Checks flow is about correct reference time
                if flow.reference.time == self.reference_time:

                    value = flow.get_value(self.reference_material)
                    # Checks flow has an entry for the reference material
                    if value:

                        # TODO Unit reconciliation
                        # Would involve getting value and checking unit
                        destination_id = flow.destination.diagram_id

                        # If origin process has not been created yet then
                        # create it
                        if (not self.__id_math_process_dict
                                    .__contains__(origin_id)):
                            self.__create_math_process(
                                origin_id,
                                flow.origin.process_type)

                            self.__id_math_process_dict[origin_id] \
                                .add_outflow(destination_id)
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
        ------------
        external_outflows (set(Flow)): Flows from the diagram out
        """
        for flow in outflows:
            # Checks flow is about correct reference time
            if flow.reference.time == self.reference_time:

                value = flow.get_value(self.reference_material)
                # Checks flow has an entry for the reference material
                if value:

                    # TODO Unit reconciliation

                    origin_id = flow.origin.diagram_id

                    destination_id = flow.destination.diagram_id

                    # If origin process has not been created yet then
                    # create it
                    if (not self.__id_math_process_dict
                                .__contains__(origin_id)):
                        self.__create_math_process(
                            origin_id,
                            flow.origin.process_type)

                        self.__id_math_process_dict[origin_id] \
                            .add_outflow(destination_id)
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
        ------------
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

                        # Model as a flow to a storage process
                        origin_id = process.diagram_id

                        dest_id = self.__get_storage_process_id(
                            process.diagram_id)

                        # If origin process has not been created yet then
                        # create it
                        if (not self.__id_math_process_dict
                                    .__contains__(origin_id)):
                            self.__create_math_process(
                                origin_id,
                                process.process_type)

                            self.__id_math_process_dict[origin_id] \
                                .add_outflow(dest_id)
                        # Otherwise add the outflow to the existing process
                        else:
                            self.__id_math_process_dict[origin_id] \
                                .add_outflow(dest_id)

                        # If destination process has not been created yet
                        # then create it as a storage process
                        if (not self.__id_math_process_dict
                                    .__contains__(dest_id)):
                            self.__create_math_process(
                                dest_id,
                                'Storage')

                    else:
                        # TODO more material reconciliation stuff
                        continue

    def __create_staf_matrices(self, staf_obs):
        """
        Create observation matrix to select out the flow equations we have
            observations for

        Args
        ---------------
        staf_obs (List[StafObservations]): Observed stock and flow values

        Returns
        ---------------
        observed_staf_matrix (np.array):
            num_obs x num_processes x num_processes matrix with 1s for each
            staf observation

        means_vector (np.array): The observed means of the flow values
        sds_vector (np.array): The observed standard deviations of the flow
            values
        """
        num_obs = staf_obs.__len__()
        num_procs = self.__id_math_process_dict.keys().__len__()

        observed_staf_matrix = np.zeros((num_obs, num_procs, num_procs))
        means_vector = np.zeros((num_obs, 1))
        sds_vector = np.zeros((num_obs, 1))

        for i, observation in enumerate(staf_obs):
            origin_id = observation.origin_id
            origin_index = self.__id_math_process_dict[origin_id].process_ind

            destination_id = observation.destination_id
            destination_index = \
                self.__id_math_process_dict[destination_id].process_ind

            observed_staf_matrix[i][origin_index][destination_index] = 1

            means_vector[i] = observation.mean
            sds_vector[i] = observation.sd

        return observed_staf_matrix, means_vector, sds_vector

    def __create_staf_observations(
            self,
            umis_processes: Set[UmisProcess],
            process_outflows_dict: Dict[str, Set[Flow]],
            external_outflows: Set[Flow]):
        """
        Store relevant observations of stock and flow values

        Args
        ----
        umis_processes (Set[UmisProcess]): Set of the UmisProcesses in the
            model

        process_outflows_dict (dict(str, set(Flow)): Dictionary mapping
            process_id to the process' outflows

        external_outflows (set(flow)): The outflows from inside the model to a
            process outside the model

        Returns
        -------
        normal_staf_obs, lognormal_staf_obs
            (tuple(list(StafObservation), list(StafObservation)): Updated
            lists of normally and lognormally distributed flow observations
        """

        normal_staf_obs = []
        lognormal_staf_obs = []

        normal_staf_obs, lognormal_staf_obs = \
            self.__create_staf_obs_from_internal_flows(
                process_outflows_dict, normal_staf_obs, lognormal_staf_obs)

        normal_staf_obs, lognormal_staf_obs = \
            self.__create_staf_obs_from_external_outflows(
                external_outflows, normal_staf_obs, lognormal_staf_obs)

        normal_staf_obs, lognormal_staf_obs = \
            self.__create_staf_obs_from_stocks(
                umis_processes, normal_staf_obs, lognormal_staf_obs)

        return normal_staf_obs, lognormal_staf_obs

    def __create_staf_obs_from_external_outflows(
            self,
            external_outflows: Set[Flow],
            normal_staf_obs: List['StafObservation'],
            lognormal_staf_obs: List['StafObservation']):
        """
        Take the external outflows and creates flow observations from them

        Args
        ----
        process_outflows_dict (dict(str, set(Flow))): Maps a process to its
            outflows

        normal_staf_obs (List[StafObservation]): List of all normally
            distributed flow observations

        lognormal_staf_obs (List[StafObservation]): List of all lognormally
            distributed flow observations
        """

        for outflow in external_outflows:

            # Checks flow is about correct reference time
            if outflow.reference.time == self.reference_time:

                value = outflow.get_value(self.reference_material)
                # Checks flow has an entry for the reference material
                if value:

                    # TODO Unit reconciliation
                    # Would involve getting value and checking unit
                    origin_id = outflow.origin.diagram_id
                    destination_id = outflow.destination.diagram_id
                    uncertainty = value.uncertainty

                    normal_staf_obs, lognormal_staf_obs = \
                        self.__add_staf_observation(
                            origin_id,
                            destination_id,
                            uncertainty,
                            normal_staf_obs,
                            lognormal_staf_obs)
                else:
                    # TODO do material reconciliation stuff
                    continue

        return normal_staf_obs, lognormal_staf_obs

    def __create_staf_obs_from_internal_flows(
            self,
            process_outflows_dict: Dict[str, Set[Flow]],
            normal_staf_obs: List['StafObservation'],
            lognormal_staf_obs: List['StafObservation']):
        """
        Take the internal flows and creates staf observations from them

        Args
        ----
        process_outflows_dict (dict(str, set(Flow))): Maps a process to its
            outflows

        normal_staf_obs (List[StafObservation]): List of all normally
            distributed flow observations

        lognormal_staf_obs (List[StafObservation]): List of all lognormally
            distributed flow observations
        """

        for origin_id, outflows in process_outflows_dict.items():

            for flow in outflows:
                # Checks flow is about correct reference time
                if flow.reference.time == self.reference_time:

                    value = flow.get_value(self.reference_material)
                    # Checks flow has an entry for the reference material
                    if value:

                        # TODO Unit reconciliation
                        # Would involve getting value and checking unit
                        destination_id = flow.destination.diagram_id

                        uncertainty = value.uncertainty

                        normal_staf_obs, lognormal_staf_obs = \
                            self.__add_staf_observation(
                                origin_id,
                                destination_id,
                                uncertainty,
                                normal_staf_obs,
                                lognormal_staf_obs)

                    else:
                        # TODO do material reconciliation stuff
                        continue

        return normal_staf_obs, lognormal_staf_obs

    def __create_staf_obs_from_stocks(
            self,
            umis_processes: Set[UmisProcess],
            normal_staf_obs: List['StafObservation'],
            lognormal_staf_obs: List['StafObservation']):
        """
        Take the stocks assigned to processes and create staf observations
        from them

        Args
        ------------
        umis_processes (list(UmisProcess)): Stocked and unstocked umis
            processes

        normal_staf_obs (List[StafObservation]): List of all normally
            distributed flow observations

        lognormal_staf_obs (List[StafObservation]): List of all lognormally
            distributed flow observations
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

                        # Model as a flow to a storage process
                        origin_id = process.diagram_id

                        dest_id = self.__get_storage_process_id(
                            process.diagram_id)

                        uncertainty = value.uncertainty

                        normal_staf_obs, lognormal_staf_obs = \
                            self.__add_staf_observation(
                                origin_id,
                                dest_id,
                                uncertainty,
                                normal_staf_obs,
                                lognormal_staf_obs)

                    else:
                        # TODO more material reconciliation stuff
                        continue

        return normal_staf_obs, lognormal_staf_obs

    def __create_transfer_coefficient_matrix(
            self,
            transformation_coeffs_obs: Dict[str, 'TransformationCoefficient'],
            distribution_coeffs_obs: Dict[str, 'DistributionCoefficients']) \
            -> T.Variable:
        """
        Builds matrix with transfer coeffs represented as random variables

        Args
        ------------
        transformation_coeffs_obs (dict(str, TransformationCoefficient)):
            Maps transformation process ids to an observation of its
            transfer coefficient

        distribution_coeffs_obs (dict(str, DistributionCoefficients)):
            Maps distribution process ids to an observation of its transfer
            coefficients
        """
        num_of_processes = self.__id_math_process_dict.keys().__len__()

        tc_matrix = T.zeros((num_of_processes, num_of_processes))

        for process_id, math_process in self.__id_math_process_dict.items():
            tc_observation = None
            if isinstance(math_process, MathTransformationProcess):
                tc_observation = transformation_coeffs_obs.get(process_id)

            if isinstance(math_process, MathDistributionProcess):
                tc_observation = distribution_coeffs_obs.get(process_id)

            if tc_observation:
                dest_process_ids, dest_rv = \
                    math_process.create_outflow_tc_rvs(tc_observation)
            else:
                dest_process_ids, dest_rv = \
                    math_process.create_outflow_tc_rvs()

            origin_ind = math_process.process_ind

            dest_inds = [self.__id_math_process_dict[pid].process_ind
                         for pid in dest_process_ids]

            tc_matrix = T.set_subtensor(
                tc_matrix[[origin_ind], dest_inds], dest_rv)

        return tc_matrix

    def __get_process_ind(self, process_id: str) -> int:
        """ Returns the index of the process in the matrix if id exists """

        ind = self.__id_math_process_dict[process_id]
        if not ind:
            raise ValueError("Process id {} does not exist"
                             .format(process_id))

        return ind

    def __get_storage_process_id(
            self,
            process_diagram_id: str) -> str:
        """
        Makes a math id for storage to a process

        Args
        ------------
        process_stafdb_id (str): Id of process in umis diagram
        """
        storage_process_id = "{}_STORAGE".format(process_diagram_id)

        return storage_process_id


class TransformationCoefficient():
    """
    TC for a transformation process with storage, modelled as normally
    distributed.

    Attributes
    ------------------
    process_id (str): Id of the process the TC is for
    mean (np.float): Expected value of TC
    sd (np.float): Standard deviation of TC
    """

    def __init__(
            self,
            process_id: str,
            mean: float,
            lower_uncertainty: float,
            upper_uncertainty: float):
        """
        Log shifts the mean and standard deviation values to ensure they don't
        pass 0 or 1

        Args
        -----------
        process_id (str): Id of the process the TC is for
        mean (float): Expected value of TC
        lower_uncertainty (float):  Lower uncertainty value of TC
        upper_uncertainty (float): Upper uncertainty value of TC
        """
        assert isinstance(process_id, str)
        assert isinstance(mean, float)
        assert isinstance(lower_uncertainty, float)
        assert isinstance(upper_uncertainty, float)

        self.process_id = process_id

        def logit(x):
            return -np.log(1/x - 1)

        def logit_range_sd(a, b):
            return (logit(b) - logit(a)) / 4

        self.mean = logit(mean)
        self.sd = logit_range_sd(lower_uncertainty, upper_uncertainty)


class DistributionCoefficient():
    """
    Outflow and its transfer coefficient

    Attributes
    ----------
    outflow_id (str): Id of receiving process for this transfer coefficient
    transfer_coefficient (float): Value of the transfer coefficient
    """

    def __init__(self, outflow_id: str, transfer_coefficient: float):
        """
        Args
        -----------
        outflow_id (str): Id of receiving process for this transfer coefficient
        transfer_coefficient (float):
        """
        assert isinstance(outflow_id, str)
        assert isinstance(transfer_coefficient, float)
        assert (transfer_coefficient >= 0 and transfer_coefficient <= 1)

        self.outflow_id = outflow_id
        self.transfer_coefficient = transfer_coefficient


class DistributionCoefficients():
    """
    TC(s) for a distribution process modelled as a dirichlet
    distribution

    Attributes
    -----------------
    outflow_coefficients (List[DistributionCoefficient]):
        Expected values of TCs
    """

    def __init__(self, outflow_coefficients: List[DistributionCoefficient]):
        """
        Args
        -----------------
        outflow_coefficients (List[DistributionCoefficient]):
            Expected values of TCs
        """

        self.shares = [oc.transfer_coefficient for oc in outflow_coefficients]
        self.outflow_processes = [oc.outflow_id
                                  for oc in outflow_coefficients]


class MathProcess():
    """
    Parent class for calculating mathematical models of processes

    Attributes
    ------------------------
    process_id (str): Id for the process in the math model
    process_ind (int): Index of process in the matrix
    outflow_process_ids (list(str)): Math ids of each process receiving a
        flow
    n_outflows (int): Number of outflows of the process
    """

    def __init__(
            self,
            process_id: str,
            process_ind: int):
        """
        Args
        -----------
        process_id (str): Id for the process in the math model
        process_ind (int): Index of process in the matrix
        outflow_process_ids (list(str)): Ids of each process receiving a
            flow
        """
        assert isinstance(process_id, str)
        assert isinstance(process_ind, int)

        self.process_id = process_id
        self.process_ind = process_ind
        self.outflow_process_ids = set()
        self.n_outflows = 0


class MathDistributionProcess(MathProcess):
    """
    Represents a distribution process in the mathematical model

    Parent Attributes
    ------------------------
    process_id (str): Id of process in math model
    process_ind (int): Index of process in the matrix
    outflow_process_ids (list(str)): Ids of each process receiving a flow
    n_outflows (int): Number of outflows of the process
    """

    def __init__(
            self,
            process_id: str,
            process_ind: int):
        """
        Args
        -----------
        process_id (str): Id of process in math model
        process_ind (int): Index of process in the matrix
        """

        super(MathDistributionProcess, self).__init__(process_id, process_ind)

    def add_outflow(self, outflow_process_id: str):
        """
        Add an outflow to the process

        Args
        -----------
        outflow_process_id (str):
        """
        assert isinstance(outflow_process_id, str)

        if self.outflow_process_ids.__contains__(outflow_process_id):
            raise ValueError(
                "Process {} already contains outflow to process {}"
                .format(self.process_id, outflow_process_id))

        self.outflow_process_ids.add(outflow_process_id)
        self.n_outflows += 1

    def create_outflow_tc_rvs(
            self,
            dist_coeffs: DistributionCoefficients = None) \
            -> Tuple[List[str], pm.Continuous]:
        """
        Create RVs for transfer coefficients for the process

        Args
        -----------
        dist_coeffs (DistributionCoefficients): known transfer coefficients
        """

        assert (self.n_outflows == len(self.outflow_process_ids) and
                self.n_outflows > 0)

        if not dist_coeffs:
            # If no coefficients supplied, model as a uniform dirichlet
            # distribution
            shares = np.ones(self.n_outflows, dtype=np.dtype(float))
            outflow_process_ids = self.outflow_process_ids
        else:
            shares = np.array(dist_coeffs.shares)
            outflow_process_ids = dist_coeffs.outflow_processes

        if(len(shares) != self.n_outflows):
            raise ValueError(
                "Must supply a transfer_coefficient for each outflow or None")

        if self.n_outflows == 1:
            (outflow_process_id, ) = self.outflow_process_ids
            random_variable = pm.Deterministic(
                "P_{}".format(self.process_id), T.ones(1,))

        else:
            random_variable = pm.Dirichlet(
                "P_{}".format(self.process_id), shares)

        return outflow_process_ids, random_variable

    @staticmethod
    def transfer_functions(transfer_coeff_rv: pm.Continuous):
        """
        Logistic function applied to first transfer coefficient to ensure it
        doesn't exceed 1 or fall below 0

        Args
        -----------
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
    outflow_process_ids (list(str)): Ids of each process receiving a flow
    n_outflows (int): Number of outflows of the process
    """

    def __init__(
            self,
            process_id: str,
            process_ind: int):
        """
        Args
        ----
        process_id (str): Process math id
        process_ind (int): Index of process in the matrix
        """
        super(
            MathTransformationProcess, self).__init__(process_id, process_ind)

    def add_outflow(self, outflow_process_id: str):
        """
        Add an outflow to the process

        Args
        -----------
        outflow_process_id (str): Math id of receiving process
        """
        if self.outflow_process_ids.__contains__(outflow_process_id):
            raise ValueError(
                "Process {} already contains outflow to process {}"
                .format(self.process_id, outflow_process_id))

        if self.n_outflows >= 2:
            raise ValueError(
                "A transformation process can have at most 2 outflows")

        self.outflow_process_ids.add(outflow_process_id)
        self.n_outflows += 1

    def create_outflow_tc_rvs(
            self,
            transform_coeff: TransformationCoefficient = None) \
            -> Tuple[List[str], pm.Continuous]:
        """
        Create RV for the transfer coefficient for the process

        Args
        -----------
        transform_coeff (TransformationCoefficient): Known mean and standard
        deviation for transfer coefficient to storage process
        """

        assert (self.n_outflows == len(self.outflow_process_ids) and
                self.n_outflows > 0)

        if self.n_outflows == 1:
            random_variable = pm.Deterministic(
                "P_{}".format(
                    self.process_id),
                T.ones(1,))

            return self.outflow_process_ids, random_variable

        if self.n_outflows == 2:
            if not transform_coeff:
                # If no tc supplied, model as a uniform distribution
                coefficient_1 = pm.Uniform(
                    "P_{}".format(
                        self.process_id),
                    lower=0,
                    upper=1)

                random_variable = T.stack([coefficient_1, 1-coefficient_1])
                return self.outflow_process_ids, random_variable

            else:

                if ((transform_coeff.sd and not transform_coeff.mean) or
                        (transform_coeff.mean and not transform_coeff.sd)):
                    raise ValueError(
                        "Must supply either both mean and standard deviation" +
                        " or no tranfer coefficient")

                other_process_id = self.__get_other_process_id(
                    transform_coeff.process_id)

                normal_rv = pm.Normal(
                    "P_{}".format(
                        self.process_id),
                    mu=transform_coeff.mean,
                    sd=transform_coeff.sd)

                # Logistic efficiency
                coefficient_1 = T.exp(normal_rv) / (1 + T.exp(normal_rv))

                random_variable = T.stack([coefficient_1, 1-coefficient_1])
                process_ids = [transform_coeff.process_id, other_process_id]
                return process_ids, random_variable

        else:
            raise ValueError("Transformation process should not have more" +
                             " than 2 outflows")

    @staticmethod
    def transfer_functions(transfer_coeff_rv):
        """
        Function applied to transfer coefficients to convert into correct
        theano values

        Args
        -----------
        tranfer_coeff_rv (pm.Continuous): RV representing transfer coefficients
        """
        return transfer_coeff_rv

    def __get_other_process_id(self, tc_process_id: str):
        """
        Checks if the process id of the transfer coefficient is an outflow of
        this process and if so returns the process id of the other outflow

        Args
        --------------
        tc_process_id (str): Process id of transfer coefficient
        """

        if not self.outflow_process_ids.__contains__(tc_process_id):
            raise ValueError("Process {} does not ".format(self.process_id) +
                             "contain outflow for given transfer coefficient")

        for outflow_id in self.outflow_process_ids:
            if outflow_id != tc_process_id:
                return outflow_id
        raise ValueError("All outflows had process id of transfer coefficient")


class MathStorageProcess(MathProcess):
    """
    Represents a storage process in the mathematical model

    Parent Attributes
    ----------
    process_id (str): Math id of the process
    process_ind (int): Index of process in the matrix
    outflow_process_ids (list(str)): Math ids of each process receiving a
        flow
    n_outflows (int): Number of outflows of the process
    """

    def __init__(self, process_id: str, process_ind: int):
        """
        Args
        -----------
        process_id (str): Math id of the process
        process_ind (int): Index of process in the matrix
        """
        # Does not provide any outflows as storage process in math model should
        # not have outflows
        super(MathStorageProcess, self).__init__(process_id, process_ind)

    def create_outflow_tc_rvs(self):
        """
        No random variable associated with process as there are no outflows
        """
        return [], 0

    @staticmethod
    def transfer_functions(tranfer_coeff_rv):
        """
        Function applied to transfer coefficients to convert into correct
        theano values

        Args
        -----------
        tranfer_coeff_rv (pm.Continuous): RV representing transfer coefficients
        """
        return T.dvector()


class StafObservation():
    """
    Represents a normally distributed stock or flow observation in the math
    model

    Attributes
    -----------------
    origin_id (str): Origin process id
    destination_id (str): Destination process id
    mean (float): Mean of the parameter value
    sd (float): sd of the parameter value
    """

    def __init__(
            self,
            origin_id: str,
            destination_id: str,
            mean: float,
            sd: float):

        """
        Attributes
        -----------------
        origin_id (str): Origin process id
        destination_id (str): Destination process id
        mean (float): Mean of the parameter value
        sd (float): Standard deviation of the parameter value
        """
        assert isinstance(origin_id, str)
        assert isinstance(destination_id, str)
        assert isinstance(mean, float)
        assert isinstance(sd, float)

        self.origin_id = origin_id
        self.destination_id = destination_id
        self.mean = mean
        self.sd = sd


class InputPrior():
    """
    Prior knowledge of flow of material into the mathematical model from
    external process or from stock (virtual reservoir)

    Attributes
    ----------
    origin_process_id (str): Math id of the origin process
    destination_process_id (str): Math id of the receiving process
    uncertainty (Uncertainty): Quantity of flow and its uncertainty
    """

    def __init__(
            self,
            origin_process_id: str,
            destination_process_id: str,
            uncertainty: Uncertainty):
        """
        Args
        ----------
        origin_process_id (str): Math id of the origin process
        destination_process_id (str): Math id of the receiving process
        uncertainty (Uncertainty): Quantity of flow and its uncertainty
        """
        assert isinstance(origin_process_id, str)
        assert isinstance(destination_process_id, str)
        assert isinstance(uncertainty, Uncertainty)

        self.origin_process_id = origin_process_id
        self.destination_process_id = destination_process_id
        self.uncertainty = uncertainty

    def create_input_rv(self):
        """
        Create random variable for this parameter
        """

        param_name = "IF_{}-{}".format(
            self.origin_process_id, self.destination_process_id)

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


class InputPriors():
    """
    Stores the inputs from external processes into the model.

    Attributes
    ---------------
    external_inputs_dict (dict(str, list(InputPrior)): Maps the process id to
        its inputs from external processes
    """

    def __init__(self):

        self.external_inputs_dict: Dict[str, list(InputPrior)] = {}

    def add_external_input(self, process_id: str, input_prior: InputPrior):
        """
        Adds a prior input to the external inputs dict

        Args
        ------------
        process_id (str): Diagram id of process receiving the input
        input_prior (InputPrior):
        """
        assert isinstance(process_id, str)
        assert isinstance(input_prior, InputPrior)

        if self.external_inputs_dict.__contains__(process_id):
            self.external_inputs_dict[process_id].append(input_prior)
        else:
            self.external_inputs_dict[process_id] = [input_prior]

    def get_width_of_input_matrix(self):
        """
        Calculate the width of the input matrix as the largest number of inputs
        to any one process
        """
        max_width = 0

        for inputs in self.external_inputs_dict.values():
            if inputs.__len__() > max_width:
                max_width = inputs.__len__()

        return max_width

    def get_input_priors_list(self, destination_id: str):
        """
        Gets the input priors for a destination process
        """
        input_list = self.external_inputs_dict.get(destination_id)
        return input_list


if __name__ == '__main__':
    sys.exit(1)
