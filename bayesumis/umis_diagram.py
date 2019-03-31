"""Classes for a graph of processes and flows"""
import sys
from typing import Dict, Set

from .umis_data_models import (
    Flow,
    UmisProcess,
    Reference,
    Stock)

from . import umis_diagram_helper_functions as helper_functions


class UmisDiagram():
    """
    Representation of a UMIS diagram, serves to add new processes and
    flows whilst ensuring that they are legal.

    Attributes
    ----------
    reference (Reference): Attributes that the stocks and flows are
        in reference to

    process_store(dict(str, Process)): Mapping of process id to the process in
        the diagram

    external_inflows (set(Flow)): Set of flows into processes from
        outside the diagram

    external_outflows (set(Flow)): Set of flows from processes to outside
        the diagram

    process_outflow_dict (dict(str, set(Flow)): Mapping from process id to
        the process' outflows
    """

    def __init__(
                self,
                external_inflows: Set[Flow],
                internal_flows: Set[Flow],
                external_outflows: Set[Flow],
                stocks: Set[Stock]):
        """
        Initializes a diagram from its components and ensures that it is valid
        within UMIS definitions

        Args
        ----

        external_inflows: Set of flows into processes from outside the diagram
        internal_flows: Set of flows between processes in the diagram
        external_outflows: Set of flows from processes to outside the diagram
        stocks: Set of stocks for processes is in diagram
        """

        self.reference = Reference

        self.process_store: Dict[str, UmisProcess] = {}

        self.process_outflows_dict: Dict[str, UmisProcess] = {}

        self.__add_internal_flows(internal_flows)

        self.__add_external_inflows(external_inflows)

        self.__add_external_outflows(external_outflows)

        self.__add_stocks(stocks)

    def __add_internal_flows(self, flows: Set[Flow]):
        """
        Adds internal flows and their processes to the diagram

        Args
        ----

        flows (list(Flow)): List of internal flows
        """

        for flow in flows:
            helper_functions.check_flow_type(flow)

            origin_process = flow.origin
            if origin_process.diagram_id not in self.process_outflows_dict:
                self.process_outflows_dict[origin_process.diagram_id] = {flow}
                self.process_store[origin_process.diagram_id] = origin_process
            else:
                self.process_outflows_dict[origin_process.diagram_id].add(flow)

            dest_process = flow.destination
            if dest_process.diagram_id not in self.process_outflows_dict:
                self.process_outflows_dict[dest_process.diagram_id] = set()

                self.process_store[dest_process.diagram_id] = \
                    dest_process

            self.__update_diagram_reference(flow.reference)

    def __add_external_outflows(self, flows: Set[Flow]):
        """Checks legality of external outflow and adds it to the diagram"""

        self.external_outflows = set()
        for flow in flows:
            helper_functions.check_flow_type(flow)

            origin_process = flow.origin
            dest_process = flow.destination

            if dest_process.diagram_id in self.process_outflows_dict:
                raise ValueError(
                    "Destination process of external outflow ({}) is in"
                    .format(flow)) + "diagram"

            if self.external_outflows.__contains__(flow):
                raise ValueError(
                    "External outflow {} has already".format(flow) +
                    " been input")

            if origin_process.diagram_id not in self.process_outflows_dict:
                self.process_outflows_dict[origin_process.diagram_id] = set()

            self.external_outflows.add(flow)

            self.__update_diagram_reference(flow.reference)

    def __add_external_inflows(self, flows: Set[Flow]):
        """ Checks legality of external inflows, adds them to the diagram """

        self.external_inflows = set()
        for flow in flows:
            helper_functions.check_flow_type(flow)

            origin_process = flow.origin
            if origin_process.diagram_id in self.process_outflows_dict:
                raise ValueError(
                    "Origin process of external inflow ({}) is in diagram"
                    .format(flow))

            if self.external_inflows.__contains__(flow):
                raise ValueError(
                    "External inflow {} has already".format(flow) +
                    " been input")

            dest_process = flow.destination
            if dest_process.diagram_id not in self.process_outflows_dict:
                self.process_outflows_dict[dest_process.diagram_id] = set()
                self.process_store[dest_process.diagram_id] = \
                    dest_process

            self.external_inflows.add(flow)

            self.__update_diagram_reference(flow.reference)

    def __add_stocks(self, stocks: Set[Stock]):
        """ Add stocks to processes in diagram """

        for stock in stocks:
            if not isinstance(stock, Stock):
                raise TypeError(
                    "Expected type Stock, was {} instead".format(type(stock)))

            stock_process_id = UmisProcess.create_diagram_id(
                stock.process_stafdb_id, stock.reference.origin_space)
            if stock_process_id not in self.process_outflows_dict:
                raise ValueError(
                    "Stock cannot be added for process with id: {}"
                    .format(stock_process_id) + " as it is not in the diagram")

            self.process_store[stock_process_id].add_stock(stock)
            self.__update_diagram_reference(stock.reference)

    def __update_diagram_reference(self, new_reference: Reference):
        """
        Update reference with new reference

        Args
        ----

        new_reference (Reference): New incoming reference
        """
        self.reference = new_reference


if __name__ == '__main__':
    sys.exit(1)
