"""
Module containing all the data models for the UMIS diagram, not
mathematical models
"""

import collections.abc
import sys
from typing import Optional


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


class ReferenceSets():
    """
    Class representing the references represented in the UMIS diagram

    Attributes
    ----------

    reference_spaces (Set(Space)): Locations stock or flow are in reference to
    reference_times (Set(int)): Years stock or flow are in reference to
    reference_materials (Set(Material)): Material stock or flows are in
        reference to
    """

    def __init__(self):

        self.reference_spaces = set()
        self.reference_times = set()
        self.reference_materials = set()

    def add_reference(self, reference: Reference):
        self.reference_spaces.add(reference.space)
        self.reference_materials.add(reference.material)
        self.reference_times.add(reference.time)


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
    quantity (float): Amount of material
    uncertainty (Uncertainty): Uncertainty around the value
    unit (str): The unit of the material
    transfer_coefficient (TransferCoefficient): The transfer
    coefficient for the stock or flow
    """

    def __init__(
            self,
            quantity: float,
            uncertainty: Uncertainty,
            unit: str,
            transfer_coefficient: TransferCoefficient):
        """
        Args
        ----

        quantity (float): Amount of material
        uncertainty (Uncertainty): Uncertainty around the value
        unit (str): The unit of the material
        transfer_coefficient (TransferCoefficient): The transfer
        coefficient for the stock or flow
        """

        self.quantity = quantity
        self.uncertainty = uncertainty
        self.unit = unit
        self.transfer_coefficient = transfer_coefficient

    def __str__(self):
        value_string = "{} {}".format(self.quantity, self.unit)

        return value_string


class Stock():
    """
    Representation of material stored at a process

    Attributes
    ----------

    reference (Reference): Reference attributes for stock
    value (Value): Amount of stock
    """

    def __init__(self, reference: Reference, value: Value):
        """
        Args
        ----

        reference (Reference): Reference attributes for stock
        value (Value): Amount of stock
        """

        self.reference = reference
        self.value = value


class Process(collections.abc.Hashable):
    """
    A process representing either tranformation or distribution of material

    Attributes
    -----------
    uuid (str): Id of process in STAFDB
    name (str): Process name
    is_separator (bool): True if process has indentical disaggregation
    parent_name (str): Name of parent process
    is_transformation (bool): Flag signifying type of process
    stock (Stock): Representation of material stored at this process
    """

    def __init__(
            self,
            uuid: str,
            name: str,
            is_separator: bool,
            parent_name: str,
            is_transformation: bool,
            stock: Optional[Stock] = None):

        """
        Args
        ----

        uuid: Id of process in STAFDB
        name: Process name
        is_separator: True if process has indentical disaggregation
        parent_name: Name of parent process
        is_transformation (bool): Flag signifying type of process
        stock: Representation of material stored at this process
        """

        self.uuid = uuid
        self.name = name
        self.is_separator = is_separator
        self.parent_name = parent_name
        self.is_transformation = is_transformation
        self.stock = stock

    def __eq__(self, process_b):
        return self.uuid == process_b.uuid

    def __hash__(self):
        return self.uuid.__hash__()


class Flow(object):
    """
    A flow between transformative and distributive processes

    Attributes
    ----------
    uuid (str): ID for the flow in STAFDB
    name (str): flow name
    is_separator (bool): True if flow has identical disaggregation
    origin (Process): The process the flow starts at
    destination (Process): The process the flow finishes at
    value (Value): Value of material flowing
    reference (Reference): Reference attributes for flow
    """

    def __init__(
                self,
                uuid: str,
                name: str,
                is_separator: bool,
                origin: Process,
                destination: Process,
                value: Value,
                reference: Reference):
        """
        Ensures origin and destination process are of differing types

        Args
        ----
        uuid: ID for the flow in STAFDB
        name: Name of flow
        is_separator: True if flow has identical disaggregation
        origin: Process flow starts at
        destination: Process flow finishes at
        value: Value of material flowing
        reference (Reference): Reference material, space and time for flow
        """

        self.uuid = uuid
        self.name = name
        self.is_separator = is_separator

        if origin.is_transformation == destination.is_transformation:
            raise ValueError(
                "Origin and Destination process must be of differing process" +
                " types, instead both were {}"
                .format(
                    "transformation"
                    if origin.is_transformation else "distribution"))

        self.origin = origin
        self.destination = destination

        self.value = value
        self.reference = reference

    def __str__(self):
        flow_string = "Flow: {}, ID: {}".format(self.name, self.uuid)
        return flow_string

    def __hash__(self):
        return self.uuid.__hash__()

    def __eq__(self, flow_b):
        return self.uuid == flow_b.uuid


if __name__ == '__main__':
    sys.exit(1)
