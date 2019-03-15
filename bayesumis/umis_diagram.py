"""Classes for a graph of processes and flows"""
import collections.abc
import sys
from typing import List, Mapping, Optional, Union


class Uncertainty():
    """ Superclass for representating uncertainty around a stock or flow value.
    Representations must have an expected value to use for display """

    def __init__(
            self,
            name: str,
            mean: float):
        """
        name: Name of distribution
        mean: Expected value
        """
        self.name = name
        self.mean = mean


class UniformUncertainty(Uncertainty):
    """ Uncertainty represented by a uniform distribution """

    def __init__(
            self,
            lower: float,
            upper: float):

        assert(upper > lower)
        assert(lower >= 0)

        self.lower = lower
        self.upper = upper

        mean = (upper + lower) / 2
        super().__init__("Uniform", mean)


class NormalUncertainty(Uncertainty):
    """ Uncertainty represented by a normal distribution """

    def __init__(
            self,
            mean: float,
            standard_deviation: float):

        assert(mean >= 0)

        self.standard_deviation = standard_deviation
        super().__init__("Normal", mean)


class LogNormalUncertainty(Uncertainty):
    """ Uncertainty represented by a log-normal distribution """

    def __init__(
            self,
            mean: float,
            standard_deviation: float):

        assert(mean >= 0)

        self.standard_deviation = standard_deviation
        super().__init__("Log-Normal", mean)


class Space():
    """ Information representing the space/location a value refers to.
    Currently very prototypical and does not reflect the entirety of the data
    stored about a location in STAFDB"""

    def __init__(
                self,
                uuid: str,
                name: str):

        self.uuid = uuid
        self.name = name


class Value():
    """ A value for a stock or a flow stored in STAFDB """

    def __init__(
            self,
            quantity: float,
            unit: str,
            uncertainty: Uncertainty,
            space: Space):

        self.quantity = quantity
        self.unit = unit
        self.uncertainty = uncertainty
        self.space = space


class TransformationProcess(collections.abc.Hashable):
    """ A transformation process """

    def __init__(
            self,
            uuid: str,
            name: str,
            is_separator: bool,
            parent_id: str,
            stock: Optional[Value] = None):

        """Constructs a transformation process object"""
        self.uuid = uuid
        self.name = name
        self.is_separator = is_separator
        self.parent_id = parent_id
        self.stock = stock

    def __eq__(self, process_b):
        return self.uuid == process_b.uuid

    def __hash__(self):
        return self.uuid.__hash__()


class DistributionProcess(collections.abc.Hashable):
    """ A distribution process """

    def __init__(
            self,
            uuid: str,
            name: str,
            is_separator: bool,
            parent_id: str):
        """ Creates a distribution process """
        self.uuid = uuid
        self.name = name
        self.is_separator = is_separator
        self.parent_id = parent_id

    def __eq__(self, process_b):
        return self.uuid == process_b.uuid

    def __hash__(self):
        return self.uuid.__hash__()


Process = Union[TransformationProcess, DistributionProcess]


class Flow(object):
    """A flow between transformative and distributive processes"""
    def __init__(
                self,
                origin: Process,
                destination: Process,
                value: float):
        """Represents the flow of stock from one process to another origin
        must be of a different process type than destination"""
        pass


class UmisDiagram(object):
    """Representation of a UMIS diagram, serves to add new processes and
    flows whilst ensuring that they are legal."""

    def __init__(
                self,
                processes: List[Process],
                external_inflows: List[Flow],
                internal_flows: List[Flow],
                external_outflows: List[Flow]):
        """Initializes a diagram from its components and ensures that it is valid
        within UMIS definitions

        processes: List of all processes for this UMIS diagram
        external_inflows: List of flows into processes from outside the diagram
        internal_flows: List of flows between processes in the diagram
        external_outflows: List of flows from processes to outside the diagram
        """

        self.process_outflows_dict: Mapping[Process, List[Flow]] = {}
        """Mapping from processes to their outflows, must be a dictionary"""

        try:
            self.__add_processes(processes)
        except Exception as err:
            raise Exception(err)

        try:
            self.__add_internal_flows(internal_flows)
        except Exception as err:
            raise Exception(err)

        try:
            self.__add_external_inflows(external_inflows)
        except Exception as err:
            raise Exception(err)

        try:
            self.__add_external_outflows(external_outflows)
        except Exception as err:
            raise Exception(err)

        self.__check_fully_connected()

    def __add_processes(self, processes: list):
        """Adds processes to dict with validation"""

        if len(processes) < 2:
            raise ValueError("Must add at least 2 processes")

        process_types = [self.__add_process(p) for p in processes]

        number_of_t_processes = process_types.count('T')
        number_of_d_processes = process_types.count('D')

        if number_of_d_processes != number_of_t_processes:
            raise ValueError(
                "Graph must have equal number of transformation and" +
                "distriubtion processes")

        return

    def __add_process(self, process):
        """Adds a new process to the diagram, returns 'T' if the process
        is a transformation process and 'D' if it is distribution"""

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
                raise TypeError(
                    "process is of type {}:".format(type(process)) +
                    " TransformationProcess or DistributionProcess expected")

        self.process_outflows_dict[process] = []

        return process_type

    def __add_internal_flows(self, flow: Flow):
        """ Checks legality of internal flow and adds it to the diagram """
        
        pass

    def __add_external_outflows(self, flow: Flow):
        """Checks legality of outflow and adds it to the diagram"""
        pass

    def __add_external_inflows(self, flow: Flow):
        """Checks legality of inflow and adds it to the diagram"""
        pass

    def __check_fully_connected(self):
        """ Ensures that the resultant diagram is a fully connected set of
        processes """
        pass


if __name__ == '__main__':
    sys.exit(1)
