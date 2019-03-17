"""
Module containing all the data models for the UMIS diagram, not
mathematical models
"""

import collections.abc
import sys
from typing import Optional, Union


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
    material (Material): Material
    space (Space): The location the value is referring to
    time (int): The year the value is referring to
    """

    def __init__(
            self,
            quantity: float,
            uncertainty: Uncertainty,
            unit: str,
            transfer_coefficient: TransferCoefficient,
            material: Material,
            space: Space,
            time: int):
        """
        Args
        ----

        quantity (float): Amount of material
        uncertainty (Uncertainty): Uncertainty around the value
        unit (str): The unit of the material
        transfer_coefficient (TransferCoefficient): The transfer
        coefficient for the stock or flow
        material (Material): Material
        space (Space): The location the value is referring to
        time (int): The year the value is referring to
        """
        if quantity < 0:
            raise ValueError(
                "Can only have stocks or flows greater than or equal to 0," +
                "quantity was {}".format(quantity))

        self.quantity = quantity
        self.uncertainty = uncertainty
        self.unit = unit
        self.transfer_coefficient = transfer_coefficient
        self.material = material
        self.space = space
        self.time = time

    def __str__(self):
        value_string = "Material: {}, Space: {}, Time: {}".format(
            self.material.name,
            self.space.name,
            self.time)

        return value_string


class TransformationProcess(collections.abc.Hashable):
    """
    A process representation transformation of material

    Attributes
    -----------
    uuid (str): Id of process in STAFDB
    name (str): Process name
    is_separator (bool): True if process has indentical disaggregation
    parent_name (str): Name of parent process
    stock (str): Representation of material stored at this process
    """

    def __init__(
            self,
            uuid: str,
            name: str,
            is_separator: bool,
            parent_name: str,
            stock: Optional[Value] = None):

        """
        Args
        ----

        uuid: Id of process in STAFDB
        name: Process name
        is_separator: True if process has indentical disaggregation
        parent_name: Name of parent process
        stock: Representation of material stored at this process
        """

        self.uuid = uuid
        self.name = name
        self.is_separator = is_separator
        self.parent_name = parent_name
        self.stock = stock

    def __eq__(self, process_b):
        return self.uuid == process_b.uuid

    def __hash__(self):
        return self.uuid.__hash__()


class DistributionProcess(collections.abc.Hashable):
    """
    A distribution process representation distribution of stock to other
    processes

    Attributes
    ----------
    uuid (str): Id of process in STAFDB
    is_separator (bool): True if process has indentical disaggregation
    name (str): Process name
    parent_name (str): Name of parent process
    """

    def __init__(
            self,
            uuid: str,
            is_separator: bool,
            name: str,
            parent_name: str):
        """
        Args
        ----

        uuid: Id of process in STAFDB
        is_separator: True if process has indentical disaggregation
        name: Process name
        parent_name: Name of parent process
        """

        self.uuid = uuid
        self.name = name
        self.is_separator = is_separator
        self.parent_name = parent_name

    def __eq__(self, process_b):
        return self.uuid == process_b.uuid

    def __hash__(self):
        return self.uuid.__hash__()


Process = Union[TransformationProcess, DistributionProcess]


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
    """

    def __init__(
                self,
                uuid: str,
                name: str,
                is_separator: bool,
                origin: Process,
                destination: Process,
                value: Value,
                ):
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
        """
        self.uuid = uuid
        self.name = name
        self.is_separator = is_separator

        if not ((isinstance(origin, TransformationProcess) and
                isinstance(destination, DistributionProcess))
                or
                (isinstance(origin, DistributionProcess) and
                    isinstance(destination, TransformationProcess))):
            raise TypeError(
                "Origin and Destination process must be of differing process" +
                " types, instead were {} and {}"
                .format(type(origin), type(destination)))

        self.origin = origin
        self.destination = destination

        self.value = value

    def __str__(self):
        flow_string = "Flow: {}, ID: {}".format(self.name, self.uuid)
        return flow_string

    def __hash__(self):
        return self.uuid.__hash__()

    def __eq__(self, flow_b):
        return self.uuid == flow_b.uuid


if __name__ == '__main__':
    sys.exit(1)
