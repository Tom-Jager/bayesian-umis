"""
Module containing all the data models for the UMIS diagram, not
mathematical models
"""

import collections.abc
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
        self.name = name
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
        assert(upper > lower)
        assert(lower >= 0)

        self.lower = lower
        self.upper = upper

        mean = (upper + lower) / 2
        super().__init__("Uniform", mean)


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

        assert(mean >= 0)

        self.standard_deviation = standard_deviation
        super().__init__("Normal", mean)


class LogNormalUncertainty(Uncertainty):
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

        assert(mean >= 0)

        self.standard_deviation = standard_deviation
        super().__init__("Log-Normal", mean)


class Space():
    """
    Information representing the space/location a value refers to.
    Currently very prototypical and does not reflect the entirety of the data
    stored about a location in STAFDB

    Attributes
    ----------
    uuid (str): Id for the reference space in STAFDB
    name (str): Name of the reference space
    """

    def __init__(
            self,
            uuid: str,
            name: str):
        """
        Args
        ----

        uuid: Id for the reference space in STAFDB
        name: Name of the reference space
        """

        self.uuid = uuid
        self.name = name

    def __hash__(self):
        return self.uuid.__hash__()


class Material():
    """
    Information representing the material of a STAFDB value

    Attributes
    ----------
    uuid (str): Id for the material in STAFDB
    code (str): Material code
    name (str): Material name
    parent_name (str): Name of the aggregation of this material
    is_separator (bool): True if material is an identical disaggregation
    """

    def __init__(
            self,
            uuid: str,
            code: str,
            name: str,
            parent_name: Optional[str],
            is_separator: bool):
        """
        Args
        ----

        uuid: Id for the material in STAFDB
        code: Material code
        name: Material name
        parent_name: Name of the aggregation of this material
        is_separator: flag to representing identical disaggregations
        """

        self.uuid = uuid
        self.code = code
        self.name = name
        self.parent_name = parent_name
        self.is_separator = is_separator

    def __eq__(self, material_b):
        assert(isinstance(material_b, Material))
        return self.uuid == material_b.uuid

    def __hash__(self):
        return self.uuid.__hash__()


class Timeframe():
    """
    The time frame the stocks and flows are in reference to, we are assuming
    that stocks and flows values are correct at the end of the year

    Attributes
    ----------

    start_time (int): Start year
    end_time (int): End year
    """

    def __init__(self, start_time: int, end_time: int):
        """
        Args
        ----
        start_time (int): Start year
        end_time (int): End year
        """

        assert(start_time <= end_time)
        self.start_time = start_time
        self.end_time = end_time


class Reference():
    """
    Class representing the attributes a stock or flow is in reference to

    Attributes
    ----------

    space (Space): Location stock or flow is in reference to
    time (int): Year stock or flow is in reference to
    material (Material): Material stock or flow is in reference to
    """

    def __init__(self, space: Space, time: int, material: Material):
        """
        Args
        ----------

        space (Space): Location stock or flow is in reference to
        time (int): Year stock or flow is in reference to
        material (Material): Material stock or flow is in reference to
        """

        self.space = space
        self.time = time
        self.material = material


class TransferCoefficient():
    """
    Transfer coefficient representing the proportion of the input to
    the process appropriated by this value

    Attributes
    ----------

    coefficient (float): Coefficient value
    uncertainty (Uncertainty): Uncertainty of coefficient value
    """

    def __init__(
            self,
            transfer_coefficient: float,
            uncertainty: Uncertainty):
        """
        Args
        ----

        coefficient (float): Coefficient value
        uncertainty (Uncertainty): Uncertainty of coefficient value
        """

        if transfer_coefficient < 0 or transfer_coefficient > 1:
            raise ValueError(
                "Transfer coefficient must be between 0 and 1, was {}"
                .format(transfer_coefficient))

        self.transfer_coefficient = transfer_coefficient
        self.uncertainty = uncertainty


class Value():
    """
    A value for a stock or a flow stored in STAFDB

    Attributes
    ----------
    quantity (float): Amount of material, if None then the amount is unknown
    uncertainty (Uncertainty): Uncertainty around the value
    unit (str): The unit of the material
    transfer_coefficient (TransferCoefficient): The transfer
        coefficient for the stock or flow, if None then the amount is unknown
    """

    def __init__(
            self,
            quantity: float,
            uncertainty: Uncertainty,
            unit: str,
            transfer_coefficient: Optional[TransferCoefficient]):
        """
        Args
        ----

        quantity (float): Amount of material, if None then amount is unknown
        uncertainty (Uncertainty): Uncertainty around the value
        unit (str): The unit of the material
        transfer_coefficient (TransferCoefficient): The transfer
            coefficient for the stock or flow, if None then the coefficient
            is unknown
        """

        self.quantity = quantity
        self.uncertainty = uncertainty
        self.unit = unit
        self.transfer_coefficient = transfer_coefficient

    def __str__(self):
        value_string = "{} {}".format(self.quantity, self.unit)

        return value_string


class Staf():
    """
    Parent class for stocks and flows

    Attributes
    ----------
    uuid (str): STAFDB id for the stock or flow
    name (str): Name of the stock or flow
    reference (Reference): Attributes the stock or flow is about
    """

    def __init__(
            self,
            uuid: str,
            name: str,
            reference: Reference,
            material_values_dict: Dict[Material, Value]):

        """
        Args
        ----
        uuid (str): STAFDB id for the stock or flow
        name (str): Name of the stock or flow
        reference (Reference): Attributes the stock or flow is about
        material_values_dict (dict(Material, Value)): Amount of stock for a
            given material
        """

        self.uuid = uuid
        self.name = name
        self.reference = reference
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
        return self.__material_values_dict[material]


class Stock(Staf):
    """
    Representation of material stored at a process

    Parent Attributes
    ----------
    uuid (str): STAFDB id for the stock or flow
    name (str): Name of the stock or flow
    reference (Reference): Attributes the stock or flow is about
    material_values_dict (dict(Material, Value)): Amount of stock for a given
        material

    Attributes
    ----------
    stock_type (str): Whether the stock represents net or total stock
    process (Process): Process the stock is storing material from
    """

    def __init__(
            self,
            uuid: str,
            name: str,
            reference: Reference,
            material_values_dict: Dict[Material, Value],
            stock_type: str,
            process: 'Process'):
        """
        Args
        ----
        uuid (str): STAFDB id for the stock or flow
        name (str): Name of the stock or flow
        reference (Reference): Attributes the stock or flow is about
        stock_type (str): Whether the stock represents net or total stock
        process (Process): Process the stock is storing material from
        material_values_dict (dict(Material, Value)): Amount of stock for a
            given material
        """

        super().__init__(uuid, name, reference, material_values_dict)
        self.stock_type = stock_type
        self.process = process


class Process(collections.abc.Hashable):
    """
    A process representing either tranformation or distribution of material

    Attributes
    -----------
    uuid (str): Id of process in STAFDB
    name (str): Process name
    is_separator (bool): True if process has indentical disaggregation
    parent_name (str): Name of parent process
    process_type (str): Type of process, either Transformation or Distribution
    """

    def __init__(
            self,
            uuid: str,
            name: str,
            is_separator: bool,
            parent_name: str,
            process_type: str):

        """
        Args
        ----

        uuid (str): Id of process in STAFDB
        name (Process): Process name
        is_separator (bool): True if process has indentical disaggregation
        parent_name (str): Name of parent process
        process_type (str): Type of process, either 'Transformation' or
            'Distribution'
        """

        if process_type != "Transformation" or process_type != "Distribution":
            raise ValueError("Process type is invalid, expected either " +
                             "'Transformation' or 'Distribution': got {} "
                             .format(process_type))

        self.uuid = uuid
        self.name = name
        self.is_separator = is_separator
        self.parent_name = parent_name
        self.process_type = process_type
        self.__stock_dict = {}

    def add_stock(self, stock: Stock):
        """
        Add a stock to the process representing a storage process

        Args
        ----

        stock (Stock): Stock to be added
        """

        assert isinstance(stock, Stock)
        self.__stock_dict[stock.stock_type] = stock

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
        if stock_type != 'Net' or stock_type != 'Total':
            raise ValueError("Incorrect stock type submitted, expected 'Net'" +
                             "or 'Total', recieved {}".format(stock_type))

        return self.__stock_dict[stock_type]

    def __eq__(self, process_b):
        return self.uuid == process_b.uuid

    def __hash__(self):
        return self.uuid.__hash__()


class Flow(Staf):
    """
    A flow between transformative and distributive processes

    Parent Attributes
    ----------
    uuid (str): STAFDB id for the stock or flow
    name (str): Name of the stock or flow
    reference (Reference): Attributes the stock or flow is about
    material_values_dict (dict(Material, Value)): Amount of stock for a
            given material

    Attributes
    ----------
    is_separator (bool): True if flow has identical disaggregation
    origin (Process): The process the flow starts at
    destination (Process): The process the flow finishes at
    """

    def __init__(
                self,
                uuid: str,
                name: str,
                reference: Reference,
                material_values_dict: Dict[Material, Value],
                is_separator: bool,
                origin: Process,
                destination: Process):
        """
        Ensures origin and destination process are of differing types

        Args
        ----
        uuid: ID for the flow in STAFDB
        name: Name of flow
        reference (Reference): Reference material, space and time for flow
        material_values_dict (dict(Material, Value)): Amount of stock for a
            given material
        is_separator: True if flow has identical disaggregation
        origin: Process flow starts at
        destination: Process flow finishes at
        """

        if origin.process_type == destination.process_type:
            raise ValueError(
                "Origin and Destination process must be of differing process" +
                " types, instead origin: {} and destination: {}"
                .format(
                    origin.is_transformation,
                    destination.is_transformation))

        super().__init__(uuid, name, reference, material_values_dict)
        self.is_separator = is_separator

        self.origin = origin
        self.destination = destination

    def __str__(self):
        flow_string = "Flow: {}, ID: {}".format(self.name, self.uuid)
        return flow_string

    def __hash__(self):
        return self.uuid.__hash__()

    def __eq__(self, flow_b):
        return self.uuid == flow_b.uuid


if __name__ == '__main__':
    sys.exit(1)
