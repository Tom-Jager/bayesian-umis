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
    Constant,
    Flow,
    LognormalUncertainty,
    NormalUncertainty,
    Material,
    ProcessOutputs,
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
    INPUT_CC_VAR_NAME = 'Input CCs'
    STAF_VAR_NAME = 'Stafs'
    TC_VAR_NAME = 'TCs'

    def __init__(
            self,
            external_inflows: Set[Flow],
            process_stafs_dict: Dict[UmisProcess, ProcessOutputs],
            external_outflows: Set[Flow],
            reference_material: Material,
            reference_time: Timeframe,
            material_reconc_table: Dict[Material, Uncertainty] = {},
            tc_observation_table: Dict[str, Dict[str, Uncertainty]] = {}):
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

        reference_material (Material): The material being balanced

        reference_time (Timeframe): The timeframe over which the stocks and
            flows are modeled
        """

        self.reference_material = reference_material
        self.reference_time = reference_time

        self.__material_reconc_table = material_reconc_table
        self.__tc_observation_table = tc_observation_table
        # Assigns a new index to each process
        self.__index_counter = 0

        self.__id_math_process_dict: Dict[str, MathProcess] = {}
        self.__input_priors = InputPriors()
        self.__staf_observations = StafObservations()
        """ Maps a math process id to its math process """

        self.__create_math_processes(
            process_stafs_dict,
            external_outflows)

        self.__create_input_priors(external_inflows)

        self.__create_staf_observations(
            process_stafs_dict,
            external_outflows)

        # Ricks Model
        with pm.Model() as self.pm_model:
            num_processes = len(self.__id_math_process_dict.keys())

            tc_matrix = self.__create_transfer_coefficient_matrix()
            tc_matrix = pm.Deterministic(self.TC_VAR_NAME, tc_matrix)

            input_matrix, input_cc_matrix = \
                self.__create_input_and_cc_matrices()

            input_matrix = pm.Deterministic(self.INPUT_VAR_NAME, input_matrix)
            input_cc_matrix = pm.Deterministic(
                self.INPUT_CC_VAR_NAME, input_cc_matrix)

            reconciled_input_matrix = \
                input_matrix * input_cc_matrix

            input_sums = T.sum(reconciled_input_matrix, axis=1)

            process_throughputs = T.dot(
                matrix_inverse(T.eye(num_processes) - tc_matrix.T),
                input_sums[:, None])

            stafs = pm.Deterministic(
                self.STAF_VAR_NAME,
                tc_matrix * process_throughputs[:, None])

            (normal_staf_obs_matrix,
             normal_staf_means,
             normal_staf_sds,
             normal_ccs) = \
                self.__create_staf_obs_matrices_normal(
                    self.__staf_observations.normal_staf_obs)

            (lognormal_staf_obs_matrix,
             lognormal_staf_means,
             lognormal_staf_sds,
             lognormal_ccs) = \
                self.__create_staf_obs_matrices_normal(
                    self.__staf_observations.lognormal_staf_obs)

            (uniform_staf_obs_matrix,
             uniform_staf_lower,
             uniform_staf_upper,
             uniform_ccs) = \
                self.__create_staf_obs_matrices_uniform(
                    self.__staf_observations.uniform_staf_obs)
        
            if len(normal_staf_means > 0):
                normal_staf_obs_eqs = pm.Deterministic(
                    'normal_staf_obs_eqs',
                    T.tensordot(
                        normal_staf_obs_matrix, stafs))

                normal_ccs = pm.Deterministic('normal_ccs', normal_ccs)

                reconciled_normal_eqs = \
                    normal_staf_obs_eqs[:, None] / normal_ccs[:, None]

                pm.Normal(
                    'normal_staf_observations',
                    mu=normal_staf_means[:, None],
                    sd=normal_staf_sds[:, None],
                    observed=reconciled_normal_eqs[:, None])

            if len(lognormal_staf_means > 0):
                lognormal_staf_obs_eqs = pm.Deterministic(
                    'lognormal_staf_obs_eqs',
                    T.tensordot(
                        lognormal_staf_obs_matrix, stafs))

                lognormal_ccs = pm.Deterministic(
                    'lognormal_ccs', lognormal_ccs)

                reconciled_lognormal_eqs = \
                    lognormal_staf_obs_eqs[:, None] / lognormal_ccs[:, None]

                pm.Lognormal(
                    'lognormal_staf_observations',
                    mu=lognormal_staf_means[:, None],
                    sd=lognormal_staf_sds[:, None],
                    observed=reconciled_lognormal_eqs[:, None])

            if len(uniform_staf_lower > 0):
                uniform_staf_obs_eqs = pm.Deterministic(
                    'uniform_staf_obs_eqs',
                    T.tensordot(
                        uniform_staf_obs_matrix, stafs))

                uniform_ccs = pm.Deterministic('uniform_ccs', uniform_ccs)

                reconciled_uniform_eqs = \
                    uniform_staf_obs_eqs[:, None] / uniform_ccs[:, None]

                pm.Uniform(
                    'uniform_staf_observations',
                    lower=uniform_staf_lower[:, None],
                    upper=uniform_staf_upper[:, None],
                    observed=reconciled_uniform_eqs[:, None])

    def get_input_inds(self, staf: Staf):
        """ Gets the process index of the destination of the staf """
        dest_id = staf.destination_process.diagram_id
        dest_math_process = self.__id_math_process_dict.get(dest_id)

        if not dest_math_process:
            raise ValueError("Process with id: {} ".format(dest_id) +
                             "is not in this math model")

        row_ind = dest_math_process.process_ind

        if isinstance(staf, Flow):
            col_ind = 0
        else:
            col_ind = 1

        return row_ind, col_ind

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

    def __add_external_input_prior(
            self,
            origin_id: str,
            dest_id: str,
            staf_uncert: 'Uncertainty',
            cc_uncert: 'Uncertainty'):
        """
        Adds a new staf observation as an input prior

        Args
        ------------
        origin_id (str): Diagram id of the origin of the staf value
        dest_id (str): Diagram id of the destination of the staf value
        staf_uncert (Uncertainty): Prior knowledge of staf value
        cc_uncer (Uncertainty): Prior knowledge of concentration
            coefficient
        """
        if dest_id not in self.__id_math_process_dict:
            raise ValueError("This diagram does not contain" +
                             " destination process with id {}"
                             .format(dest_id))

        staf_prior = ParamPrior(
            'Inflow', origin_id, dest_id, staf_uncert)

        cc_prior = ParamPrior(
            'Conc_Coeff',
            origin_id,
            dest_id,
            cc_uncert)

        input_prior = InputPrior(staf_prior, cc_prior)

        self.__input_priors.external_inputs_dict[dest_id] = input_prior

    def __add_stock_input_prior(
            self,
            origin_id: str,
            dest_id: str,
            staf_uncert: 'Uncertainty',
            cc_uncert: 'Uncertainty'):
        """
        Adds a new staf observation as an input prior

        Args
        ------------
        origin_id (str): Diagram id of the origin of the staf value
        dest_id (str): Diagram id of the destination of the staf value
        staf_uncert (Uncertainty): Prior knowledge of staf value
        cc_uncer (Uncertainty): Prior knowledge of concentration
            coefficient
        """
        if dest_id not in self.__id_math_process_dict:
            raise ValueError("This diagram does not contain" +
                             " destination process with id {}"
                             .format(dest_id))

        staf_prior = ParamPrior(
            'Stock Input', origin_id, dest_id, staf_uncert)

        cc_prior = ParamPrior(
            'Conc_Coeff',
            origin_id,
            dest_id,
            cc_uncert)

        input_prior = InputPrior(staf_prior, cc_prior)

        self.__input_priors.stock_inputs_dict[dest_id] = input_prior

    def __create_input_and_cc_matrices(self):
        """
        Builds inputs and input concentration coefficient matrices from
        external input and stock input priors
        """
        num_processes = len(self.__id_math_process_dict.keys())

        inputs_matrix = T.zeros((num_processes, 2))
        cc_matrix = T.ones((num_processes, 2))

        for process_id, external_input in \
                self.__input_priors.external_inputs_dict.items():

            process_index = self.__id_math_process_dict[process_id].process_ind

            external_input_prior = external_input.staf_prior
            external_input_rv = external_input_prior.create_param_rv()
            inputs_matrix = T.set_subtensor(
                inputs_matrix[[process_index], [0]], [external_input_rv])

            external_input_cc_prior = external_input.cc_prior
            external_input_cc_rv = external_input_cc_prior.create_param_rv()
            cc_matrix = T.set_subtensor(
                cc_matrix[[process_index], [0]],
                [external_input_cc_rv])

        for process_id, stock_input in \
                self.__input_priors.stock_inputs_dict.items():

            stock_input_prior = stock_input.staf_prior
            stock_input_rv = stock_input_prior.create_param_rv()
            inputs_matrix = T.set_subtensor(
                inputs_matrix[[process_index], [1]], [stock_input_rv])

            stock_input_cc_prior = stock_input.cc_prior
            stock_input_cc_rv = stock_input_cc_prior.create_param_rv()
            cc_matrix = T.set_subtensor(
                cc_matrix[[process_index], [1]], [stock_input_cc_rv])

        return inputs_matrix, cc_matrix

    def __create_input_priors(self, external_inflows: Set[Flow]):
        """
        Add observations of inflows to the model as prior distributions

        Args
        ----
        external_inflows (set(Flow)): Flows to processes inside the model from
            outside the model

        """
        for flow in external_inflows:

            if flow.staf_reference.time == self.reference_time:

                value = flow.get_value(self.reference_material)

                origin_id = flow.origin_process.diagram_id
                dest_id = flow.destination_process.diagram_id

                if value:

                    staf_uncert = value.uncertainty
                    cc_uncert = Constant(1)

                    self.__add_external_input_prior(
                        origin_id,
                        dest_id,
                        staf_uncert,
                        cc_uncert)

                else:
                    staf_value, cc_uncert = \
                        self.__material_reconciliation(flow)

                    if (staf_value is not None
                            and cc_uncert is not None):
                        
                        staf_uncert = staf_value.uncertainty

                        self.__add_external_input_prior(
                            origin_id,
                            dest_id,
                            staf_uncert,
                            cc_uncert)
                    else:
                        print("Inflow {} could not be reconciled"
                              .format(flow))

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
            process_stafs_dict: Dict[str, ProcessOutputs],
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

        self.__create_math_processes_from_internal_stafs(process_stafs_dict)
        self.__create_math_processes_from_external_outflows(external_outflows)

    def __create_math_processes_from_internal_stafs(
            self,
            process_stafs_dict: Dict[str, ProcessOutputs]):
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
                    if(value is not None):
                        self.__create_math_processes_from_staf(flow)

                    else:
                        value, cc_uncert = self.__material_reconciliation(flow)

                        if value is not None or cc_uncert is not None:
                            self.__create_math_processes_from_staf(flow)

            if process_outflows.stock is not None:
                stock = process_outflows.stock
                origin_process = stock.origin_process
                if (origin_process.process_type == 'Transformation'
                        or origin_process.process_type == 'Distribution'):

                    if stock.staf_reference.time == self.reference_time:

                        value = stock.get_value(self.reference_material)

                        if (value is not None):
                            if value.stock_type == 'Net':
                                self.__create_math_processes_from_staf(
                                    stock)

                        else:
                            value, cc_uncert = self.__material_reconciliation(
                                stock)

                            if value is not None or cc_uncert is not None:
                                if value.stock_type == 'Net':
                                    self.__create_math_processes_from_staf(
                                        stock)
                            else:
                                print("Staf {} could not be reconciled"
                                      .format(stock))

    def __create_math_processes_from_staf(self, staf: Staf):
        """
        Creates the math processes either side of the staf
        """

        # Stocks from the virtual reservoir are seen as inputs
        origin_id = staf.origin_process.diagram_id
        dest_id = staf.destination_process.diagram_id

        # If origin process has not been created yet then
        # create it
        if (origin_id not in self.__id_math_process_dict):
            self.__create_math_process(
                origin_id,
                staf.origin_process.process_type)

        outflow_tc_uncert = self.__get_tc_observation(origin_id, dest_id)
        outflow_tc = ParamPrior('TC', origin_id, dest_id, outflow_tc_uncert)
        self.__id_math_process_dict[origin_id] \
            .add_outflow(outflow_tc)

        # If destination process has not been created yet then
        # create it
        if (not self.__id_math_process_dict
                    .__contains__(dest_id)):
            self.__create_math_process(
                dest_id,
                staf.destination_process.process_type)

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
                if value is not None:

                    self.__create_math_processes_from_staf(flow)
                else:
                    value, cc_uncert = self.__material_reconciliation(flow)

                    if value is not None or cc_uncert is not None:
                        self.__create_math_processes_from_staf(flow)
    
    def __create_staf_obs_matrices_normal(self, staf_obs):
        """
        Create observation matrix to select out the flow equations we have
            lognormal observations for

        Args
        ---------------
        staf_obs (list(StafObservations)): List of staf value observations
        Returns
        ---------------
        observed_staf_matrix (np.array):
            num_obs x num_processes x num_processes matrix with 1s for each
            normal staf observation

        means_vector (np.array): The observed means of the flow values
        sds_vector (np.array): The observed standard deviations of the flow
            values
        """
        num_obs = len(staf_obs)
        num_procs = len(self.__id_math_process_dict.keys())

        observed_staf_matrix = np.zeros((num_obs, num_procs, num_procs))
        means_vector = np.zeros(num_obs)
        sds_vector = np.zeros(num_obs)
        ccs_vector = np.zeros(num_obs)

        for i, staf_obs in enumerate(staf_obs):
            staf_prior = staf_obs.staf_prior

            origin_id = staf_prior.origin_id
            origin_index = \
                self.__id_math_process_dict[origin_id].process_ind

            dest_id = staf_prior.dest_id
            dest_index = \
                self.__id_math_process_dict[dest_id].process_ind

            observed_staf_matrix[i][origin_index][dest_index] = 1

            cc_rv = staf_obs.cc_prior.create_param_rv()

            ccs_vector[i] = cc_rv
            means_vector[i] = staf_prior.uncertainty.mean
            sds_vector[i] = staf_prior.uncertainty.standard_deviation

        return observed_staf_matrix, means_vector, sds_vector, ccs_vector

    def __create_staf_obs_matrices_uniform(self, staf_obs):
        """
        Create observation matrix to select out the flow equations we have
            uniform observations for

        Args
        ---------------
        staf_obs (list(StafObservations)): List of staf value  uniform
            observations

        Returns
        ---------------
        observed_staf_matrix (np.array):
            num_obs x num_processes x num_processes matrix with 1s for each
            normal staf observation

        means_vector (np.array): The observed means of the flow values
        sds_vector (np.array): The observed standard deviations of the flow
            values
        """
        num_obs = len(staf_obs)
        num_procs = len(self.__id_math_process_dict.keys())
        observed_staf_matrix = np.zeros((num_obs, num_procs, num_procs))
        lower_vector = np.zeros(num_obs)
        upper_vector = np.zeros(num_obs)
        ccs_vector = np.zeros(num_obs)

        for i, staf_obs in enumerate(staf_obs):
            staf_prior = staf_obs.staf_prior

            origin_id = staf_prior.origin_id
            origin_index = \
                self.__id_math_process_dict[origin_id].process_ind

            dest_id = staf_prior.dest_id
            dest_index = \
                self.__id_math_process_dict[dest_id].process_ind

            observed_staf_matrix[i][origin_index][dest_index] = 1

            cc_rv = staf_obs.cc_prior.create_param_rv()
            ccs_vector[i] = cc_rv
            lower_vector[i] = staf_prior.uncertainty.lower
            upper_vector[i] = staf_prior.uncertainty.upper

        return observed_staf_matrix, lower_vector, upper_vector, ccs_vector

    def __create_staf_observations(
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
        """
        self.__create_staf_obs_from_internal_stafs(process_stafs_dict)
        self.__create_staf_obs_from_external_outflows(external_outflows)

    def __create_staf_obs_from_external_outflows(
            self,
            external_outflows: Set[Flow]):
        """
        Take the external outflows and creates flow observations from them

        Args
        ----
        process_stafs_dict (dict(str, set(Flow))): Maps a process to its
            outflows
        """

        for outflow in external_outflows:

            # Checks flow is about correct reference time
            if outflow.staf_reference.time == self.reference_time:

                value = outflow.get_value(self.reference_material)
                # Checks flow has an entry for the reference material
                if value:
                    origin_id = outflow.origin_process.diagram_id
                    dest_id = outflow.destination_process.diagram_id
                    staf_uncert = value.uncertainty
                    cc_uncert = Constant(1)
                    
                    self.__staf_observations.add_staf_observation(
                        origin_id,
                        dest_id,
                        staf_uncert,
                        cc_uncert)

                else:
                    
                    staf_value, cc_uncert = \
                        self.__material_reconciliation(outflow)

                    if (staf_value is not None
                            and cc_uncert is not None):

                        staf_uncert = staf_value.uncertainty

                        self.__staf_observations.add_staf_observation(
                            origin_id,
                            dest_id,
                            staf_uncert,
                            cc_uncert)
                    else:
                        print("Outflow {} could not be reconciled"
                              .format(outflow))

                    continue

    def __create_staf_obs_from_internal_stafs(
            self,
            process_stafs_dict: Dict[str, ProcessOutputs]):
        """
        Take the internal flows and creates staf observations from them

        Args
        ----
        process_stafs_dict (dict(str, set(Staf))): Maps a process to its
            outflows
        """

        for origin_process, process_outputs in process_stafs_dict.items():

            for flow in process_outputs.flows:
                # Checks flow is about correct reference time
                if flow.staf_reference.time == self.reference_time:

                    value = flow.get_value(self.reference_material)
                    # Checks flow has an entry for the reference material
                    if value:

                        origin_id = origin_process.diagram_id
                        dest_id = flow.destination_process.diagram_id

                        staf_uncert = value.uncertainty
                        cc_uncert = Constant(1)

                        self.__staf_observations.add_staf_observation(
                            origin_id,
                            dest_id,
                            staf_uncert,
                            cc_uncert)
                    else:

                        staf_value, cc_uncert = \
                            self.__material_reconciliation(flow)

                        if (staf_value is not None
                                and cc_uncert is not None):

                            staf_uncert = staf_value.uncertainty

                            self.__staf_observations.add_staf_observation(
                                origin_id,
                                dest_id,
                                staf_uncert,
                                cc_uncert)
                        else:
                            print("flow {} could not be reconciled"
                                  .format(flow))

            if process_outputs.stock is not None:
                stock = process_outputs.stock

                # Checks stock is about correct reference time
                if stock.staf_reference.time == self.reference_time:

                    value = stock.get_value(self.reference_material)
                    # Checks stock has an entry for the reference material and
                    # is a net stock value
                    if value is not None:
                        cc_uncert = Constant(1)
                    else:
                        value, cc_uncert = self.__material_reconciliation(
                            stock)

                        if value is None or cc_uncert is None:
                            print("Stock {} could not be reconciled"
                                  .format(stock))
                            continue

                    if value.stock_type == 'Net':

                        origin_id = origin_process.diagram_id
                        dest_id = stock.destination_process.diagram_id

                        staf_uncert = value.uncertainty

                        if origin_process.process_type == 'Storage':

                            self.__add_stock_input_prior(
                                origin_id,
                                dest_id,
                                staf_uncert,
                                cc_uncert)

                        else:
                            self.__staf_observations.add_staf_observation(
                                origin_id,
                                dest_id,
                                staf_uncert,
                                cc_uncert)

    def __create_transfer_coefficient_matrix(self) -> T.Variable:
        """
        Builds matrix with transfer coeffs represented as random variables

        Args
        ------------
        transformation_coeffs_obs (dict(str, ParamPrior)):
            Maps transformation process ids to an observation of its
            transfer coefficient

        distribution_coeffs_obs (dict(str, DistributionCoefficients)):
            Maps distribution process ids to an observation of its transfer
            coefficients
        """
        num_of_processes = len(self.__id_math_process_dict.keys())

        tc_matrix = T.zeros((num_of_processes, num_of_processes))

        for _, math_process in self.__id_math_process_dict.items():
            dest_ids, dest_rvs = \
                math_process.create_outflow_tc_rvs()

            origin_ind = math_process.process_ind

            dest_inds = [self.__id_math_process_dict[pid].process_ind
                         for pid in dest_ids]

            tc_matrix = T.set_subtensor(
                tc_matrix[[origin_ind], dest_inds], dest_rvs)

        return tc_matrix

    def __get_process_ind(self, process_id: str) -> int:
        """ Returns the index of the process in the matrix if id exists """

        ind = self.__id_math_process_dict[process_id]
        if not ind:
            raise ValueError("Process id {} does not exist"
                             .format(process_id))

        return ind

    def __get_tc_observation(self, origin_id: str, dest_id: str) \
            -> Uncertainty:
        """
        Search tc_observation_table for TC prior
        """
        row = self.__tc_observation_table.get(origin_id)

        if row is not None:
            return row.get(dest_id)
        else:
            return None

    def __material_reconciliation(self, staf: Staf):
        """
        If possible, reconciles the materials in the staf into the reference
        material

        Args
        -------
        staf (Staf): Staf being reconciled

        Returns
        -------
        staf_uncert, cc_uncert
            (tuple(Uncertainty, Uncertainty)): None, None id reconciliation is
            not possible, otherwise the uncertainty of the unreconciled staf
            value and the uncertainty of the reconciliation coefficient
        """
        for material in staf.get_materials():

            material_cc_uncert = self.__material_reconc_table.get(material)

            if material_cc_uncert is not None:

                material_staf_value = staf.get_value(material)

                return material_staf_value, material_cc_uncert

        return None, None


class MathProcess():
    """
    Parent class for calculating mathematical models of processes

    Attributes
    ------------------------
    process_id (str): Id for the process in the math model
    process_ind (int): Index of process in the matrix
    process_outflow_tcs (list(ParamPrior)): Prior knowledge of transfer
        coefficients for this process
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
        """
        assert isinstance(process_id, str)
        assert isinstance(process_ind, int)

        self.process_id = process_id
        self.process_ind = process_ind
        self.process_outflow_tcs = []
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

    def add_outflow(self, process_outflow_tc: 'ParamPrior'):
        """
        Add an outflow to the process

        Args
        -----------
        process_outflow_tc (ParamPrior): Prior knowledge about outflow tc
        """
        assert isinstance(process_outflow_tc, ParamPrior)

        self.process_outflow_tcs.append(process_outflow_tc)
        self.n_outflows += 1

    def create_outflow_tc_rvs(self) \
            -> Tuple[List[str], pm.Continuous]:
        """
        Create RVs for transfer coefficients for the process

        Args
        -----------
        dist_coeffs (DistributionCoefficients): known transfer coefficients
        """

        assert (self.n_outflows == len(self.process_outflow_tcs))

        if (self.n_outflows == 0):
            return [], 0

        # If no coefficients supplied, model as a uniform dirichlet
        # distribution
        shares = []
        outflow_process_ids = []
        for tc in self.process_outflow_tcs:

            tc_uncertainty = tc.uncertainty
            if isinstance(tc_uncertainty, Uncertainty):
                shares.append(tc_uncertainty.mean)
            else:
                shares.append(1)

            outflow_process_ids.append(tc.dest_id)
        shares = np.array(shares)

        if self.n_outflows == 1:
            random_variable = pm.Deterministic(
                "P_{}".format(self.process_id), T.ones(1,))

        else:
            random_variable = pm.Dirichlet(
                "P_{}".format(self.process_id), shares)
        
        return outflow_process_ids, random_variable


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

    def add_outflow(self, process_outflow_tc: 'ParamPrior'):
        """
        Add an outflow to the process

        Args
        -----------
        process_outflow_tc (ParamPrior): Math id of receiving process
        """
        if self.n_outflows >= 2:
            raise ValueError(
                "A transformation process can have at most 2 outflows")

        self.process_outflow_tcs.append(process_outflow_tc)
        self.n_outflows += 1

    def create_outflow_tc_rvs(self) \
            -> Tuple[List[str], pm.Continuous]:
        """
        Create RVs for the transfer coefficients for the process
        """

        assert (self.n_outflows == len(self.process_outflow_tcs))

        if (self.n_outflows == 0):
            
            return [], 0

        if self.n_outflows == 1:
            dest_id = self.process_outflow_tcs[0].dest_id
            random_variable = pm.Deterministic(
                "P_{}".format(
                    self.process_id),
                T.ones(1,))

            return [dest_id], random_variable

        if self.n_outflows == 2:
            known_outflow_tc, unknown_outflow_tc = self.__identify_known_tc()

            known_outflow_rv = known_outflow_tc.create_param_rv()

            # Enforce the TC to be between 0 and 1
            coefficient_1 = ParamPrior.enforce_range(known_outflow_rv)

            random_variables = T.stack([coefficient_1, 1-coefficient_1])

            known_outflow_id = known_outflow_tc.dest_id

            unknown_outflow_id = unknown_outflow_tc.dest_id

            process_ids = [known_outflow_id, unknown_outflow_id]

            return process_ids, random_variables

        else:
            raise ValueError("Transformation process should not have more" +
                             " than 2 outflows")

    def __identify_known_tc(self):
        """
        Checks if either transfer coefficient is known
        """
        assert (len(self.process_outflow_tcs) == 2)
        outflow_tc_1, outflow_tc_2 = self.process_outflow_tcs

        if isinstance(outflow_tc_1.uncertainty, Uncertainty):
            known_outflow_tc = outflow_tc_1
            unknown_outflow_tc = outflow_tc_2

            return known_outflow_tc, unknown_outflow_tc
        elif isinstance(outflow_tc_2.uncertainty, Uncertainty):
            known_outflow_tc = outflow_tc_2
            unknown_outflow_tc = outflow_tc_1

            return known_outflow_tc, unknown_outflow_tc
        else:
            outflow_tc_1.uncertainty = UniformUncertainty(lower=0, upper=1)
            outflow_tc_2.uncertainty = UniformUncertainty(lower=0, upper=1)

            return outflow_tc_1, outflow_tc_2


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


class ParamPrior():
    """
    Prior knowledge of a parameter in the mathematical model
    Creates a random variable representing the value of the parameter
    Attributes
    ----------
    param_name (str): Name of the parameter
    param_type (str): Type of parameter
    origin_id (str): Origin process id
    dest_id (str): Destination process id
    uncertainty (Uncertainty): Quantity of flow and its uncertainty
    """

    def __init__(
            self,
            param_type: str,
            origin_id: str,
            dest_id: str,
            uncertainty: Uncertainty):
        """
        Args
        ----------
        param_type (str): Type of parameter
        origin_id (str): Origin process id
        dest_id (str): Destination process id
        uncertainty (Uncertainty): Quantity of flow and its uncertainty
        """
        assert isinstance(param_type, str)
        assert isinstance(origin_id, str)
        assert isinstance(dest_id, str)
        assert isinstance(uncertainty, Uncertainty) or uncertainty is None

        self.param_type = param_type
        self.origin_id = origin_id
        self.dest_id = dest_id

        self.param_name = "{}-{}_{}".format(
            param_type, origin_id, dest_id)
        self.uncertainty = uncertainty

    def create_param_rv(self):
        """
        Create random variable for this parameter
        """

        if isinstance(self.uncertainty, UniformUncertainty):
            return pm.Uniform(
                self.param_name,
                lower=self.uncertainty.lower,
                upper=self.uncertainty.upper)

        elif isinstance(self.uncertainty, NormalUncertainty):
            return pm.Normal(
                self.param_name,
                mu=self.uncertainty.mean,
                sd=self.uncertainty.standard_deviation)

        elif isinstance(self.uncertainty, LognormalUncertainty):
            return pm.Lognormal(
                self.param_name,
                mu=self.uncertainty.mean,
                sd=self.uncertainty.standard_deviation)

        elif isinstance(self.uncertainty, Constant):
            return np.float(self.uncertainty.mean)

        else:
            raise ValueError(
                "Uncertainty parameter is of unknown distribution")

    @staticmethod
    def enforce_range(param_rv):
        """
        Enforce the random variable to be between 0 and 1
        """
        pos_rv = T.maximum(0, param_rv)
        enforced_rv = T.minimum(1, pos_rv)

        return enforced_rv


class InputPriors():
    """
    Stores the external inputs and inputs from stocks into the model.

    Attributes
    ---------------
    external_inputs_dict (dict(str, InputPrior)): Maps the process id to
        its external inputs

    stock_inputs_dict (dict(str, InputPrior)): Maps the process id to its
        input from stock
    """

    def __init__(self):

        self.external_inputs_dict: Dict[str, InputPriors] = {}
        self.stock_inputs_dict: Dict[str, InputPriors] = {}


class InputPrior():
    """
    Contains prior observations for stock or flow input to model and its
    concentration coefficient

    Attributes
    ------------
    staf_prior (ParamPrior): Prior knowledge of stock or flow value
    cc_prior (ParamPrior): Prior knowledge of a concentration
        coefficient
    """

    def __init__(self, staf_prior: ParamPrior, cc_prior: ParamPrior):
        """
        Args
        ------------
        staf_prior (ParamPrior): Prior knowledge of stock or flow value
        cc (ParamPrior): Prior knowledge of a concentration
            coefficient
        """
        self.staf_prior = staf_prior
        self.cc_prior = cc_prior


class StafObservation():
    """
    Stores the observation of the staf value and its concentration coefficient
    
    Attributes
    -------------
    staf_prior (ParamPrior): Observation of staf value
    cc_prior (ParamPrior): Observation of concentration coefficient
    """

    def __init__(self, staf_prior, cc_prior):
        """
        Attributes
        -------------
        staf_prior (ParamPrior): Observation of staf value
        cc_prior (ParamPrior): Observation of concentration coefficient
        """
        assert isinstance(staf_prior, ParamPrior)
        assert isinstance(cc_prior, ParamPrior)

        self.staf_prior = staf_prior
        self.cc_prior = cc_prior


class StafObservations():
    """
    Stores all dependent parameter observations and applies them to the model
    """

    def __init__(self):
        self.normal_staf_obs: List[StafObservation] = []
        self.lognormal_staf_obs: List[StafObservation] = []
        self.uniform_staf_obs: List[StafObservation] = []

    def add_staf_observation(
            self,
            origin_id: str,
            dest_id: str,
            staf_uncert: Uncertainty,
            cc_uncert: Uncertainty):
        """
        Creates a staf observation and adds it to the correct list

        Args
        -----------
        origin_id (str): Origin process id for the staf
        dest_id (str): Destination process id for the staf
        staf_uncert (Uncertainty): Uncertainty of staf value
        cc_uncert (Uncertainty): Uncertainty of concentration coefficient for
            staf value
        """
        staf_prior = ParamPrior(
            "Staf Observation", origin_id, dest_id, staf_uncert)

        cc_prior = ParamPrior(
            "CC Observation", origin_id, dest_id, cc_uncert)

        staf_observation = StafObservation(staf_prior, cc_prior)
        if staf_uncert is None:
            return
        if isinstance(staf_uncert, NormalUncertainty):
            self.normal_staf_obs.append(staf_observation)
        elif isinstance(staf_uncert, LognormalUncertainty):
            self.lognormal_staf_obs.append(staf_observation)
        elif isinstance(staf_uncert, UniformUncertainty):
            self.uniform_staf_obs.append(staf_observation)
        else:
            raise ValueError("Staf observation has uncertainty of unsupported"
                             + "distribution, instead was {}"
                             .format(type(staf_uncert)))
        

if __name__ == '__main__':
    sys.exit(1)
