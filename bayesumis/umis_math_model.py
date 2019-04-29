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

from bayesumis.umis_data_models import (
    Flow,
    LognormalUncertainty,
    NormalUncertainty,
    Material,
    ProcessOutflows,
    Staf,
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
    INPUT_VAR_NAME = 'Inputs'
    STAF_VAR_NAME = 'Stafs'
    TC_VAR_NAME = 'TCs'

    def __init__(
            self,
            external_inflows: Set[Flow],
            process_stafs_dict: Dict[UmisProcess, ProcessOutflows],
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

        process_stafs_dict (dict(str, set(Flow)): Dictionary mapping
            process_id to the process' outflows

        external_inflows (set(flow)): The inflows from outside the model to a
            process in the model

        external_outflows (set(flow)): The outflows from inside the model to a
            process outside the model

        transformation_coeff_obs (dict(str, TransformationCoefficient)): Maps a
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

        self.__create_math_processes(
            process_stafs_dict,
            external_outflows)

        self.__create_input_priors(external_inflows)

        staf_priors, normal_staf_obs, lognormal_staf_obs = \
            self.__create_staf_obs_and_priors(
                process_stafs_dict,
                external_outflows)

        normal_staf_obs_matrix, normal_staf_means, normal_staf_sds = \
            self.__create_staf_obs_matrices(normal_staf_obs)

        lognormal_staf_matrix, lognormal_staf_means, lognormal_staf_sds = \
            self.__create_staf_obs_matrices(lognormal_staf_obs)

        # Ricks Model
        with pm.Model() as self.pm_model:
            num_processes = len(self.__id_math_process_dict.keys())

            tc_matrix = self.__create_transfer_coefficient_matrix(
                transformation_coeff_obs,
                distribution_coeff_obs)

            tc_matrix = pm.Deterministic(self.TC_VAR_NAME, tc_matrix)

            input_matrix = self.__create_input_matrix()

            input_matrix = pm.Deterministic(self.INPUT_VAR_NAME, input_matrix)

            input_sums = T.sum(input_matrix, axis=1)

            process_throughputs = T.dot(
                matrix_inverse(T.eye(num_processes) - tc_matrix.T),
                input_sums[:, None])

            stafs = pm.Deterministic(
                self.STAF_VAR_NAME,
                tc_matrix * process_throughputs[:, None])

        # Toms Model1
        # with pm.Model() as self.pm_model:
        #     num_processes = len(self.__id_math_process_dict.keys())

        #     staf_matrix = self.__create_staf_priors_matrix(staf_priors)

        #     tc_matrix = self.__create_transfer_coefficient_matrix(
        #         transformation_coeff_obs,
        #         distribution_coeff_obs)

        #     tc_matrix = pm.Deterministic('TCs', tc_matrix)

        #     input_matrix = self.__create_input_matrix()

        #     input_matrix = pm.Deterministic('Inputs', input_matrix)

        #     input_sums = T.sum(input_matrix, axis=1)

        #     internal_inflow_sum_1 = T.sum(staf_matrix, axis=0)

        #     all_inflow_sum_1 = internal_inflow_sum_1[:, None] \
        #         + input_sums[:, None]

        #     staf_eqs_2 = pm.Deterministic(
        #         'staf_eqs_2', all_inflow_sum_1[:, None] * tc_matrix)

        # Toms Model2
        # with pm.Model() as self.pm_model:
        #     num_processes = len(self.__id_math_process_dict.keys())

        #     staf_matrix = self.__create_staf_priors_matrix(staf_priors)

        #     tc_matrix = self.__create_transfer_coefficient_matrix(
        #         transformation_coeff_obs,
        #         distribution_coeff_obs)

        #     tc_matrix = pm.Deterministic('TCs', tc_matrix)

        #     input_matrix = self.__create_input_matrix()

        #     input_matrix = pm.Deterministic('Inputs', input_matrix)

        #     input_sums = T.sum(input_matrix, axis=1)

        #     internal_inflow_sum_1 = T.sum(staf_matrix, axis=0)

        #     all_inflow_sum_1 = internal_inflow_sum_1[:, None] \
        #         + input_sums[:, None]

        #     staf_eqs_1 = all_inflow_sum_1[:, None] * tc_matrix

        #     all_but_one_outflow_sum = T.dot(
        #             staf_eqs_1,
        #             T.ones((num_processes, num_processes))
        #             - T.eye(num_processes))

        #     internal_inflow_sum_2 = T.sum(staf_eqs_1, axis=0)

        #     all_internal_inflow_2 = internal_inflow_sum_2[:, None] \
        #         + input_sums[:, None]

        #     staf_eqs_2 = pm.Deterministic(
        #         'staf_eqs_2',
        #         all_internal_inflow_2[:, None]
        #         - all_but_one_outflow_sum)

            if len(normal_staf_means > 0):
                normal_staf_obs_eqs = pm.Deterministic(
                    'normal_staf_obs_eqs',
                    T.tensordot(
                        normal_staf_obs_matrix, stafs))

                pm.Normal(
                    'normal_staf_observations',
                    mu=normal_staf_obs_eqs[:, None],
                    sd=normal_staf_sds[:, None],
                    observed=normal_staf_means[:, None])

            if len(lognormal_staf_means > 0):
                lognormal_staf_obs_eqs = pm.Deterministic(
                    'lognormal_staf_obs_eqs',
                    T.tensordot(
                        lognormal_staf_matrix, stafs))

                pm.Lognormal(
                    'lognormal_staf_observations',
                    mu=np.log(lognormal_staf_obs_eqs[:, None]),
                    sd=lognormal_staf_sds[:, None],
                    observed=lognormal_staf_means[:, None])

    def get_input_inds(self, staf: Staf):
        """ Gets the process index of the destination of the staf """
        dest_id = staf.destination_process.diagram_id
        dest_math_process = self.__id_math_process_dict.get(dest_id)

        if not dest_math_process:
            raise ValueError("Process with id: {} ".format(dest_id) +
                             "is not in this math model")

        dest_index = dest_math_process.process_ind

        input_priors_list = self.__input_priors.get_input_priors_list(dest_id)
        if not input_priors_list:
            raise ValueError("Process {} has no external stafs"
                             .format(dest_id))
        col_ind = -1
        for i, input_prior in enumerate(input_priors_list):
            if input_prior.origin_process_id == staf.origin_process.diagram_id:
                col_ind = i

        if col_ind == -1:
            raise ValueError("Inflow {} not in model".format(staf.stafdb_id))

        return dest_index, col_ind

    def get_process_ind(self, process_id: str):
        """ Gets the process index from process id """
        math_process = self.__id_math_process_dict.get(process_id)

        if not math_process:
            raise ValueError("Process with id: {} ".format(process_id) +
                             "is not in this math model")

        process_index = math_process.process_ind
        return process_index

    def get_staf_inds(self, staf: Staf):
        """ Gets the indices of a non input staf """
        origin_id = staf.origin_process.diagram_id
        origin_math_process = self.__id_math_process_dict.get(origin_id)

        if not origin_math_process:
            raise ValueError("Process with id: {} ".format(origin_id) +
                             "is not in this math model")

        origin_index = origin_math_process.process_ind

        dest_id = staf.destination_process.diagram_id
        dest_math_process = self.__id_math_process_dict.get(dest_id)

        if not dest_math_process:
            raise ValueError("Process with id: {} ".format(dest_id) +
                             "is not in this math model")

        dest_index = dest_math_process.process_ind
        return origin_index, dest_index

    def __add_staf_as_input_prior(
            self,
            origin_id: str,
            destination_id: str,
            uncertainty: Uncertainty):
        """
        Adds a new staf observation as an input prior

        Args
        ------------
        origin_id (str): Diagram id of the origin of the staf value
        destination_id (str): Diagram id of the destination of the staf value
        uncertainty (Uncertainty): Uncertainty of the value of the observation
        """
        if destination_id not in self.__id_math_process_dict:
            raise ValueError("This diagram does not contain" +
                             " destination process with id {}"
                             .format(destination_id))

        input_prior = StafPrior(
            origin_id, destination_id, uncertainty)

        self.__input_priors.add_external_input(
            destination_id, input_prior)

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
                self.__input_priors.inputs_dict.items():

            process_index = self.__id_math_process_dict[process_id].process_ind

            for i, inp in enumerate(inputs):
                input_rv = inp.create_staf_rv()
                input_matrix = T.set_subtensor(
                    input_matrix[process_index, i], input_rv)

        return input_matrix

    def __create_input_priors(self, external_inflows: Set[Flow]):
        """
        Add observations of inflows to the model as prior distributions

        Args
        ----
        external_inflows (set(Flow)): Flows to processes inside the model from
            outside the model

        """
        self.__input_priors = InputPriors()

        for flow in external_inflows:

            flow: Flow = flow
            if flow.staf_reference.time == self.reference_time:

                value = flow.get_value(self.reference_material)

                if value:

                    origin_id = flow.origin_process.diagram_id
                    destination_id = flow.destination_process.diagram_id

                    self.__add_staf_as_input_prior(
                        origin_id,
                        destination_id,
                        value.uncertainty)

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
            process_stafs_dict: Dict[str, ProcessOutflows],
            external_outflows: Set[Flow]):
        """
        Generates the math models of processes from stocks and flows

        Args
        ------------
        umis_processes (Set[UmisProcess]): Set of the UmisProcesses in the
            model

        process_stafs_dict (dict(str, set(Flow)): Dictionary mapping
            process_id to the process' outflows

        external_outflows (set(flow)): The outflows from inside the model to a
            process outside the model
        """

        self.__create_math_processes_from_internal_flows(process_stafs_dict)
        self.__create_math_processes_from_external_outflows(external_outflows)

    def __create_math_processes_from_internal_flows(
            self,
            process_stafs_dict: Dict[str, ProcessOutflows]):
        """
        Take the flows and creates internal_flows from them

        Args
        ------------
        process_stafs_dict (dict(str, set(Flow))): Maps a process to its
            outflows
        """

        for _, process_outflows in process_stafs_dict.items():

            for flow in process_outflows.flows:
                # Checks flow is about correct reference time
                if flow.staf_reference.time == self.reference_time:

                    value = flow.get_value(self.reference_material)
                    # Checks flow has an entry for the reference material
                    if(value is None):
                        print("Staf: {} has no value".format(flow.name))
                        # TODO do material reconciliation stuff
                        continue

                    else:

                        # TODO Unit reconciliation
                        # Would involve getting value and checking unit
                        self.__create_math_processes_from_staf(flow)

            if process_outflows.stock is not None:
                stock = process_outflows.stock

                if stock.staf_reference.time == self.reference_time:

                    value = stock.get_value(self.reference_material)

                    if (value is None):
                        print("Stock {} has no value for reference material"
                              .format(stock.name))

                    else:
                        if value.stock_type == 'Net':
                            self.__create_math_processes_from_staf(stock)

                        else:
                            # Doesn't support using data from total
                            # stock values
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
            if flow.staf_reference.time == self.reference_time:

                value = flow.get_value(self.reference_material)
                # Checks flow has an entry for the reference material
                if value:

                    # TODO Unit reconciliation

                    origin_id = flow.origin_process.diagram_id

                    destination_id = flow.destination_process.diagram_id

                    # If origin process has not been created yet then
                    # create it
                    if (not self.__id_math_process_dict
                                .__contains__(origin_id)):
                        self.__create_math_process(
                            origin_id,
                            flow.origin_process.process_type)

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

    def __create_math_processes_from_staf(self, staf: Staf):
        """
        Creates the math processes either side of the staf
        """

        # Stocks from the virtual reservoir are seen as inputs
        if staf.origin_process.process_type == 'Storage':
            return

        origin_id = staf.origin_process.diagram_id
        destination_id = staf.destination_process.diagram_id

        # If origin process has not been created yet then
        # create it
        if (not self.__id_math_process_dict
                    .__contains__(origin_id)):
            self.__create_math_process(
                origin_id,
                staf.origin_process.process_type)

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
                staf.destination_process.process_type)

    def __create_staf_obs_matrices(self, staf_obs):
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
        means_vector = np.zeros(num_obs)
        sds_vector = np.zeros(num_obs)

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

    def __create_staf_obs_and_priors(
            self,
            process_stafs_dict: Dict[str, Set[Staf]],
            external_outflows: Set[Flow]):
        """
        Store relevant observations of stock and flow values

        Args
        ----

        process_stafs_dict (dict(str, set(Staf)): Dictionary mapping
            process_id to the process' outflows

        external_outflows (set(flow)): The outflows from inside the model to a
            process outside the model

        Returns
        -------
        staf_priors, normal_staf_obs, lognormal_staf_obs
            (tuple(
                list(StafPrior), list(StafObservation), list(StafObservation)):
                    Updated lists of normally and lognormally distributed flow
                    observations
        """
        staf_priors = []
        normal_staf_obs = []
        lognormal_staf_obs = []

        staf_priors, normal_staf_obs, lognormal_staf_obs = \
            self.__create_staf_obs_and_priors_from_internal_stafs(
                process_stafs_dict,
                normal_staf_obs,
                lognormal_staf_obs,
                staf_priors)

        staf_priors, normal_staf_obs, lognormal_staf_obs = \
            self.__create_staf_obs_and_priors_from_external_outflows(
                external_outflows,
                normal_staf_obs,
                lognormal_staf_obs,
                staf_priors)

        return staf_priors, normal_staf_obs, lognormal_staf_obs

    def __create_staf_obs_and_priors_from_external_outflows(
            self,
            external_outflows: Set[Flow],
            normal_staf_obs: List['StafObservation'],
            lognormal_staf_obs: List['StafObservation'],
            staf_priors: List['StafPrior']):
        """
        Take the external outflows and creates flow observations from them

        Args
        ----
        process_stafs_dict (dict(str, set(Flow))): Maps a process to its
            outflows

        normal_staf_obs (List[StafObservation]): List of all normally
            distributed flow observations

        lognormal_staf_obs (List[StafObservation]): List of all lognormally
            distributed flow observations

        staf_priors (List[StafPrior]): List of all prior observations of staf
            values
        """

        for outflow in external_outflows:

            # Checks flow is about correct reference time
            if outflow.staf_reference.time == self.reference_time:

                value = outflow.get_value(self.reference_material)
                # Checks flow has an entry for the reference material
                if value:

                    # TODO Unit reconciliation
                    # Would involve getting value and checking unit
                    origin_id = outflow.origin_process.diagram_id
                    destination_id = outflow.destination_process.diagram_id
                    uncertainty = value.uncertainty

                    normal_staf_obs, lognormal_staf_obs = \
                        self.__add_staf_observation(
                            origin_id,
                            destination_id,
                            uncertainty,
                            normal_staf_obs,
                            lognormal_staf_obs)

                    staf_prior = StafPrior(
                            origin_id,
                            destination_id,
                            uncertainty)

                    staf_priors.append(staf_prior)

                else:
                    # TODO do material reconciliation stuff
                    continue

        return staf_priors, normal_staf_obs, lognormal_staf_obs

    def __create_staf_obs_and_priors_from_internal_stafs(
            self,
            process_stafs_dict: Dict[str, Set[Staf]],
            normal_staf_obs: List['StafObservation'],
            lognormal_staf_obs: List['StafObservation'],
            staf_priors: List['StafPrior']):
        """
        Take the internal flows and creates staf observations from them

        Args
        ----
        process_stafs_dict (dict(str, set(Staf))): Maps a process to its
            outflows

        normal_staf_obs (List[StafObservation]): List of all normally
            distributed flow observations

        lognormal_staf_obs (List[StafObservation]): List of all lognormally
            distributed flow observations

        staf_priors (List[StafPrior]): List of all prior observations of staf
            values
        """

        for origin_process, process_outflows in process_stafs_dict.items():

            for flow in process_outflows.flows:
                # Checks flow is about correct reference time
                if flow.staf_reference.time == self.reference_time:

                    value = flow.get_value(self.reference_material)
                    # Checks flow has an entry for the reference material
                    if value:

                        origin_id = origin_process.diagram_id
                        # TODO Unit reconciliation
                        # Would involve getting value and checking unit

                        destination_id = flow.destination_process.diagram_id

                        uncertainty = value.uncertainty

                        normal_staf_obs, lognormal_staf_obs = \
                            self.__add_staf_observation(
                                origin_id,
                                destination_id,
                                uncertainty,
                                normal_staf_obs,
                                lognormal_staf_obs)

                        staf_prior = StafPrior(
                            origin_id,
                            destination_id,
                            uncertainty)

                        staf_priors.append(staf_prior)

                    else:
                        # TODO do material reconciliation stuff
                        continue

            if process_outflows.stock is not None:
                stock = process_outflows.stock

                # Checks stock is about correct reference time
                if stock.staf_reference.time == self.reference_time:

                    value = stock.get_value(self.reference_material)
                    # Checks stock has an entry for the reference material and
                    # is a net stock value
                    if value and value.stock_type == 'Net':

                        origin_id = origin_process.diagram_id
                        # TODO Unit reconciliation
                        # Would involve getting value and checking unit

                        destination_id = stock.destination_process.diagram_id

                        uncertainty = value.uncertainty

                        if origin_process.process_type == 'Storage':
                            self.__add_staf_as_input_prior(
                                origin_id,
                                destination_id,
                                uncertainty)

                        else:
                            normal_staf_obs, lognormal_staf_obs = \
                                self.__add_staf_observation(
                                    origin_id,
                                    destination_id,
                                    uncertainty,
                                    normal_staf_obs,
                                    lognormal_staf_obs)

                            staf_prior = StafPrior(
                                origin_id,
                                destination_id,
                                uncertainty)

                            staf_priors.append(staf_prior)

        return staf_priors, normal_staf_obs, lognormal_staf_obs

    def __create_staf_priors_matrix(
            self,
            staf_priors: List['StafPrior']) -> T.Variable:
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

        staf_priors_matrix = T.zeros((num_of_processes, num_of_processes))

        np_s_p = np.zeros((num_of_processes, num_of_processes))

        for staf_prior in staf_priors:
            staf_prior: StafPrior = staf_prior
            staf_prior_rv = staf_prior.create_staf_rv()

            origin_id = staf_prior.origin_process_id
            origin_index = self.__id_math_process_dict[origin_id].process_ind

            dest_id = staf_prior.destination_process_id
            dest_index = self.__id_math_process_dict[dest_id].process_ind

            staf_priors_matrix = T.set_subtensor(
                staf_priors_matrix[[origin_index], [dest_index]],
                staf_prior_rv)

            np_s_p[[origin_index], [dest_index]] = staf_prior.uncertainty.mean

        return staf_priors_matrix

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


class TransformationCoefficient():
    """
    TC for a transformation process with storage, modelled as normally
    distributed. TC is the proportion going to storage

    Attributes
    ------------------
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
        -----------
        mean (float): Expected value of TC
        lower_uncertainty (float):  Lower uncertainty value of TC
        upper_uncertainty (float): Upper uncertainty value of TC
        """
        assert isinstance(mean, float)
        assert isinstance(lower_uncertainty, float)
        assert isinstance(upper_uncertainty, float)

        assert lower_uncertainty < upper_uncertainty

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

        assert (self.n_outflows == len(self.outflow_process_ids))

        if (self.n_outflows == 0):
            print("Process with id: {}, has no outflows"
                  .format(self.process_id))
            return [], 0

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

        assert (self.n_outflows == len(self.outflow_process_ids))

        if (self.n_outflows == 0):
            print("Process with id: {}, has no outflows"
                  .format(self.process_id))
            return [], 0

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

                if ((transform_coeff.sd and transform_coeff.mean is None) or
                        (transform_coeff.mean and transform_coeff.sd is None)):
                    raise ValueError(
                        "Must supply either both mean and standard deviation" +
                        " or no tranfer coefficient")

                storage_id, outflow_id = self.__separate_ids()

                normal_rv = pm.Normal(
                    "P_{}".format(
                        self.process_id),
                    mu=transform_coeff.mean,
                    sd=transform_coeff.sd)

                # Logistic efficiency
                coefficient_1 = T.exp(normal_rv) / (1 + T.exp(normal_rv))

                random_variable = T.stack([coefficient_1, 1-coefficient_1])
                process_ids = [storage_id, outflow_id]
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

    def __separate_ids(self):
        """
        Checks if the process id of the transfer coefficient is an outflow of
        this process and if so returns the process id of the other outflow

        Args
        --------------
        tc_process_id (str): Process id of transfer coefficient
        """
        (outflow_1, outflow_2) = self.outflow_process_ids

        if outflow_1.__contains__("STORAGE"):
            storage_id = outflow_1
            outflow_id = outflow_2
            return storage_id, outflow_id
        else:
            if outflow_2.__contains__("STORAGE"):
                storage_id = outflow_2
                outflow_id = outflow_1
                return storage_id, outflow_id
            else:
                raise ValueError("No outflow is a storage process")


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


class StafPrior():
    """
    Prior knowledge of stock or flow of material in the mathematical model

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

    def create_staf_rv(self):
        """
        Create random variable for this parameter
        """

        param_name = "Staf_{}-{}".format(
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
    inputs_dict (dict(str, list(stafPrior)): Maps the process id to
        its inputs from external processes
    """

    def __init__(self):

        self.inputs_dict: Dict[str, list(StafPrior)] = {}

    def add_external_input(self, process_id: str, input_prior: StafPrior):
        """
        Adds a prior input to the external inputs dict

        Args
        ------------
        process_id (str): Diagram id of process receiving the input
        input_prior (StafPrior):
        """
        assert isinstance(process_id, str)
        assert isinstance(input_prior, StafPrior)

        if self.inputs_dict.__contains__(process_id):
            self.inputs_dict[process_id].append(input_prior)
        else:
            self.inputs_dict[process_id] = [input_prior]

    def get_width_of_input_matrix(self):
        """
        Calculate the width of the input matrix as the largest number of inputs
        to any one process
        """
        max_width = 0

        for inputs in self.inputs_dict.values():
            if inputs.__len__() > max_width:
                max_width = inputs.__len__()

        return max_width

    def get_input_priors_list(self, destination_id: str):
        """
        Gets the input priors for a destination process
        """
        input_list = self.inputs_dict.get(destination_id)
        return input_list


if __name__ == '__main__':
    sys.exit(1)
