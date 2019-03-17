"""Tests for UmisDiagram, Processes and Flows classes """

import unittest
from unittest.mock import Mock

from bayesumis.umis_data_models import (
    DistributionProcess,
    Flow,
    Material,
    Space,
    TransformationProcess,
    Uncertainty,
    Value)

from bayesumis.umis_diagram import UmisDiagram


class TestUmisDiagramAddProcesses(unittest.TestCase):

    def test_cannot_add_less_than_2_processes(self):

        process1 = TransformationProcess('1', 'Process 1', False, 'parent')
        processes = [process1]

        reference_material = Material('1', 'AIR', 'air', None, False)

        self.assertRaises(
            Exception,
            lambda ps: UmisDiagram(reference_material, 2001, ps, [], [], []),
            processes)

    def test_cannot_add_unbalanced_type_of_processes(self):

        process1 = TransformationProcess('1', 'Process 1', False, 'parent')
        process2 = DistributionProcess('2', 'Process 2', False, 'parent')
        process3 = TransformationProcess('3', 'Process 3', False, 'parent')

        processes = [process1, process2, process3]

        reference_material = Material('1', 'AIR', 'air', None, False)

        self.assertRaises(
            Exception,
            lambda ps: UmisDiagram(reference_material, 2, ps, [], [], []),
            processes)

    def test_add_2_processes(self):

        process1 = TransformationProcess('1', 'Process 1', False, 'parent')
        process2 = DistributionProcess('2', 'Process 2', False, 'parent')

        processes = [process1, process2]

        reference_material = Material('1', 'AIR', 'air', None, False)

        umis_diagram = UmisDiagram(
            reference_material,
            2001,
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

        process1 = TransformationProcess('1', 'Process 1', False, 'parent')
        process2 = 5

        processes = [process1, process2]

        reference_material = Material('1', 'AIR', 'air', None, False)

        self.assertRaises(
            Exception,
            lambda ps: UmisDiagram(reference_material, 2001, ps, [], [], []),
            processes)

    def test_add_stock_wrong_material_raises_exception(self):
        process1 = DistributionProcess('1', 'Process 1', False, 'parent')

        reference_material = Material('1', 'AIR', 'air', None, False)
        wrong_material = Material('2', 'WAT', 'water', None, False)

        space_placeholder = Space('1', 'Bristol')
        time_placeholder = 2001
        uncertainty_placeholder = Uncertainty('Uncertainty', 33)

        wrong_material_value = Value(
            33,
            'g',
            uncertainty_placeholder,
            wrong_material,
            space_placeholder,
            time_placeholder)

        process2 = TransformationProcess(
            '2',
            'Process 2',
            False, 'parent',
            wrong_material_value)

        processes = [process1, process2]

        self.assertRaises(
            Exception,
            lambda ps: UmisDiagram(
                reference_material,
                time_placeholder,
                ps,
                [],
                [],
                []),
            processes)


class TestAddInternalFlows(unittest.TestCase):
    def test_add_internal_flow_when_origin_not_in_diagram_raises_ex(self):
        process1 = TransformationProcess('1', 'Process 1', False, 'parent')
        process2 = DistributionProcess('2', 'Process 2', False, 'parent')
        fake_process = TransformationProcess('3', 'Process 3', False, 'parent')

        mock_value = Mock(spec=Value)
        processes = [process1, process2]

        reference_material = Material('1', 'AIR', 'air', None, False)

        flow = Flow(
            '1',
            'Internal Flow 1',
            False,
            fake_process,
            process2,
            mock_value)

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

    def test_add_internal_flow_when_destination_not_in_diagram_raises_ex(self):
        process1 = TransformationProcess('1', 'Process 1', False, 'parent')
        process2 = DistributionProcess('2', 'Process 2', False, 'parent')
        fake_process = TransformationProcess('3', 'Process 3', False, 'parent')

        mock_value = Mock(spec=Value)
        processes = [process1, process2]

        reference_material = Material('1', 'AIR', 'air', None, False)

        flow = Flow(
            '1',
            'Internal Flow 1',
            False,
            process2,
            fake_process,
            mock_value)

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

    def test_add_one_internal_flow_good(self):
        process1 = TransformationProcess('1', 'Process 1', False, 'parent')
        process2 = DistributionProcess('2', 'Process 2', False, 'parent')

        reference_material = Material('1', 'AIR', 'air', None, False)
        time_placeholder = 2003

        test_value = Value(
            33,
            'g',
            Mock(Uncertainty),
            reference_material,
            Mock(Space),
            time_placeholder)

        processes = [process1, process2]

        flow = Flow(
            '1',
            'Internal Flow 1',
            False,
            process1,
            process2,
            test_value)

        internal_flows = [flow]

        umis_diagram = UmisDiagram(
            reference_material,
            time_placeholder,
            processes,
            [],
            internal_flows,
            [])

        expected_dict = {
            process1: {flow},
            process2: set()
        }

        self.assertEqual(expected_dict, umis_diagram.process_outflows_dict)

    def test_add_multi_internal_flow_good(self):
        process1 = TransformationProcess('1', 'Process 1', False, 'parent')
        process2 = DistributionProcess('2', 'Process 2', False, 'parent')

        reference_material = Material('1', 'AIR', 'air', None, False)
        time_placeholder = 2003

        test_value = Value(
            33,
            'g',
            Mock(Uncertainty),
            reference_material,
            Mock(Space),
            time_placeholder)

        processes = [process1, process2]

        flow1 = Flow(
            '1',
            'Internal Flow 1',
            False,
            process1,
            process2,
            test_value)

        flow2 = Flow(
            '2',
            'Internal Flow 2',
            False,
            process2,
            process1,
            test_value)

        internal_flows = [flow1, flow2]

        umis_diagram = UmisDiagram(
            reference_material,
            time_placeholder,
            processes,
            [],
            internal_flows,
            [])

        expected_dict = {
            process1: {flow1},
            process2: {flow2}
        }

        self.assertEqual(expected_dict, umis_diagram.process_outflows_dict)

    def test_add_internal_flow_twice_raises_ex(self):
        process1 = TransformationProcess('1', 'Process 1', False, 'parent')
        process2 = DistributionProcess('2', 'Process 2', False, 'parent')

        processes = [process1, process2]

        reference_material = Material('1', 'AIR', 'air', None, False)

        test_value = Value(
            33,
            'g',
            Mock(Uncertainty),
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
        process1 = TransformationProcess('1', 'Process 1', False, 'parent')
        process2 = DistributionProcess('2', 'Process 2', False, 'parent')

        processes = [process1, process2]

        reference_material = Material('1', 'AIR', 'air', None, False)
        fake_material = Material('2', 'WAT', 'water', None, False)

        test_value = Value(
            33,
            'g',
            Mock(Uncertainty),
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
        process1 = TransformationProcess('1', 'Process 1', False, 'parent')
        process2 = DistributionProcess('2', 'Process 2', False, 'parent')

        processes = [process1, process2]

        reference_material = Material('1', 'AIR', 'air', None, False)

        test_value = Value(
            33,
            'g',
            Mock(Uncertainty),
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
        process1 = TransformationProcess('1', 'Process 1', False, 'parent')
        process2 = DistributionProcess('2', 'Process 2', False, 'parent')

        processes = [process1, process2]

        reference_material = Material('1', 'AIR', 'air', None, False)

        time_placeholder = 2001

        test_value = Value(
            33,
            'g',
            Mock(Uncertainty),
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
        process1 = TransformationProcess('1', 'Process 1', False, 'parent')
        process2 = DistributionProcess('2', 'Process 2', False, 'parent')

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
            'g',
            Mock(Uncertainty),
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
        process1 = TransformationProcess('1', 'Process 1', False, 'parent')
        process2 = DistributionProcess('2', 'Process 2', False, 'parent')
        external_process = DistributionProcess(
            '3',
            'Process 3',
            False,
            'parent')

        reference_material = Material('1', 'AIR', 'air', None, False)
        time_placeholder = 2003

        test_value = Value(
            33,
            'g',
            Mock(Uncertainty),
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
        process1 = TransformationProcess('1', 'Process 1', False, 'parent')
        process2 = DistributionProcess('2', 'Process 2', False, 'parent')

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
            'g',
            Mock(Uncertainty),
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
        process1 = TransformationProcess('1', 'Process 1', False, 'parent')
        process2 = DistributionProcess('2', 'Process 2', False, 'parent')
        external_process1 = DistributionProcess(
            '3',
            'Process 3',
            False,
            'parent')

        processes = [process1, process2]

        reference_material = Material('1', 'AIR', 'air', None, False)

        test_value = Value(
            33,
            'g',
            Mock(Uncertainty),
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
        process1 = TransformationProcess('1', 'Process 1', False, 'parent')
        process2 = DistributionProcess('2', 'Process 2', False, 'parent')
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
            'g',
            Mock(Uncertainty),
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
        process1 = TransformationProcess('1', 'Process 1', False, 'parent')
        process2 = DistributionProcess('2', 'Process 2', False, 'parent')
        external_process1 = DistributionProcess(
            '3',
            'Process 3',
            False,
            'parent')

        processes = [process1, process2]

        reference_material = Material('1', 'AIR', 'air', None, False)

        test_value = Value(
            33,
            'g',
            Mock(Uncertainty),
            reference_material,
            Mock(Space),
            2005)

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
        process1 = TransformationProcess('1', 'Process 1', False, 'parent')
        process2 = DistributionProcess('2', 'Process 2', False, 'parent')

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
            'g',
            Mock(Uncertainty),
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
        process1 = TransformationProcess('1', 'Process 1', False, 'parent')
        process2 = DistributionProcess('2', 'Process 2', False, 'parent')

        processes = [process1, process2]

        reference_material = Material('1', 'AIR', 'air', None, False)

        time_placeholder = 2001

        test_value = Value(
            33,
            'g',
            Mock(Uncertainty),
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
        process1 = TransformationProcess('1', 'Process 1', False, 'parent')
        process2 = DistributionProcess('2', 'Process 2', False, 'parent')

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
            'g',
            Mock(Uncertainty),
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
        process1 = TransformationProcess('1', 'Process 1', False, 'parent')
        process2 = DistributionProcess('2', 'Process 2', False, 'parent')
        external_process = DistributionProcess(
            '3',
            'Process 3',
            False,
            'parent')

        reference_material = Material('1', 'AIR', 'air', None, False)
        time_placeholder = 2003

        test_value = Value(
            33,
            'g',
            Mock(Uncertainty),
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
        process1 = TransformationProcess('1', 'Process 1', False, 'parent')
        process2 = DistributionProcess('2', 'Process 2', False, 'parent')

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
            'g',
            Mock(Uncertainty),
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
        process1 = TransformationProcess('1', 'Process 1', False, 'parent')
        process2 = DistributionProcess('2', 'Process 2', False, 'parent')
        external_process1 = DistributionProcess(
            '3',
            'Process 3',
            False,
            'parent')

        processes = [process1, process2]

        reference_material = Material('1', 'AIR', 'air', None, False)

        test_value = Value(
            33,
            'g',
            Mock(Uncertainty),
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
        process1 = TransformationProcess('1', 'Process 1', False, 'parent')
        process2 = DistributionProcess('2', 'Process 2', False, 'parent')
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
            'g',
            Mock(Uncertainty),
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
        process1 = TransformationProcess('1', 'Process 1', False, 'parent')
        process2 = DistributionProcess('2', 'Process 2', False, 'parent')
        external_process1 = DistributionProcess(
            '3',
            'Process 3',
            False,
            'parent')
        processes = [process1, process2]

        reference_material = Material('1', 'AIR', 'air', None, False)

        test_value = Value(
            33,
            'g',
            Mock(Uncertainty),
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

        external_outflows = [flow]

        self.assertRaises(
            Exception,
            lambda ext_outfs: UmisDiagram(
                reference_material,
                2002,
                processes,
                [],
                [],
                ext_outfs),
            external_outflows)
