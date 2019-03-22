""" Tests for UmisDiagram """
import unittest
from unittest.mock import Mock

from bayesumis.umis_data_models import (
    Flow,
    Material,
    UmisProcess,
    Reference,
    Space,
    Stock,
    Timeframe,
    TransferCoefficient,
    Uncertainty,
    Value
)
from bayesumis.umis_diagram import UmisDiagram


class TestUmisDiagram(unittest.TestCase):

    def test_add_internal_flow(self):
        process1 = UmisProcess(
            '1', 'Process 1', False, 'parent', 'Transformation')
        process2 = UmisProcess(
            '2', 'Process 1', False, 'parent', 'Distribution')

        material = Material('1', 'WAT', 'Water', 'parent', False)
        space = Space('1', 'Bristol')
        timeframe = Timeframe(2001, 2001)

        value = Value(30, Mock(Uncertainty), 'g', Mock(TransferCoefficient))

        reference = Reference(space, timeframe, material)
        flow = Flow('1', 'Flow 1', reference, value, False, process1, process2)

        umis_diagram = UmisDiagram(
            external_inflows={},
            internal_flows={flow},
            external_outflows={},
            stocks={}
        )

        expected_process_store = {'1': process1, '2': process2}
        expected_process_outflows_dict = {'1': {flow}, '2': set()}

        self.assertEqual(expected_process_store, umis_diagram.process_store)
        self.assertEqual(
            expected_process_outflows_dict, umis_diagram.process_outflows_dict)

    def test_add_external_inflow(self):
        external_process1 = UmisProcess(
            '1',
            'External Process 1',
            False,
            'parent',
            'Transformation')

        process2 = UmisProcess(
            '2', 'Process 1', False, 'parent', 'Distribution')

        material = Material('1', 'WAT', 'Water', 'parent', False)
        space = Space('1', 'Bristol')
        timeframe = Timeframe(2001, 2001)

        value = Value(30, Mock(Uncertainty), 'g', Mock(TransferCoefficient))

        reference = Reference(space, timeframe, material)

        flow = Flow(
            '1',
            'Flow 1',
            reference,
            value,
            False,
            external_process1,
            process2)

        umis_diagram = UmisDiagram(
            external_inflows={flow},
            internal_flows={},
            external_outflows={},
            stocks={}
        )

        expected_process_store = {'2': process2}
        expected_process_outflows_dict = {'2': set()}
        expected_external_inflows = {flow}

        self.assertEqual(expected_process_store, umis_diagram.process_store)
        self.assertEqual(
            expected_process_outflows_dict, umis_diagram.process_outflows_dict)

        self.assertEqual(
            expected_external_inflows, umis_diagram.external_inflows)
        self.assertEqual(reference, umis_diagram.reference)

    def test_add_external_outflow(self):
        process1 = UmisProcess(
            '1',
            'Process 1',
            False,
            'parent',
            'Transformation')

        external_process2 = UmisProcess(
            '2',
            'External Process 2',
            False,
            'parent',
            'Distribution')

        material = Material('1', 'WAT', 'Water', 'parent', False)
        space = Space('1', 'Bristol')
        timeframe = Timeframe(2001, 2001)

        value = Value(30, Mock(Uncertainty), 'g', Mock(TransferCoefficient))

        reference = Reference(space, timeframe, material)

        flow = Flow(
            '1',
            'Flow 1',
            reference,
            value,
            False,
            process1,
            external_process2)

        umis_diagram = UmisDiagram(
            external_inflows={},
            internal_flows={},
            external_outflows={flow},
            stocks={}
        )

        expected_process_store = {'1': process1}
        expected_process_outflows_dict = {'1': {flow}}
        expected_external_outflows = {flow}

        self.assertEqual(expected_process_store, umis_diagram.process_store)
        self.assertEqual(
            expected_process_outflows_dict, umis_diagram.process_outflows_dict)

        self.assertEqual(
            expected_external_outflows, umis_diagram.external_outflows)
        self.assertEqual(reference, umis_diagram.reference)

    def test_add_stock_to_process(self):
        process1 = UmisProcess(
            '1', 'Process 1', False, 'parent', 'Transformation')
        process2 = UmisProcess(
            '2', 'Process 1', False, 'parent', 'Distribution')

        material = Material('1', 'WAT', 'Water', 'parent', False)
        material2 = Material('2', 'WAT', 'Water', 'parent', False)

        space = Space('1', 'Bristol')
        timeframe = Timeframe(2001, 2001)

        value = Value(30, Mock(Uncertainty), 'g', Mock(TransferCoefficient))
        value2 = Value(50, Mock(Uncertainty), 'g', Mock(TransferCoefficient))

        reference = Reference(space, timeframe, material)
        flow = Flow('1', 'Flow 1', reference, value, False, process1, process2)

        reference2 = Reference(space, timeframe, material2)

        stock = Stock(
            '1', 'Stock 1', reference2, {material2: value2}, 'Net', '1')

        umis_diagram = UmisDiagram(
            external_inflows={},
            internal_flows={flow},
            external_outflows={},
            stocks={stock}
        )

        expected_process_store = {'1': process1, '2': process2}
        expected_process_outflows_dict = {'1': {flow}, '2': set()}

        self.assertEqual(expected_process_store, umis_diagram.process_store)
        self.assertEqual(
            expected_process_outflows_dict, umis_diagram.process_outflows_dict)

        self.assertEqual(
            stock, umis_diagram.process_store['1'].get_stock('Net'))
