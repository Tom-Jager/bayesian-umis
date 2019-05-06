"""Classes for a graph of processes and flows"""
import sys
from typing import Dict, Set

from .umis_data_models import (
    DiagramReference,
    Flow,
    ProcessOutputs,
    Staf,
    Stock,
    UmisProcess
)


class UmisDiagram():
    """
    Representation of a UMIS diagram, serves to add new processes and
    flows whilst ensuring that they are legal.

    Attributes
    ----------
    external_inflows (set(Flow)): Set of flows into processes from
        outside the diagram

    external_outflows (set(Flow)): Set of flows from processes to outside
        the diagram

    process_stafs_dict(dict(str, UmisProcess)): Mapping of process to its
        outflows and stocks

    reference (Reference): Attributes that the stocks and flows are
        in reference to    
    """

    def __init__(
                self,
                external_inflows: Set[Flow],
                internal_stafs: Set[Staf],
                external_outflows: Set[Flow]):
        """
        Initializes a diagram from its components and ensures that it is valid
        within UMIS definitions

        Args
        ----

        external_inflows: Set of flows into processes from outside the diagram
        internal_stafs: Set of stocks and flows between processes in the
            diagram
        external_outflows: Set of flows from processes to outside the diagram
        """

        self.reference = DiagramReference()

        self.__process_stafs_dict: Dict[UmisProcess, ProcessOutputs] = {}

        self.__add_internal_stafs(internal_stafs)

        self.__add_external_inflows(external_inflows)

        self.__add_external_outflows(external_outflows)

    def __add_internal_stafs(self, stafs: Set[Staf]):
        """
        Adds internal stafs and their processes to the diagram

        Args
        ----

        stafs (set(Staf)): Set of internal stafs
        """

        for staf in stafs:

            if isinstance(staf, Stock):

                if staf.origin_process == "Storage":
                    graph_process = staf.destination_process
                elif staf.destination_process == "Storage":
                    graph_process = staf.origin_process
                else:
                    raise ValueError("At least one process must be a storage "
                                     + "process")

                if graph_process not in self.__process_stafs_dict:
                    self.__process_stafs_dict[graph_process] = ProcessOutputs()

                graph_process_outflows = \
                    self.__process_stafs_dict[graph_process]

                if (graph_process_outflows.stock is None):
                    graph_process_outflows.stock = staf
                else:
                    raise ValueError("Cannot add stock {} as process {}"
                                     .format(staf, graph_process)
                                     + " already has a stock {} assigned"
                                     .format(graph_process_outflows.stock))

            elif isinstance(staf, Flow):
                graph_process = staf.origin_process

                if graph_process not in self.__process_stafs_dict:
                    self.__process_stafs_dict[graph_process] = ProcessOutputs()

                graph_process_outflows = \
                    self.__process_stafs_dict[graph_process]

                graph_process_outflows.flows.add(staf)

                dest_process = staf.destination_process
                if dest_process not in self.__process_stafs_dict:
                    self.__process_stafs_dict[dest_process] = ProcessOutputs()
            else:
                raise TypeError("Staf {} is of wrong type, expected Stock"
                                .format(staf)
                                + " or Flow, found {} instead"
                                .format(type(staf)))

            # This is where we would update the diagram reference space, 
            # material and time to reflect the entire diagram
            self.__update_diagram_reference(
                staf.staf_reference.time,
                staf.staf_reference.material,
                staf.origin_process.reference_space,
                staf.destination_process.reference_space)

    def __add_external_inflows(self, flows: Set[Flow]):
        """ Checks legality of external inflows, adds them to the diagram """

        self.__external_inflows = set()
        for flow in flows:
            self.__check_flow_type(flow)

            origin_process = flow.origin_process
            if origin_process in self.__process_stafs_dict:
                raise ValueError(
                    "Origin process of external inflow ({}) is in diagram"
                    .format(flow))

            if self.__external_inflows.__contains__(flow):
                raise ValueError(
                    "External inflow {} has already".format(flow) +
                    " been input")

            dest_process = flow.destination_process
            if dest_process not in self.__process_stafs_dict:
                self.__process_stafs_dict[dest_process] = ProcessOutputs()

            self.__external_inflows.add(flow)

            self.__update_diagram_reference(
                flow.staf_reference.time,
                flow.staf_reference.material,
                flow.origin_process.reference_space,
                flow.destination_process.reference_space)

    def __add_external_outflows(self, flows: Set[Flow]):
        """Checks legality of external outflow and adds it to the diagram"""

        self.__external_outflows = set()
        for flow in flows:
            self.__check_flow_type(flow)

            dest_process = flow.destination_process

            if dest_process in self.__process_stafs_dict:
                raise ValueError(
                    "Destination process of external outflow ({}) is in"
                    .format(flow)) + "diagram"

            if self.__external_outflows.__contains__(flow):
                raise ValueError(
                    "External outflow {} has already".format(flow) +
                    " been input")

            self.__external_outflows.add(flow)

            self.__update_diagram_reference(
                flow.staf_reference.time,
                flow.staf_reference.material,
                flow.origin_process.reference_space,
                flow.destination_process.reference_space)

    def __check_flow_type(self, flow):
        """
        Type checks flow
        """
        if not isinstance(flow, Flow):
            raise TypeError(
                "Tried to add {}, when should be adding a Flow"
                .format(flow))

    def __update_diagram_reference(self, *args, **kwargs):
        """
        Update reference with new reference

        Args
        ----

        new_reference (Reference): New incoming reference
        """
        pass

    def get_process_stafs_dict(self):
        """
        Returns process stafs dict
        """
        return self.__process_stafs_dict

    def get_external_inflows(self):
        """
        Returns external inflows
        """

        return self.__external_inflows

    def get_external_outflows(self):
        """
        Returns external inflows
        """

        return self.__external_outflows


if __name__ == '__main__':
    sys.exit(1)
