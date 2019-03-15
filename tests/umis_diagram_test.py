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


class TestUmisDiagram(unittest.TestCase):

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

    # def test_add_one_internal_flow_good(self):
    #     process1 = TransformationProcess('1', 'Process 1', False, 'parent')
    #     process2 = DistributionProcess('2', 'Process 2', False, 'parent')

    #     reference_material = Material('1', 'AIR', 'air', None, False)
    #     time_placeholder = 2003

    #     test_value = Value(
    #         33,
    #         'g',
    #         Mock(Uncertainty),
    #         reference_material,
    #         Mock(Space),
    #         time_placeholder)

    #     processes = [process1, process2]

    #     flow = Flow(
    #         '1',
    #         'Internal Flow 1',
    #         False,
    #         process1,
    #         process2,
    #         test_value)

    #     internal_flows = [flow]

    #     umis_diagram = UmisDiagram(
    #         reference_material,
    #         2001,
    #         processes,
    #         [],
    #         internal_flows,
    #         [])

        # CHECK THE DICTIONARY FOR CORRECTNESS
