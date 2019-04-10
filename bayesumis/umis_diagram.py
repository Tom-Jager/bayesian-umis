"""Classes for a graph of processes and flows"""
import sys
from typing import Dict, Set

from .umis_data_models import (
    DiagramReference,
    Flow,
    UmisProcess,
    Staf,
    Stock
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

    process_outflows_dict(dict(str, Process)): Mapping of process to its
        outflows

    reference (Reference): Attributes that the stocks and flows are
        in reference to    
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
        internal_flows: Set of stocks and flows between processes in the
            diagram
        external_outflows: Set of flows from processes to outside the diagram
        """

        self.reference = DiagramReference()

        self.__process_stafs_dict: Dict[UmisProcess, Set[Staf]] = {}

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
            
            flow: Flow = flow
            self.__check_flow_type(flow)

            self.__add_flow(flow)

            dest_process = flow.destination
            if dest_process not in self.__process_stafs_dict:
                self.__process_stafs_dict[dest_process] = set()

            self.__update_diagram_reference(
                flow.staf_reference.time,
                flow.staf_reference.material,
                flow.origin.reference_space,
                flow.destination.reference_space)

    def __add_external_inflows(self, flows: Set[Flow]):
        """ Checks legality of external inflows, adds them to the diagram """

        self.__external_inflows = set()
        for flow in flows:
            self.__check_flow_type(flow)

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

            self.__external_inflows.add(flow)

            self.__update_diagram_reference(
                flow.staf_reference.time,
                flow.staf_reference.material,
                flow.origin.reference_space,
                flow.destination.reference_space)

    def __add_external_outflows(self, flows: Set[Flow]):
        """Checks legality of external outflow and adds it to the diagram"""

        self.__external_outflows = set()
        for flow in flows:
            self.__check_flow_type(flow)

            dest_process = flow.destination

            if dest_process in self.process_outflows_dict:
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
                flow.origin.reference_space,
                flow.destination.reference_space)

    def __add_flow(self, flow: Flow):
        """
        Adds flow to process_outflow_dict

        Args
        ---------
        flow (Flow)
        """
        origin_process = flow.origin
        if origin_process not in self.__process_stafs_dict:
            self.__process_stafs_dict[origin_process] = set()
        
        self.__process_stafs_dict[origin_process].add(flow)

    def __add_stocks(self, stocks: Set[Stock]):
        """ Add stocks to processes in diagram """

        for stock in stocks:
            if not isinstance(stock, Stock):
                raise TypeError(
                    "Expected type Stock, was {} instead".format(type(stock)))

            stock_process = stock.stock_process
            
            if stock_process not in self.__process_stafs_dict:
                self.__process_stafs_dict[stock_process] = set()

            self.__process_stafs_dict[stock_process].add(stock)
            
            self.__update_diagram_reference(
                stock.staf_reference.time,
                stock.staf_reference.material,
                stock.process.reference_space)

    def __check_flow_type(self, flow):
        """
        Type checks flow
        """
        if not isinstance(flow, Flow):
            raise TypeError(
                "Tried to add {}, when should be adding a Flow"
                .format(flow))

    def __get_process_outflows_dict(self):
        """
        Returns process outflows dict
        """
        return self.__process_stafs_dict

    def __get_external_inflows(self):
        """
        Returns external inflows
        """

        return self.__external_inflows

    def __get_external_outflows(self):
        """
        Returns external inflows
        """

        return self.__external_outflows

    def __update_diagram_reference(self, *args, **kwargs):
        """
        Update reference with new reference

        Args
        ----

        new_reference (Reference): New incoming reference
        """
        pass


if __name__ == '__main__':
    sys.exit(1)
