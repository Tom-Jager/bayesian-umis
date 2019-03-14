"""Classes for a graph of processes and flows"""
import collections.abc
import sys
from typing import Type


class Stock():
    """ A stock of material stored in STAFDB """

    def __init__(self):
        pass


class Storage():
    """ A node which stores a stock """
    def __init__(self, stock: Stock):
        self.stock = stock


class Process(collections.abc.Hashable):
    """A process in a UMIS diagram"""

    def __init__(
            self,
            uuid: str,
            name: str,
            is_separator: bool,
            parent_id: str):

        """Constructs a process object"""
        self.uuid = uuid
        self.name = name
        self.is_separator = is_separator
        self.parent_id = parent_id

    def __eq__(self, process_b):
        return self.uuid == process_b.uuid

    def __hash__(self):
        return self.uuid.__hash__()


class TransformationProcess(Process):
    """ A transformation process """

    def __init__(
            self,
            uuid: str,
            name: str,
            is_separator: bool,
            parent_id: str,
            storage: Storage = None):
        """ Creates a transformation process """
        super().__init__(
            uuid,
            name,
            is_separator,
            parent_id,
        )

        self.storage = storage


class DistributionProcess(Process):
    """ A distribution process """

    def __init__(
            self,
            uuid: str,
            name: str,
            is_separator: bool,
            parent_id: str):
        """ Creates a distribution process """

        super().__init__(
            uuid,
            name,
            is_separator,
            parent_id,
        )


class Flow(object):
    """A flow between transformative and distributive processes"""
    def __init__(
                self,
                origin: Process,
                destination: Process,
                value: float):
        """Represents the flow of stock from one process to another"""
        pass


class UmisDiagram(object):
    """Representation of a UMIS diagram, serves to add new processes and
    flows whilst ensuring that they are legal."""

    def __init__(
                self,
                processes: list,
                external_inflows: list,
                internal_flows: list,
                external_outflows: list):
        """Initializes a diagram from its components and ensures that it is valid
        within UMIS definitions

        processes: List of all processes for this UMIS diagram
        external_inflows: List of flows into processes from outside the diagram
        internal_flows: List of flows between processes in the diagram
        external_outflows: List of flows from processes to outside the diagram
        """

        self.process_outflows_dict = {}
        """Mapping from processes to their outflows, must be a dictionary"""

        try:
            self.__add_processes(processes)
        except Exception as err:
            print("Error when adding processes: {}".format(err))

        try:
            self.__add_internal_flows(internal_flows)
        except Exception as err:
            print("Error when adding internal flows: {}".format(err))

        try:
            self.__add_external_inflows(external_inflows)
        except Exception as err:
            print("Error when adding external inflows: {}".format(err))

        try:
            self.__add_external_outflows(external_outflows)
        except Exception as err:
            print("Error when adding external outflows: {}".format(err))

    def __add_processes(self, processes: list):
        """Adds processes to dict with validation"""

        if len(processes <= 2):
            raise ValueError("Processes must be of at least length 2")

        process_types = [self.__add_process(p) for p in processes]

        number_of_t_processes = process_types.count('T')
        number_of_d_processes = process_types.count('D')

        if number_of_d_processes != number_of_t_processes:
            raise ValueError(
                "Graph must have equal number of transformation and" +
                "distriubtion processes")

        return

    def __add_process(self, process: Type[Process]):
        """Adds a new process to the diagram"""
        if process in self.process_outflows_dict:
            raise ValueError(
                "Process {} with id {} is already in the diagram"
                .format(process.name, process.uuid))

        if isinstance(process, TransformationProcess):
            process_type = 'T'
        else:
            if isinstance(process, DistributionProcess):
                process_type = 'D'
            else:
                TypeError(
                    "process is of type {}:".format(type(process)) +
                    " TransformationProcess or DistributionProcess expected")

        self.process_outflows_dict[process] = []

        return process_type

    def __add_internal_flows(self, flow: Type[Flow]):
        """Checks legality of internal flow and adds it to the diagram"""
        pass

    def __add_external_outflows(self, flow: Type[Flow]):
        """Checks legality of outflow and adds it to the diagram"""
        pass

    def __add_external_inflows(self, flow: Type[Flow]):
        """Checks legality of inflow and adds it to the diagram"""
        pass


if __name__ == '__main__':
    sys.exit(1)
