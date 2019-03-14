"""Classes for a graph of processes and flows"""
import collections
import sys


class UmisDiagram(object):
    """Representation of a UMIS diagram as a serves to add new processes and
    flows whilst ensuring that they are legal."""

    def __init__(self, processes, flows=[]):
        """Initializes a diagram with an empty, dictionary entry
        must be in the form Process : Flows"""
        assert len(processes) >= 2

        self.process_dict = {}

        map(self.add_process, processes)
        map(self.add_flow, flows)

    def add_process(self, process):
        """Adds a new process to the diagram"""
        if process in self.process_dict:
            raise ValueError("""Process {process.name} is
            already in the diagram""")

        self.process_dict[process] = []

    def add_flow(self, flow):
        """Checks legality of flow and adds it to the diagram"""
        pass

    def flows(self):
        """Return a list of pairs of nodes representing flows in the UMIS
        diagram"""
        pass
    
    def processes(self):
        """Return a list of nodes representing processes in the UMIS diagram"""
        pass


class TransformationProcess(collections.Hashable):
    """A node in the bipartite directed graph representing a
    transformation process"""
    
    def __init__(
            self,
            uuid: str,
            name: str,
            is_separator: bool,
            parent_id: str) -> collections.Hashable:

        """Constructs a transformation process object"""
        assert isinstance(uuid, collections.Hashable)
        self.uuid = uuid
        self.name = name
        self.is_separator = is_separator
        self.parent_id = parent_id

    def __eq__(self, process_b):
        return self.uuid == process_b.uuid

    def __hash__(self):
        return self.uuid.__hash__()

    def add_outflow(self, flow):
        return 

class DistributionProcess(collecitons.Hashable):
    """A node in the bipartite directed graph representing a
    transformation process"""



class Flow(object):
    """A flow between transformative and distributive processes"""
    def __init__(self,
                 origin: Process,
                 destination: Process,
                 value: float
                 ):
        """Represents the flow of stock from one process to another"""
        
        pass


if __name__ == '__main__':
    sys.exit(1)
