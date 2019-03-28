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
    Uncertainty,
    Value
)
from bayesumis.umis_diagram import UmisDiagram


class TestUmisDiagram(unittest.TestCase):

    def test_add_internal_flow(self):

        material = Material('1', 'WAT', 'Water', 'parent', False)
        space = Space('1', 'Bristol')
        timeframe = Timeframe('1', 2001, 2001)

        process1 = UmisProcess(
            '1', 'Proc1', 'Process1', space, False, 'parent', 'Transformation')
        process2 = UmisProcess(
            '2', 'PROC2', 'Process 2', space, False, 'parent', 'Distribution')

        value = Value('1', 30, Mock(Uncertainty), 'g')

        reference = Reference(space, space, timeframe, material)
        flow = Flow('1', 'Flow 1', reference, value, False, process1, process2)

        umis_diagram = UmisDiagram(
            external_inflows={},
            internal_flows={flow},
            external_outflows={},
            stocks={}
        )

        expected_process_store = {'1_1': process1, '2_1': process2}
        expected_process_outflows_dict = {'1_1': {flow}, '2_1': set()}

        self.assertEqual(expected_process_store, umis_diagram.process_store)
        self.assertEqual(
            expected_process_outflows_dict, umis_diagram.process_outflows_dict)

    def test_add_two_processes_different_space(self):
        material = Material('1', 'WAT', 'Water', 'parent', False)
        space1 = Space('1', 'Bristol')
        space2 = Space('2', 'Edinburgh')

        timeframe = Timeframe('1', 2001, 2001)

        process1 = UmisProcess(
            '1', 'Proc1', 'Proces1', space1, False, 'parent', 'Transformation')
        process2 = UmisProcess(
            '1', 'Proc1', 'Proces1', space2, False, 'parent', 'Distribution')

        value = Value('1', 30, Mock(Uncertainty), 'g')

        reference = Reference(space1, space2, timeframe, material)
        flow = Flow('1', 'Flow 1', reference, value, False, process1, process2)

        umis_diagram = UmisDiagram(
            external_inflows={},
            internal_flows={flow},
            external_outflows={},
            stocks={}
        )

        expected_process_store = {'1_1': process1, '1_2': process2}
        expected_process_outflows_dict = {'1_1': {flow}, '1_2': set()}

        self.assertEqual(expected_process_store, umis_diagram.process_store)
        self.assertEqual(
            expected_process_outflows_dict, umis_diagram.process_outflows_dict)

    def test_add_two_internal_flows(self):
        material = Material('1', 'WAT', 'Water', 'parent', False)
        space = Space('1', 'Bristol')
        timeframe = Timeframe('1', 2001, 2001)

        process1 = UmisProcess(
            '1', 'Proc1', 'Process1', space, False, 'parent', 'Transformation')
        process2 = UmisProcess(
            '2', 'PROC2', 'Process 2', space, False, 'parent', 'Distribution')

        value = Value('1', 30, Mock(Uncertainty), 'g')

        reference = Reference(space, space, timeframe, material)
        flow1 = Flow('1', 'Flow1', reference, value, False, process1, process2)
        flow2 = Flow('2', 'Flow2', reference, value, False, process1, process2)

        umis_diagram = UmisDiagram(
            external_inflows={},
            internal_flows={flow1, flow2},
            external_outflows={},
            stocks={}
        )

        expected_process_store = {'1_1': process1, '2_1': process2}
        expected_process_outflows_dict = {'1_1': {flow1, flow2}, '2_1': set()}

        self.assertEqual(expected_process_store, umis_diagram.process_store)
        self.assertEqual(
            expected_process_outflows_dict, umis_diagram.process_outflows_dict)

    def test_add_two_internal_flows_different_processes(self):
        material = Material('1', 'WAT', 'Water', 'parent', False)
        space = Space('1', 'Bristol')
        timeframe = Timeframe('1', 2001, 2001)

        process1 = UmisProcess(
            '1', 'Proc1', 'Process1', space, False, 'parent', 'Transformation')
        process2 = UmisProcess(
            '2', 'PROC2', 'Process 2', space, False, 'parent', 'Distribution')

        value = Value('1', 30, Mock(Uncertainty), 'g')

        reference = Reference(space, space, timeframe, material)
        flow1 = Flow('1', 'Flow1', reference, value, False, process1, process2)
        flow2 = Flow('2', 'Flow2', reference, value, False, process2, process1)

        umis_diagram = UmisDiagram(
            external_inflows={},
            internal_flows={flow1, flow2},
            external_outflows={},
            stocks={}
        )

        expected_process_store = {'1_1': process1, '2_1': process2}
        expected_process_outflows_dict = {'1_1': {flow1}, '2_1': {flow2}}

        self.assertEqual(expected_process_store, umis_diagram.process_store)
        self.assertEqual(
            expected_process_outflows_dict, umis_diagram.process_outflows_dict)

    def test_add_external_inflow(self):
        material = Material('1', 'WAT', 'Water', 'parent', False)
        space = Space('1', 'Bristol')
        timeframe = Timeframe('1', 2001, 2001)

        external_process1 = UmisProcess(
            '1',
            'EXPROC1',
            'External Process 1',
            space,
            False,
            'parent',
            'Transformation')

        process2 = UmisProcess(
            '2', 'PROC2', 'Process 2', space, False, 'parent', 'Distribution')

        value = Value('1', 30, Mock(Uncertainty), 'g')

        reference = Reference(space, space, timeframe, material)

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

        expected_process_store = {'2_1': process2}
        expected_process_outflows_dict = {'2_1': set()}
        expected_external_inflows = {flow}

        self.assertEqual(expected_process_store, umis_diagram.process_store)
        self.assertEqual(
            expected_process_outflows_dict, umis_diagram.process_outflows_dict)

        self.assertEqual(
            expected_external_inflows, umis_diagram.external_inflows)
        self.assertEqual(reference, umis_diagram.reference)

    def test_add_external_outflow(self):
        material = Material('1', 'WAT', 'Water', 'parent', False)
        space = Space('1', 'Bristol')
        timeframe = Timeframe('1', 2001, 2001)

        process1 = UmisProcess(
            '1',
            'PROC1',
            'Process 1',
            space,
            False,
            'parent',
            'Transformation')

        external_process2 = UmisProcess(
            '2',
            'EXPROC2',
            'External Process 2',
            space,
            False,
            'parent',
            'Distribution')

        value = Value('1', 30, Mock(Uncertainty), 'g')

        reference = Reference(space, space, timeframe, material)

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

        expected_process_store = {'1_1': process1}
        expected_process_outflows_dict = {'1_1': {flow}}
        expected_external_outflows = {flow}

        self.assertEqual(expected_process_store, umis_diagram.process_store)
        self.assertEqual(
            expected_process_outflows_dict, umis_diagram.process_outflows_dict)

        self.assertEqual(
            expected_external_outflows, umis_diagram.external_outflows)
        self.assertEqual(reference, umis_diagram.reference)

    def test_add_stock_to_process(self):
        material = Material('1', 'WAT', 'Water', 'parent', False)
        material2 = Material('2', 'WAT', 'Water', 'parent', False)

        space = Space('1', 'Bristol')
        timeframe = Timeframe('1', 2001, 2001)

        process1 = UmisProcess(
            '1', 'Proc1', 'Process 1', space, False, 'parent', 'Transformation')
        process2 = UmisProcess(
            '2', 'PROC2', 'Process 2', space, False, 'parent', 'Distribution')

        value = Value('1', 30, Mock(Uncertainty), 'g')
        value2 = Value('2', 50, Mock(Uncertainty), 'g')

        reference = Reference(space, space, timeframe, material)
        flow = Flow('1', 'Flow 1', reference, value, False, process1, process2)

        reference2 = Reference(space, space, timeframe, material2)

        stock = Stock(
            '1', 'Stock 1', reference2, {material2: value2}, 'Net', '1')

        umis_diagram = UmisDiagram(
            external_inflows={},
            internal_flows={flow},
            external_outflows={},
            stocks={stock}
        )

        expected_process_store = {'1_1': process1, '2_1': process2}
        expected_process_outflows_dict = {'1_1': {flow}, '2_1': set()}

        self.assertEqual(expected_process_store, umis_diagram.process_store)
        self.assertEqual(
            expected_process_outflows_dict, umis_diagram.process_outflows_dict)

        self.assertEqual(
            stock, umis_diagram.process_store['1_1'].get_stock('Net'))

