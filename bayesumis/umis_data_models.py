"""
Module containing all the data models for the UMIS diagram, not
mathematical models
"""

import sys
from typing import Optional, Dict


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


class Reference():
    """
    Class representing the attributes a stock or flow is in reference to

    Attributes
    ----------

    origin_space (Space): Location start of stock or flow is in reference to
    destination_space (Space): Location end of stock or flow is in reference to
    time (Timeframe): Year stock or flow is in reference to
    material (Material): Material stock or flow is in reference to
    """

    def __init__(
            self,
            origin_space: Space,
            destination_space: Space,
            time: Timeframe,
            material: Material):
        """
        Args
        ----------

        origin_space (Space): Location start of stock or flow is in reference
            to
        destination_space (Space): Location end of stock or flow is in
            reference to
        time (Timeframe): Year stock or flow is in reference to
        material (Material): Material stock or flow is in reference to
        """
        assert isinstance(origin_space, Space)
        assert isinstance(destination_space, Space)
        assert isinstance(time, Timeframe)
        assert isinstance(material, Material)

        self.origin_space = origin_space
        self.destination_space = destination_space
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
    reference (Reference): Attributes the stock or flow is about
    """

    def __init__(
            self,
            stafdb_id: str,
            name: str,
            reference: Reference,
            material_values_dict: Dict[Material, Value]):

        """
        Args
        ----
        stafdb_id (str): STAFDB id for the stock or flow
        name (str): Name of the stock or flow
        reference (Reference): Attributes the stock or flow is about
        material_values_dict (dict(Material, Value)): Amount of stock for a
            given material
        """
        assert isinstance(stafdb_id, str)
        assert isinstance(name, str)
        assert isinstance(reference, Reference)

        self.stafdb_id = stafdb_id
        self.name = name
        self.reference = reference

        for key, value in material_values_dict.items():
            assert isinstance(key, Material)
            assert isinstance(value, Value)

        self.__material_values_dict = material_values_dict

    def get_value(self, material: Material):
        """
        Get value of material stored at stock or flow

        Args
        ----
        material (Material): Material

        Returns
        -------
        None if material is not stored at stock or flow
        Value of material otherwise
        """
        assert isinstance(material, Material)
        value = self.__material_values_dict.get(material)
        assert isinstance(value, Value) or value is None
        return value


class Stock(Staf):
    """
    Representation of material stored at a process

    Parent Attributes
    ----------
    stafdb_id (str): STAFDB id for the stock or flow
    name (str): Name of the stock or flow
    reference (Reference): Attributes the stock or flow is about
    material_values_dict (dict(Material, Value)): Amount of stock for a given
        material

    Attributes
    ----------
    stock_type (str): Whether the stock represents net or total stock
    process_stafdb_id (str): Id of the process the stock is storing material
        from
    """

    def __init__(
            self,
            stafdb_id: str,
            name: str,
            reference: Reference,
            material_values_dict: Dict[Material, Value],
            stock_type: str,
            process_stafdb_id: str):
        """
        Args
        ----
        stafdb_id (str): STAFDB id for the stock or flow
        reference (Reference): Attributes the stock or flow is about
        name (str): Name of the stock or flow
        stock_type (str): Whether the stock represents net or total stock
        process_stafdb_id (str): Id of the process the stock is storing
            material from
        material_values_dict (dict(Material, Value)): Amount of stock for a
            given material
        """

        super(
            Stock,
            self).__init__(stafdb_id, name, reference, material_values_dict)

        assert stock_type == 'Net' or stock_type == 'Total'
        self.stock_type = stock_type

        assert isinstance(process_stafdb_id, str)
        self.process_stafdb_id = process_stafdb_id

    def get_stock_process_diagram_id(self):
        """
        Returns the process this stock is on's diagram id
        """
        return UmisProcess.create_diagram_id(self.process_stafdb_id)


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
    space (Space): Reference space for process
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

        if process_type != "Transformation" and process_type != "Distribution":
            raise ValueError("Process type is invalid, expected either " +
                             "'Transformation' or 'Distribution': got {} "
                             .format(process_type))

        self.process_type = process_type

        self.__stock_dict = {}

        self.diagram_id = self.create_diagram_id(stafdb_id, reference_space)

    def add_stock(self, stock: Stock):
        """
        Add a stock to the process representing a storage process

        Args
        ----

        stock (Stock): Stock to be added
        """

        assert isinstance(stock, Stock)
        self.__stock_dict[stock.stock_type] = stock

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

    def get_stock(self, stock_type: str):
        """
        Get stock of given type from process

        Args
        ----
        stock_type (str): Must be either 'Net' or 'Total'

        Returns
        -------
        stock (Stock): Stock in storage process if it exists
        None: Returns None if the stock of that type does not exist
        """
        if stock_type != 'Net' and stock_type != 'Total':
            raise ValueError("Incorrect stock type submitted, expected 'Net'" +
                             "or 'Total', recieved {}".format(stock_type))

        stock = self.__stock_dict.get(stock_type)
        assert isinstance(stock, Stock) or stock is None
        return stock

    def __eq__(self, process_b):
        return self.diagram_id == process_b.diagram_id

    def __hash__(self):
        return self.diagram_id.__hash__()


class Flow(Staf):
    """
    A flow between transformative and distributive processes

    Parent Attributes
    ----------
    stafdb_id (str): STAFDB id for the stock or flow
    name (str): Name of the stock or flow
    reference (Reference): Attributes the stock or flow is about
    material_values_dict (dict(Material, Value)): Amount of stock for a
            given material

    Attributes
    ----------
    origin (UmisProcess): The process the flow starts at
    destination (UmisProcess): The process the flow finishes at
    """

    def __init__(
                self,
                stafdb_id: str,
                name: str,
                reference: Reference,
                material_values_dict: Dict[Material, Value],
                origin: UmisProcess,
                destination: UmisProcess):
        """
        Ensures origin and destination process are of differing types

        Args
        ----
        stafdb_id: ID for the flow in STAFDB
        name: Name of flow
        reference (Reference): Reference material, space and time for flow
        material_values_dict (dict(Material, Value)): Amount of stock for a
            given material
        origin: Process flow starts at
        destination: Process flow finishes at
        """
        if origin == destination:
            raise ValueError("Origin and destination process must be of" +
                             "different types")

        if origin.process_type == destination.process_type:
            raise ValueError(
                "Origin and Destination process must be of differing process" +
                " types, instead origin: {} and destination: {}"
                .format(
                    origin.is_transformation,
                    destination.is_transformation))

        super(
            Flow,
            self).__init__(stafdb_id, name, reference, material_values_dict)
        
        assert isinstance(origin, UmisProcess)
        assert isinstance(destination, UmisProcess)

        self.origin = origin
        self.destination = destination

    def __str__(self):
        flow_string = "Flow: {}, ID: {}".format(self.name, self.stafdb_id)
        return flow_string

    def __hash__(self):
        return self.stafdb_id.__hash__()

    def __eq__(self, flow_b):
        return self.stafdb_id == flow_b.stafdb_id


if __name__ == '__main__':
    sys.exit(1)
