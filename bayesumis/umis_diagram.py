"""Classes for a graph of processes and flows"""
import sys
from typing import List, Mapping, Set

from bayesumis.umis_data_models import (
    Flow,
    Process,
    Reference,
    Stock,
    Value)


class UmisDiagram():
    """
    Representation of a UMIS diagram, serves to add new processes and
    flows whilst ensuring that they are legal.

    Attributes
    ----------
    reference (Reference): Attributes that the stocks and flows are
        in reference to

    processes (processes): List of all processes for this UMIS diagram

    external_inflows (set(Process)): List of flows into processes from
        outside the diagram

    external_outflows (set(Flow)): List of flows from processes to outside
        the diagram

    process_outflow_dict (dict(Process, list(Flow)): Mapping from processes to
        their outflows
    """

    def __init__(
                self,
                external_inflows: List[Flow],
                internal_flows: List[Flow],
                external_outflows: List[Flow],
                stocks: List[Stock]):
        """
        Initializes a diagram from its components and ensures that it is valid
        within UMIS definitions

        Args
        ----

        processes: List of all processes for this UMIS diagram
        external_inflows: List of flows into processes from outside the diagram
        internal_flows: List of flows between processes in the diagram
        external_outflows: List of flows from processes to outside the diagram
        """

        self.reference = Reference
    
        self.__add_internal_flows(internal_flows)

        self.__add_external_inflows(external_inflows)

        self.__add_external_outflows(external_outflows)

        self.__add_stocks(stocks)

    def __add_processes(self, processes: List[Process]):
        """
        Adds processes to dict with validation

        Args
        ----
        processes (list(process)): List of processes to be added
        """

        if len(processes) < 2:
            raise ValueError("Must add at least 2 processes")

        self.process_outflows_dict: Mapping[Process, Set[Flow]] = {}

        process_types = [self.__add_process(p) for p in processes]

        number_of_t_processes = process_types.count('T')
        number_of_d_processes = process_types.count('D')

        if number_of_d_processes != number_of_t_processes:
            raise ValueError(
                "Graph must have equal number of transformation and" +
                "distriubtion processes")

        return

    def __add_process(self, process: Process) -> str:
        """
        Adds a new process to the diagram, updates reference sets if needed

        Args
        ----
        process (Process): Process to be added

        Returns
        -------
        returns 'T' if the process is a transformation process and
        'D' if it is distribution
        """

        if process in self.process_outflows_dict:
            raise ValueError(
                "Process {} with id {} is already in the diagram"
                .format(process.name, process.uuid))

        if process.is_transformation:
            process_type = 'T'

        else:
            process_type = 'D'

        self.process_outflows_dict[process] = set()

        if process.stock:
                if not isinstance(process.stock.value, Value):
                    raise TypeError("Stock not of type Value")

                self.__update_diagram_reference(process.stock.reference)

        return process_type

    def __add_internal_flows(self, flows: List[Flow]):
        """
        Checks legality of all internal flows and adds them to the diagram

        Args
        ----

        flows (list(Flow)): List of internal flows
        """

        for flow in flows:
            origin_process = flow.origin
            if origin_process not in self.process_outflows_dict:
                raise ValueError(
                    "Origin process of internal flow ({}) is not in diagram"
                    .format(flow))

            destination_process = flow.destination
            if destination_process not in self.process_outflows_dict:
                raise ValueError(
                    "Destination process of internal flow ({})".format(flow) +
                    " is not in diagram")

            if self.process_outflows_dict[origin_process].__contains__(flow):
                raise ValueError(
                    "Internal flow {} has already been input".format(flow))

            self.process_outflows_dict[origin_process].add(flow)

            self.__update_diagram_reference(flow.reference)

    def __add_external_outflows(self, flows: List[Flow]):
        """Checks legality of external outflow and adds it to the diagram"""

        self.external_outflows = set()
        for flow in flows:
            origin_process = flow.origin
            if origin_process not in self.process_outflows_dict:
                raise ValueError(
                    "Origin process of external outflow ({}) is not in diagram"
                    .format(flow))

            destination_process = flow.destination
            if destination_process in self.process_outflows_dict:
                raise ValueError(
                    "Destination process of external outflow ({}) is in"
                    .format(flow)) + "diagram"

            if self.external_outflows.__contains__(flow):
                raise ValueError(
                    "External outflow {} has already".format(flow) +
                    " been input")

            self.external_outflows.add(flow)

            self.__update_diagram_reference(flow.reference)

    def __add_external_inflows(self, flows: List[Flow]):
        """ Checks legality of external inflows, adds them to the diagram """

        self.external_inflows = set()
        for flow in flows:
            origin_process = flow.origin
            if origin_process in self.process_outflows_dict:
                raise ValueError(
                    "Origin process of external inflow ({}) is in diagram"
                    .format(flow))

            destination_process = flow.destination
            if destination_process not in self.process_outflows_dict:
                raise ValueError(
                    "Destination process of external outflow ({}) is not in"
                    .format(flow)) + "diagram"

            if self.external_inflows.__contains__(flow):
                raise ValueError(
                    "External inflow {} has already".format(flow) +
                    " been input")

            self.external_inflows.add(flow)

            self.__update_diagram_reference(flow.reference)

    def __update_diagram_reference(self, new_reference: Reference):
        """
        Update reference with new reference
        """
        self.reference = new_reference


if __name__ == '__main__':
    sys.exit(1)
