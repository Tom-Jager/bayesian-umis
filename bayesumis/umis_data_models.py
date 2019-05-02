"""
Module containing all the data models for the UMIS diagram, not
mathematical models
"""

import sys
from typing import Dict


class Uncertainty():
    """
    Superclass for representating uncertainty around a stock or flow value.
    Representations must have an expected value to use for display

    Attributes
    ----------
    name (str): Name of distribution
    mean (float): Expected value
    """

    def __init__(
            self,
            name: str,
            mean: float):
        """
        Args
        ----

        name: Name of distribution
        mean: Expected value
        """
        assert isinstance(name, str)
        self.name = name

        mean = float(mean)
        self.mean = mean


class UniformUncertainty(Uncertainty):
    """
    Uncertainty represented by a uniform distribution

    Attributes
    ----------

    lower (float): Lower bound of probability distribution
    upper (float): Upper bound of probability distribution
    """

    def __init__(
            self,
            lower: float,
            upper: float):
        """
        Args
        ----

        lower (float): Lower bound of probability distribution
        upper (float): Upper bound of probability distribution
        """
        lower = float(lower)
        upper = float(upper)
        assert(upper >= lower)
        assert(lower >= 0)
        mean = (upper + lower) / 2
        super(UniformUncertainty, self).__init__("Uniform", mean)
        self.lower = lower
        self.upper = upper


class NormalUncertainty(Uncertainty):
    """
    Uncertainty represented by a normal distribution

    Attributes
    ----------
    mean (float)
    standard_deviation (float)
    """

    def __init__(
            self,
            mean: float,
            standard_deviation: float):
        """
        Args
        ----

        mean (float)
        standard_deviation (float)
        """
        mean = float(mean)
        standard_deviation = float(standard_deviation)

        assert(mean >= 0)

        super(NormalUncertainty, self).__init__("Normal", mean)
        self.standard_deviation = standard_deviation


class LognormalUncertainty(Uncertainty):
    """
    Uncertainty represented by a log-normal distribution

    Attributes
    ----------
    mean (float)
    standard_deviation (float)
    """

    def __init__(
            self,
            mean: float,
            standard_deviation: float):
        """
        Args
        ----

        mean (float)
        standard_deviation (float)
        """
        mean = float(mean)
        standard_deviation = float(standard_deviation)

        assert(mean >= 0)
        super(LognormalUncertainty, self).__init__("Lognormal", mean)
        self.standard_deviation = standard_deviation


class Space():
    """
    Information representing the space/location a value refers to.
    Currently very prototypical and does not reflect the entirety of the data
    stored about a location in STAFDB

    Attributes
    ----------
    stafdb_id (str): Id for the reference space in STAFDB
    name (str): Name of the reference space
    """

    def __init__(
            self,
            stafdb_id: str,
            name: str):
        """
        Args
        ----

        stafdb_id: Id for the reference space in STAFDB
        name: Name of the reference space
        """
        assert isinstance(stafdb_id, str)
        assert isinstance(name, str)

        self.stafdb_id = stafdb_id
        self.name = name

    def __hash__(self):
        return self.stafdb_id.__hash__()


class Material():
    """
    Information representing the material of a STAFDB value

    Attributes
    ----------
    stafdb_id (str): Material ID in STAFDB
    code (str): Material code
    name (str): Material name
    parent_name (str): Name of the aggregation of this material
    is_separator (bool): True if material is an identical disaggregation
    """

    def __init__(
            self,
            stafdb_id: str,
            code: str,
            name: str,
            parent_name: str,
            is_separator: bool):
        """
        Args
        ----

        stafdb_id: Id for the material in STAFDB
        code: Material code
        name: Material name
        parent_name: Name of the aggregation of this material
        is_separator: flag to representing identical disaggregations
        """
        assert isinstance(stafdb_id, str)
        assert isinstance(code, str)
        assert isinstance(name, str)
        assert isinstance(parent_name, str)
        assert isinstance(is_separator, bool)

        self.stafdb_id = stafdb_id
        self.code = code
        self.name = name
        self.parent_name = parent_name
        self.is_separator = is_separator

    def __eq__(self, material_b: 'Material'):
        assert(isinstance(material_b, Material))
        return self.stafdb_id == material_b.stafdb_id

    def __hash__(self):
        return self.stafdb_id.__hash__()


class Timeframe():
    """
    The time frame the stocks and flows are in reference to, we are assuming
    that stocks and flows values are correct at the end of the year

    Attributes
    ----------
    stafdb_id: Id of timeframe in Stafdb
    start_time (int): Start year
    end_time (int): End year
    """

    def __init__(self, stafdb_id: str, start_time: int, end_time: int):
        """
        Args
        ----
        stafdb_id: Id of timeframe in Stafdb
        start_time (int): Start year
        end_time (int): End year
        """
        assert isinstance(stafdb_id, str)
        assert isinstance(start_time, int)
        assert isinstance(end_time, int)

        assert(start_time <= end_time)
        self.stafdb_id = stafdb_id
        self.start_time = start_time
        self.end_time = end_time

    def __eq__(self, timeframe_b: 'Timeframe'):
        assert isinstance(timeframe_b, Timeframe)

        return (self.start_time == timeframe_b.start_time and
                self.end_time == timeframe_b.end_time)


class DiagramReference():
    """
    Class representing the overall attributes a Umis Diagram is in reference to

    Attributes
    ----------

    space (Space): Location umis diagram is in reference to
    time (Timeframe): Year umis diagram is in reference to
    material (Material): Material umis_diagram is in reference to
    """

    def __init__(
            self,
            space: Space = None,
            time: Timeframe = None,
            material: Material = None):
        """
        Args
        ----------

        space (Space): Location umis_diagram is in
            reference to
        time (Timeframe): Year umis_diagram is in reference to
        material (Material): Material umis_diagram is in reference to
        """
        assert not space or isinstance(space, Space)
        assert not time or isinstance(time, Timeframe)
        assert not material or isinstance(material, Material)

        self.space = space
        self.time = time
        self.material = material


class StafReference():
    """
    Class representing the overall attributes a staf is in reference to

    Attributes
    ----------

    time (Timeframe): Year staf is in reference to
    material (Material): Material staf is in reference to
    """

    def __init__(
            self,
            time: Timeframe,
            material: Material):
        """
        Args
        ----------

        time (Timeframe): Year staf is in reference to
        material (Material): Material staf is in reference to
        """
        assert isinstance(time, Timeframe)
        assert isinstance(material, Material)

        self.time = time
        self.material = material


class Value():
    """
    A value for a stock or a flow stored in STAFDB

    Attributes
    ----------
    stafdb_id: Id of timeframe in Stafdb
    quantity (float): Amount of material, if None then the amount is unknown
    uncertainty (Uncertainty): Uncertainty around the value
    unit (str): The unit of the material
    """

    def __init__(
            self,
            stafdb_id: str,
            quantity: float,
            uncertainty: Uncertainty,
            unit: str):
        """
        Args
        ----
        stafdb_id: Id of timeframe in Stafdb
        quantity (float): Amount of material, if None then amount is unknown
        uncertainty (Uncertainty): Uncertainty around the value
        unit (str): The unit of the material
        """
        assert isinstance(stafdb_id, str)
        assert isinstance(uncertainty, Uncertainty)
        assert isinstance(unit, str)

        self.stafdb_id = stafdb_id

        quantity = float(quantity)
        self.quantity = quantity

        self.uncertainty = uncertainty
        self.unit = unit

    def __str__(self):
        value_string = "{} {}".format(self.quantity, self.unit)

        return value_string


class Staf():
    """
    Parent class for stocks and flows

    Attributes
    ----------
    stafdb_id (str): STAFDB id for the stock or flow
    name (str): Name of the stock or flow
    staf_reference (StafReference): Attributes the stock or flow is about
    origin_process (UmisProcess): Process the stock or flow is coming from
    destination_process (UmisProcess): Process the stock or flow is going to
    """

    def __init__(
            self,
            stafdb_id: str,
            name: str,
            staf_reference: StafReference,
            origin_process: 'UmisProcess',
            destination_process: 'UmisProcess'):

        """
        Args
        ----
        stafdb_id (str): STAFDB id for the stock or flow
        name (str): Name of the stock or flow
        staf_reference (StafReference): Attributes the stock or flow is about
        origin_process (UmisProcess): Process the stock or flow is coming from
        destination_process (UmisProcess): Process the stock or flow is going
            to
        """
        assert isinstance(stafdb_id, str)
        assert isinstance(name, str)
        assert isinstance(staf_reference, StafReference)
        assert isinstance(origin_process, UmisProcess)
        assert isinstance(destination_process, UmisProcess)

        self.stafdb_id = stafdb_id
        self.name = name
        self.staf_reference = staf_reference
        self.origin_process = origin_process
        self.destination_process = destination_process

    def __hash__(self):
        return self.stafdb_id.__hash__()

    def __str__(self):
        staf_string = "Staf: {}, ID: {}".format(self.name, self.stafdb_id)
        return staf_string


class Stock(Staf):
    """
    Representation of material stored at a process

    Parent Attributes
    ----------
    stafdb_id (str): STAFDB id for the stock or flow
    name (str): Name of the stock or flow
    staf_reference (StafReference): Attributes the stock or flow is about
    origin_process (UmisProcess): Process material is being stored from
    destination_process (UmisProcess): Process that is storing the stock
    
    Attributes
    ----------
    material_values_dict (dict(Material, Value)): Amount of stock for a given
        material
    """

    def __init__(
            self,
            stafdb_id: str,
            name: str,
            staf_reference: StafReference,
            origin_process: 'UmisProcess',
            destination_process: 'UmisProcess',
            material_values_dict: Dict[Material, 'StockValue']):
        """
        Args
        ----
        stafdb_id (str): STAFDB id for the stock or flow
        name (str): Name of the stock or flow
        staf_reference (StafReference): Attributes the stock or flow is about
        material_values_dict (dict(Material, StockValue)): Amount of stock for
            a given material
        origin_process (UmisProcess): Process material is being stored from
        destination_process (UmisProcess): Process that is storing the stock
        """
        
        assert isinstance(origin_process, UmisProcess)

        assert isinstance(destination_process, UmisProcess)

        assert origin_process.process_type != destination_process.process_type

        super(Stock, self).__init__(
            stafdb_id,
            name,
            staf_reference,
            origin_process,
            destination_process)

        for key, value in material_values_dict.items():
            assert isinstance(key, Material)
            assert isinstance(value, StockValue)

        self.__material_values_dict = material_values_dict

    def get_value(self, material: Material):
        """
        Get value of material stored in stock

        Args
        ----
        material (Material): Material

        Returns
        -------
        None if material is not stored in stock
        Value of material otherwise
        """
        assert isinstance(material, Material)
        value = self.__material_values_dict.get(material)
        assert isinstance(value, StockValue) or value is None
        return value

    def __hash__(self):
        return super(Stock, self).__hash__()

    def __str__(self):
        return super(Stock, self).__str__()


class StockValue(Value):
    """
    Extends value class for stock values as it has a stock type attribute
    
    Attributes
    -----------------
    stafdb_id: Id of timeframe in Stafdb
    quantity (float): Amount of material, if None then the amount is unknown
    uncertainty (Uncertainty): Uncertainty around the value
    unit (str): The unit of the material
    """

    def __init__(
            self,
            stafdb_id: str,
            quantity: float,
            uncertainty: Uncertainty,
            unit: str,
            stock_type: str):
        """
        Args
        ----
        stafdb_id: Id of timeframe in Stafdb
        quantity (float): Amount of material, if None then amount is unknown
        uncertainty (Uncertainty): Uncertainty around the value
        unit (str): The unit of the material
        stock_type (str): The type of stock being stored (net or total)
        """

        super(
            StockValue, self).__init__(stafdb_id, quantity, uncertainty, unit)

        if not (stock_type == 'Total' or stock_type == 'Net'):
            raise ValueError(("Invalid stock type for data with id: {}, "
                             "expected 'Total or 'Net', received {} instead")
                             .format(stafdb_id, stock_type))

        self.stock_type = stock_type


class UmisProcess():
    """
    A process representing either tranformation or distribution of material

    Attributes
    -----------
    diagram_id (str): Unique ID for a process at a space in a Umis diagram
        constructed from process id and space id
    stafdb_id (str): Unique ID for process in STAFDB
    code (str): Unique code for process in STAFDB
    name (str): Process name
    reference_space (Space): Reference space for process
    is_separator (bool): True if process has indentical disaggregation
    parent_name (str): Name of parent process
    process_type (str): Type of process, either Transformation or Distribution
    """

    def __init__(
            self,
            stafdb_id: str,
            code: str,
            name: str,
            reference_space: Space,
            is_separator: bool,
            parent_name: str,
            process_type: str):

        """
        Args
        ----
        diagram_id (str): Unique ID for a process at a space in a Umis diagram
        stafdb_id (str): Unique ID of process in STAFDB
        code (str): Readable Code of process in STAFDB
        name (Process): Process name
        reference_space (Space): Reference space for process
        is_separator (bool): True if process has indentical disaggregation
        parent_name (str): Name of parent process
        process_type (str): Type of process, either 'Transformation' or
            'Distribution'
        """
        assert isinstance(stafdb_id, str)
        assert isinstance(code, str)
        assert isinstance(name, str)
        assert isinstance(reference_space, Space)
        assert isinstance(is_separator, bool)
        assert isinstance(parent_name, str)
        
        self.stafdb_id = stafdb_id
        self.code = code
        self.name = name
        self.reference_space = reference_space
        self.is_separator = is_separator
        self.parent_name = parent_name

        if (process_type != "Transformation"
                and process_type != "Distribution"
                and process_type != "Storage"):
            raise ValueError("Process type is invalid, expected either " +
                             "'Transformation' or 'Distribution': got {} "
                             .format(process_type))

        self.process_type = process_type

        self.__stock_dict = {}

        self.diagram_id = self.create_diagram_id(stafdb_id, reference_space)

    @staticmethod
    def create_diagram_id(process_stafdb_id: str, space: Space):
        """
        Creates diagram id for this process

        Args
        ----
        process_stafdb_id (str):
        space (Space): Space the process is in
        """
        return "{}_{}".format(process_stafdb_id, space.stafdb_id)

    def __eq__(self, process_b):
        return self.diagram_id == process_b.diagram_id

    def __hash__(self):
        return self.diagram_id.__hash__()

    def __str__(self):
        process_string = "Process: {}, STAFDB ID: {}".format(
                            self.name, self.stafdb_id)
        return process_string


class Flow(Staf):
    """
    A flow between transformative and distributive processes

    Parent Attributes
    ----------
    stafdb_id (str): STAFDB id for the stock or flow
    name (str): Name of the stock or flow
    staf_reference (StafReference): Attributes the stock or flow is about
    origin (UmisProcess): The process the flow starts at
    destination (UmisProcess): The process the flow finishes at
    """

    def __init__(
                self,
                stafdb_id: str,
                name: str,
                staf_reference: StafReference,
                origin_process: UmisProcess,
                destination_process: UmisProcess,
                material_values_dict: Dict[Material, Value]):
        """
        Ensures origin and destination process are of differing types

        Args
        ----
        stafdb_id (str): ID for the flow in STAFDB
        name (str): Name of flow
        staf_reference (StafReference): Reference material and time for
            flow
        origin_process (UmisProcess): Process flow starts at
        destination_process (UmisProcess): Process flow finishes at
        material_values_dict (dict(Material, Value)): Amount of stock for a
            given material
        """
        assert ((origin_process.process_type == 'Transformation'
                 and destination_process.process_type == 'Distribution')
                or
                (origin_process.process_type == 'Distribution'
                 and destination_process.process_type == 'Transformation'))

        super(Flow, self).__init__(
            stafdb_id,
            name,
            staf_reference,
            origin_process,
            destination_process)

        assert isinstance(origin_process, UmisProcess)
        assert isinstance(destination_process, UmisProcess)

        for key, value in material_values_dict.items():
            assert isinstance(key, Material)
            assert isinstance(value, Value)

        self.__material_values_dict = material_values_dict

    def get_value(self, material: Material):
        """
        Get value of material stored in flow

        Args
        ----
        material (Material): Material

        Returns
        -------
        None if material is not stored in flow
        Value of material otherwise
        """
        assert isinstance(material, Material)
        value = self.__material_values_dict.get(material)
        assert isinstance(value, Value) or value is None
        return value

    def __str__(self):
        return super(Flow, self).__str__()

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, flow_b):
        return self.stafdb_id == flow_b.stafdb_id


class ProcessOutputs():
    """
    Outflows of a process in a UmisDiagram

    Attributes
    -----------
    flows (set(Flow)): Flows leaving the process
    stock (Stock): Stock of material at this process
    """

    def __init__(self):
        self.flows = set()
        self.stock = None


if __name__ == '__main__':
    sys.exit(1)
