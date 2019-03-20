"""Tests for UmisDiagram, Processes and Flows classes """

import unittest
from unittest.mock import Mock

from bayesumis.umis_data_models import (
    Flow,
    Material,
    Process,
    Reference,
    Space,
    Stock,
    TransferCoefficient,
    Uncertainty,
    Value)

from bayesumis.umis_diagram import UmisDiagram


class TestUmisDiagramAddProcesses(unittest.TestCase):

    def test_cannot_add_less_than_2_processes(self):

        process1 = Process('1', 'Process 1', False, 'parent', True)
        processes = [process1]

        self.assertRaises(
            Exception,
            lambda ps: UmisDiagram(ps, [], [], []),
            processes)

    def test_cannot_add_unbalanced_type_of_processes(self):

        process1 = Process('1', 'Process 1', False, 'parent', True)
        process2 = Process('2', 'Process 2', False, 'parent', False)
        process3 = Process('3', 'Process 3', False, 'parent', True)
        process4 = Process('4', 'Process 4', False, 'parent', True)

        processes = [process1, process2, process3, process4]

        self.assertRaises(
            Exception,
            lambda ps: UmisDiagram(ps, [], [], []),
            processes)

    def test_add_2_processes(self):

        process1 = Process('1', 'Process 1', False, 'parent', True)
        process2 = Process('2', 'Process 2', False, 'parent', False)

        processes = [process1, process2]

        umis_diagram = UmisDiagram(
            processes,
            [],
            [],
            [])

        expected_dict = {
            process1: set(),
            process2: set()
        }

        self.assertEqual(umis_diagram.process_outflows_dict, expected_dict)

    def test_add_not_a_process_raises_exception(self):

        process1 = Process('1', 'Process 1', False, 'parent', True)
        process2 = 5

        processes = [process1, process2]

        self.assertRaises(
            Exception,
            lambda ps: UmisDiagram(ps, [], [], []),
            processes)

    def test_add_stock_adds_to_reference_set(self):
        reference_material = Material('1', 'AIR', 'air', None, False)
        reference_time = 2001
        reference_space = Space('1', 'Bristol')

        reference1 = Reference(
            reference_space,
            reference_time,
            reference_material
        )

        new_material = Material('2', 'WAT', 'water', None, False)
        new_time = 2002
        new_space = Space('2', 'Edinburgh')

        reference2 = Reference(
            new_space,
            new_time,
            new_material
        )

        stock1 = Stock(reference1, Mock(Value))
        stock2 = Stock(reference2, Mock(Value))

        process1 = Process('1', 'Process 1', False, 'parent', True, stock1)
        process2 = Process('2', 'Process 2', False, 'parent', False, stock2)

        processes = [process1, process2]

        expected_time_reference_set = {reference_time, new_time}
        expected_space_reference_set = {reference_space, new_space}
        expected_material_reference_set = {reference_material, new_material}

        umis_diagram = UmisDiagram(processes, [], [], [])

        self.assertEqual(
            expected_material_reference_set,
            umis_diagram.reference_sets.reference_materials)

        self.assertEqual(
            expected_time_reference_set,
            umis_diagram.reference_sets.reference_times)

        self.assertEqual(
            expected_space_reference_set,
            umis_diagram.reference_sets.reference_spaces)

    def test_add_same_type_stock_twice_adds_once_to_reference_set(self):
        reference_material = Material('1', 'AIR', 'air', None, False)
        reference_time = 2001
        reference_space = Space('1', 'Bristol')

        reference1 = Reference(
            reference_space,
            reference_time,
            reference_material
        )

        new_material = Material('2', 'WAT', 'water', None, False)
        new_time = 2002
        new_space = Space('2', 'Edinburgh')

        reference2 = Reference(
            new_space,
            new_time,
            new_material
        )

        stock1 = Stock(reference1, Mock(Value))
        stock2 = Stock(reference2, Mock(Value))

        process1 = Process('1', 'Process 1', False, 'parent', True, stock1)
        process2 = Process('2', 'Process 2', False, 'parent', False, stock2)
        process3 = Process('3', 'Process 3', False, 'parent', True, stock1)
        process4 = Process('4', 'Process 4', False, 'parent', False, stock2)

        processes = [process1, process2, process3, process4]

        expected_time_reference_set = {reference_time, new_time}
        expected_space_reference_set = {reference_space, new_space}
        expected_material_reference_set = {reference_material, new_material}

        umis_diagram = UmisDiagram(processes, [], [], [])

        self.assertEqual(
            expected_material_reference_set,
            umis_diagram.reference_sets.reference_materials)

        self.assertEqual(
            expected_time_reference_set,
            umis_diagram.reference_sets.reference_times)

        self.assertEqual(
            expected_space_reference_set,
            umis_diagram.reference_sets.reference_spaces)


class TestAddInternalFlows(unittest.TestCase):
    def test_add_internal_flow_when_origin_not_in_diagram_raises_ex(self):
        process1 = Process('1', 'Process 1', False, 'parent', True)
        process2 = Process('2', 'Process 2', False, 'parent', False)
        fake_process = Process('3', 'Process 3', False, 'parent', True)

        mock_value = Mock(spec=Value)
        processes = [process1, process2]

        flow = Flow(
            '1',
            'Internal Flow 1',
            False,
            fake_process,
            process2,
            mock_value,
            Mock(Reference))

        internal_flows = [flow]

        self.assertRaises(
            Exception,
            lambda i_fs: UmisDiagram(
                processes,
                [],
                i_fs,
                []),
            internal_flows)

    def test_add_internal_flow_when_destination_not_in_diagram_raises_ex(self):
        process1 = Process('1', 'Process 1', False, 'parent', True)
        process2 = Process('2', 'Process 2', False, 'parent', False)
        fake_process = Process('3', 'Process 3', False, 'parent', True)

        mock_value = Mock(spec=Value)
        processes = [process1, process2]

        flow = Flow(
            '1',
            'Internal Flow 1',
            False,
            process2,
            fake_process,
            mock_value,
            Mock(Reference))

        internal_flows = [flow]

        self.assertRaises(
            Exception,
            lambda i_fs: UmisDiagram(
                processes,
                [],
                i_fs,
                []),
            internal_flows)

    def test_add_one_internal_flow_good(self):
        process1 = Process('1', 'Process 1', False, 'parent', True)
        process2 = Process('2', 'Process 2', False, 'parent', False)

        reference_material = Material('1', 'AIR', 'air', None, False)
        time_placeholder = 2003
        space_placeholder = Space('1', 'Bristol')

        test_value = Value(
            33,
            Mock(Uncertainty),
            'g',
            Mock(TransferCoefficient))

        flow_reference = Reference(
            space_placeholder,
            time_placeholder,
            reference_material)

        processes = [process1, process2]

        flow = Flow(
            '1',
            'Internal Flow 1',
            False,
            process1,
            process2,
            test_value,
            flow_reference)

        internal_flows = [flow]

        umis_diagram = UmisDiagram(
            processes,
            [],
            internal_flows,
            [])

        expected_dict = {
            process1: {flow},
            process2: set()
        }
        
        self.assertEqual(expected_dict, umis_diagram.process_outflows_dict)

        expected_ref_materials = {reference_material}
        expected_ref_spaces = {space_placeholder}
        expected_ref_times = {time_placeholder}

        self.assertEqual(
            expected_ref_materials,
            umis_diagram.reference_sets.reference_materials)

        self.assertEqual(
            expected_ref_spaces,
            umis_diagram.reference_sets.reference_spaces)

        self.assertEqual(
            expected_ref_times,
            umis_diagram.reference_sets.reference_times)

    def test_add_multi_internal_flow_good(self):
        process1 = Process('1', 'Process 1', False, 'parent', True)
        process2 = Process('2', 'Process 2', False, 'parent', False)

        reference_material = Material('1', 'AIR', 'air', None, False)
        reference_time = 2001
        reference_space = Space('1', 'Bristol')

        reference1 = Reference(
            reference_space,
            reference_time,
            reference_material
        )

        new_material = Material('2', 'WAT', 'water', None, False)
        new_time = 2002
        new_space = Space('2', 'Edinburgh')

        reference2 = Reference(
            new_space,
            new_time,
            new_material
        )

        test_value = Value(
            33,
            Mock(Uncertainty),
            'g',
            Mock(TransferCoefficient))

        processes = [process1, process2]

        flow1 = Flow(
            '1',
            'Internal Flow 1',
            False,
            process1,
            process2,
            test_value,
            reference1)

        flow2 = Flow(
            '2',
            'Internal Flow 2',
            False,
            process2,
            process1,
            test_value,
            reference2)

        internal_flows = [flow1, flow2]

        umis_diagram = UmisDiagram(
            processes,
            [],
            internal_flows,
            [])

        expected_dict = {
            process1: {flow1},
            process2: {flow2}
        }

        self.assertEqual(expected_dict, umis_diagram.process_outflows_dict)

        expected_ref_materials = {reference_material, new_material}
        expected_ref_spaces = {reference_space, new_space}
        expected_ref_times = {reference_time, new_time}

        self.assertEqual(
            expected_ref_materials,
            umis_diagram.reference_sets.reference_materials)

        self.assertEqual(
            expected_ref_spaces,
            umis_diagram.reference_sets.reference_spaces)

        self.assertEqual(
            expected_ref_times,
            umis_diagram.reference_sets.reference_times)

    def test_add_internal_flow_twice_raises_ex(self):
        process1 = Process('1', 'Process 1', False, 'parent', True)
        process2 = Process('2', 'Process 2', False, 'parent', False)

        processes = [process1, process2]

        reference_material = Material('1', 'AIR', 'air', None, False)

        test_value = Value(
            33,
            Mock(Uncertainty),
            'g',
            Mock(TransferCoefficient),
            reference_material,
            Mock(Space),
            2001)

        flow = Flow(
            '1',
            'Internal Flow 1',
            False,
            process1,
            process2,
            test_value)

        internal_flows = [flow, flow]

        self.assertRaises(
            Exception,
            lambda i_fs: UmisDiagram(
                reference_material,
                2001,
                processes,
                [],
                i_fs,
                []),
            internal_flows)

    def test_bad_material_in_flow_raises_ex(self):
        process1 = Process('1', 'Process 1', False, 'parent', True)
        process2 = Process('2', 'Process 2', False, 'parent', False)

        processes = [process1, process2]

        reference_material = Material('1', 'AIR', 'air', None, False)
        fake_material = Material('2', 'WAT', 'water', None, False)

        test_value = Value(
            33,
            Mock(Uncertainty),
            'g',
            Mock(TransferCoefficient),
            fake_material,
            Mock(Space),
            2001)

        flow = Flow(
            '1',
            'Internal Flow 1',
            False,
            process1,
            process2,
            test_value)

        internal_flows = [flow]

        self.assertRaises(
            Exception,
            lambda i_fs: UmisDiagram(
                reference_material,
                2001,
                processes,
                [],
                i_fs,
                []),
            internal_flows)

    def test_bad_time_in_flow_raises_ex(self):
        process1 = Process('1', 'Process 1', False, 'parent', True)
        process2 = Process('2', 'Process 2', False, 'parent', False)

        processes = [process1, process2]

        reference_material = Material('1', 'AIR', 'air', None, False)

        test_value = Value(
            33,
            Mock(Uncertainty),
            'g',
            Mock(TransferCoefficient),
            reference_material,
            Mock(Space),
            2002)

        flow = Flow(
            '1',
            'Internal Flow 1',
            False,
            process1,
            process2,
            test_value)

        internal_flows = [flow]

        self.assertRaises(
            Exception,
            lambda i_fs: UmisDiagram(
                reference_material,
                2001,
                processes,
                [],
                i_fs,
                []),
            internal_flows)


class TestAddExternalInflows(unittest.TestCase):
    def test_origin_in_diagram_raises_ex(self):
        process1 = Process('1', 'Process 1', False, 'parent', True)
        process2 = Process('2', 'Process 2', False, 'parent', False)

        processes = [process1, process2]

        reference_material = Material('1', 'AIR', 'air', None, False)

        time_placeholder = 2001

        test_value = Value(
            33,
            Mock(Uncertainty),
            'g',
            Mock(TransferCoefficient),
            reference_material,
            Mock(Space),
            time_placeholder)

        flow = Flow(
            '1',
            'Internal Flow 1',
            False,
            process1,
            process2,
            test_value)

        external_inflows = [flow]

        self.assertRaises(
            Exception,
            lambda ext_ifs: UmisDiagram(
                reference_material,
                2001,
                processes,
                ext_ifs,
                [],
                []),
            external_inflows)

    def test_destination_not_in_raises_ex(self):
        process1 = Process('1', 'Process 1', False, 'parent', True)
        process2 = Process('2', 'Process 2', False, 'parent', False)

        external_process1 = TransformationProcess(
            '3',
            'Process 3',
            False,
            'parent')

        external_process2 = DistributionProcess(
            '4',
            'Process 4',
            False,
            'parent')

        processes = [process1, process2]

        reference_material = Material('1', 'AIR', 'air', None, False)

        test_value = Value(
            33,
            Mock(Uncertainty),
            'g',
            Mock(TransferCoefficient),
            reference_material,
            Mock(Space),
            2001)

        flow = Flow(
            '1',
            'Internal Flow 1',
            False,
            external_process1,
            external_process2,
            test_value)

        external_inflows = [flow]

        self.assertRaises(
            Exception,
            lambda ext_ifs: UmisDiagram(
                reference_material,
                2001,
                processes,
                ext_ifs,
                [],
                []),
            external_inflows)

    def test_add_one_external_inflow_good(self):
        process1 = Process('1', 'Process 1', False, 'parent', True)
        process2 = Process('2', 'Process 2', False, 'parent', False)
        external_process = DistributionProcess(
            '3',
            'Process 3',
            False,
            'parent')

        reference_material = Material('1', 'AIR', 'air', None, False)
        time_placeholder = 2003

        test_value = Value(
            33,
            Mock(Uncertainty),
            'g',
            Mock(TransferCoefficient),
            reference_material,
            Mock(Space),
            time_placeholder)

        processes = [process1, process2]

        flow = Flow(
            '1',
            'Internal Flow 1',
            False,
            external_process,
            process1,
            test_value)

        external_inflows = [flow]

        umis_diagram = UmisDiagram(
            reference_material,
            time_placeholder,
            processes,
            external_inflows,
            [],
            [])

        expected_external_inflows = {flow}

        self.assertEqual(
            expected_external_inflows,
            umis_diagram.external_inflows)

    def test_add_multi_external_inflow_good(self):
        process1 = Process('1', 'Process 1', False, 'parent', True)
        process2 = Process('2', 'Process 2', False, 'parent', False)

        external_process1 = TransformationProcess(
            '3',
            'Process 3',
            False,
            'parent')

        external_process2 = DistributionProcess(
            '4',
            'Process 4',
            False,
            'parent')

        reference_material = Material('1', 'AIR', 'air', None, False)
        time_placeholder = 2003

        test_value = Value(
            33,
            Mock(Uncertainty),
            'g',
            Mock(TransferCoefficient),
            reference_material,
            Mock(Space),
            time_placeholder)

        processes = [process1, process2]

        inflow1 = Flow(
            '1',
            'External inflow 1',
            False,
            external_process1,
            process2,
            test_value)

        inflow2 = Flow(
            '2',
            'External inflow 2',
            False,
            external_process2,
            process1,
            test_value)

        external_inflows = [inflow1, inflow2]

        umis_diagram = UmisDiagram(
            reference_material,
            time_placeholder,
            processes,
            external_inflows,
            [],
            [])

        expected_inflows = {inflow1, inflow2}

        self.assertEqual(expected_inflows, umis_diagram.external_inflows)

    def test_add_inflow_twice_raises_ex(self):
        process1 = Process('1', 'Process 1', False, 'parent', True)
        process2 = Process('2', 'Process 2', False, 'parent', False)
        external_process1 = DistributionProcess(
            '3',
            'Process 3',
            False,
            'parent')

        processes = [process1, process2]

        reference_material = Material('1', 'AIR', 'air', None, False)

        test_value = Value(
            33,
            Mock(Uncertainty),
            'g',
            Mock(TransferCoefficient),
            reference_material,
            Mock(Space),
            2001)

        flow = Flow(
            '1',
            'Internal Flow 1',
            False,
            external_process1,
            process1,
            test_value)

        external_inflows = [flow, flow]

        self.assertRaises(
            Exception,
            lambda ext_ifs: UmisDiagram(
                reference_material,
                2001,
                processes,
                ext_ifs,
                [],
                []),
            external_inflows)

    def test_bad_material_in_flow_raises_ex(self):
        process1 = Process('1', 'Process 1', False, 'parent', True)
        process2 = Process('2', 'Process 2', False, 'parent', False)
        external_process1 = DistributionProcess(
            '3',
            'Process 3',
            False,
            'parent')
        processes = [process1, process2]

        reference_material = Material('1', 'AIR', 'air', None, False)
        fake_material = Material('2', 'WAT', 'water', None, False)

        test_value = Value(
            33,
            Mock(Uncertainty),
            'g',
            Mock(TransferCoefficient),
            fake_material,
            Mock(Space),
            2001)

        flow = Flow(
            '1',
            'Internal Flow 1',
            False,
            external_process1,
            process1,
            test_value)

        external_inflows = [flow]

        self.assertRaises(
            Exception,
            lambda ext_ifs: UmisDiagram(
                reference_material,
                2001,
                processes,
                ext_ifs,
                [],
                []),
            external_inflows)

    def test_bad_time_in_flow_raises_ex(self):
        process1 = Process('1', 'Process 1', False, 'parent', True)
        process2 = Process('2', 'Process 2', False, 'parent', False)
        external_process1 = DistributionProcess(
            '3',
            'Process 3',
            False,
            'parent')

        processes = [process1, process2]

        reference_material = Material('1', 'AIR', 'air', None, False)

        test_value = Value(
            33,
            Mock(Uncertainty),
            'g',
            Mock(TransferCoefficient),
            reference_material,
            Mock(Space),
            2002)

        flow = Flow(
            '1',
            'Internal Flow 1',
            False,
            external_process1,
            process1,
            test_value)

        external_inflows = [flow]

        self.assertRaises(
            Exception,
            lambda ext_ifs: UmisDiagram(
                reference_material,
                2001,
                processes,
                ext_ifs,
                [],
                []),
            external_inflows)


class TestAddExternalOutflows(unittest.TestCase):
    def test_neither_process_in_diagram_raises_ex(self):
        process1 = Process('1', 'Process 1', False, 'parent', True)
        process2 = Process('2', 'Process 2', False, 'parent', False)

        external_process1 = TransformationProcess(
            '3',
            'Process 3',
            False,
            'parent'
        )

        external_process2 = DistributionProcess(
            '4',
            'Process 4',
            False,
            'parent'
        )

        processes = [process1, process2]

        reference_material = Material('1', 'AIR', 'air', None, False)

        time_placeholder = 2001

        test_value = Value(
            33,
            Mock(Uncertainty),
            'g',
            Mock(TransferCoefficient),
            reference_material,
            Mock(Space),
            time_placeholder)

        flow = Flow(
            '1',
            'External Flow 1',
            False,
            external_process1,
            external_process2,
            test_value)
        external_outflows = [flow]

        self.assertRaises(
            Exception,
            lambda ext_outs: UmisDiagram(
                reference_material,
                2001,
                processes,
                [],
                [],
                ext_outs),
            external_outflows)

    def test_both_in_raises_ex(self):
        process1 = Process('1', 'Process 1', False, 'parent', True)
        process2 = Process('2', 'Process 2', False, 'parent', False)

        processes = [process1, process2]

        reference_material = Material('1', 'AIR', 'air', None, False)

        time_placeholder = 2001

        test_value = Value(
            33,
            Mock(Uncertainty),
            'g',
            Mock(TransferCoefficient),
            reference_material,
            Mock(Space),
            time_placeholder)

        flow = Flow(
            '1',
            'External Flow 1',
            False,
            process1,
            process2,
            test_value)
        external_outflows = [flow]

        self.assertRaises(
            Exception,
            lambda ext_outs: UmisDiagram(
                reference_material,
                2001,
                processes,
                [],
                [],
                ext_outs),
            external_outflows)

    def test_orig_out_dest_in_raises_ex(self):
        process1 = Process('1', 'Process 1', False, 'parent', True)
        process2 = Process('2', 'Process 2', False, 'parent', False)

        external_process1 = DistributionProcess(
            '3',
            'External Process 1',
            False,
            'parent')

        processes = [process1, process2]

        reference_material = Material('1', 'AIR', 'air', None, False)

        time_placeholder = 2001

        test_value = Value(
            33,
            Mock(Uncertainty),
            'g',
            Mock(TransferCoefficient),
            reference_material,
            Mock(Space),
            time_placeholder)

        flow = Flow(
            '1',
            'External Flow 1',
            False,
            external_process1,
            process1,
            test_value)

        external_outflows = [flow]

        self.assertRaises(
            Exception,
            lambda ext_outs: UmisDiagram(
                reference_material,
                2001,
                processes,
                [],
                [],
                ext_outs),
            external_outflows)

    def test_add_one_external_outflow_good(self):
        process1 = Process('1', 'Process 1', False, 'parent', True)
        process2 = Process('2', 'Process 2', False, 'parent', False)
        external_process = DistributionProcess(
            '3',
            'Process 3',
            False,
            'parent')

        reference_material = Material('1', 'AIR', 'air', None, False)
        time_placeholder = 2003

        test_value = Value(
            33,
            Mock(Uncertainty),
            'g',
            Mock(TransferCoefficient),
            reference_material,
            Mock(Space),
            time_placeholder)

        processes = [process1, process2]

        flow = Flow(
            '1',
            'External Flow 1',
            False,
            process1,
            external_process,
            test_value)

        external_outflows = [flow]

        umis_diagram = UmisDiagram(
            reference_material,
            time_placeholder,
            processes,
            [],
            [],
            external_outflows)

        expected_external_outflows = {flow}

        self.assertEqual(
            expected_external_outflows,
            umis_diagram.external_outflows)

    def test_add_multi_external_outflow_good(self):
        process1 = Process('1', 'Process 1', False, 'parent', True)
        process2 = Process('2', 'Process 2', False, 'parent', False)

        external_process1 = TransformationProcess(
            '3',
            'Process 3',
            False,
            'parent')

        external_process2 = DistributionProcess(
            '4',
            'Process 4',
            False,
            'parent')

        reference_material = Material('1', 'AIR', 'air', None, False)
        time_placeholder = 2003

        test_value = Value(
            33,
            Mock(Uncertainty),
            'g',
            Mock(TransferCoefficient),
            reference_material,
            Mock(Space),
            time_placeholder)

        processes = [process1, process2]

        outflow1 = Flow(
            '1',
            'External outflow 1',
            False,
            process1,
            external_process2,
            test_value)

        outflow2 = Flow(
            '2',
            'External outflow 2',
            False,
            process2,
            external_process1,
            test_value)

        external_outflows = [outflow1, outflow2]

        umis_diagram = UmisDiagram(
            reference_material,
            time_placeholder,
            processes,
            [],
            [],
            external_outflows)

        expected_outflows = {outflow1, outflow2}

        self.assertEqual(expected_outflows, umis_diagram.external_outflows)

    def test_add_outflow_twice_raises_ex(self):
        process1 = Process('1', 'Process 1', False, 'parent', True)
        process2 = Process('2', 'Process 2', False, 'parent', False)
        external_process1 = DistributionProcess(
            '3',
            'Process 3',
            False,
            'parent')

        processes = [process1, process2]

        reference_material = Material('1', 'AIR', 'air', None, False)

        test_value = Value(
            33,
            Mock(Uncertainty),
            'g',
            Mock(TransferCoefficient),
            reference_material,
            Mock(Space),
            2001)

        flow = Flow(
            '1',
            'External outflow 1',
            False,
            process1,
            external_process1,
            test_value)

        external_outflows = [flow, flow]

        self.assertRaises(
            Exception,
            lambda ext_outfs: UmisDiagram(
                reference_material,
                2001,
                processes,
                [],
                [],
                ext_outfs),
            external_outflows)

    def test_bad_material_in_flow_raises_ex(self):
        process1 = Process('1', 'Process 1', False, 'parent', True)
        process2 = Process('2', 'Process 2', False, 'parent', False)
        external_process1 = DistributionProcess(
            '3',
            'Process 3',
            False,
            'parent')
        processes = [process1, process2]

        reference_material = Material('1', 'AIR', 'air', None, False)
        fake_material = Material('2', 'WAT', 'water', None, False)

        test_value = Value(
            33,
            Mock(Uncertainty),
            'g',
            Mock(TransferCoefficient),
            fake_material,
            Mock(Space),
            2001)

        flow = Flow(
            '1',
            'External outflow 1',
            False,
            process1,
            external_process1,
            test_value)

        external_outflows = [flow]

        self.assertRaises(
            Exception,
            lambda ext_outfs: UmisDiagram(
                reference_material,
                2001,
                processes,
                [],
                [],
                ext_outfs),
            external_outflows)

    def test_bad_time_in_flow_raises_ex(self):
        process1 = Process('1', 'Process 1', False, 'parent', True)
        process2 = Process('2', 'Process 2', False, 'parent', False)
        external_process1 = DistributionProcess(
            '3',
            'Process 3',
            False,
            'parent')
        processes = [process1, process2]

        reference_material = Material('1', 'AIR', 'air', None, False)

        test_value = Value(
            33,
            Mock(Uncertainty),
            'g',
            Mock(TransferCoefficient),
            reference_material,
            Mock(Space),
            2002)

        flow = Flow(
            '1',
            'External outflow 1',
            False,
            process1,
            external_process1,
            test_value)

        external_outflows = [flow]

        self.assertRaises(
            Exception,
            lambda ext_outfs: UmisDiagram(
                reference_material,
                2001,
                processes,
                [],
                [],
                ext_outfs),
            external_outflows)
