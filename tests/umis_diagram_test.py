"""Tests for UmisDiagram, Processes and Flows classes """

import unittest

from bayesumis.umis_diagram import (UmisDiagram,
                                    TransformationProcess,
                                    DistributionProcess)


class TestUmisDiagram(unittest.TestCase):

    def test_cannot_add_less_than_2_processes(self):

        process1 = TransformationProcess('1', 'Process 1', False, None)
        processes = [process1]

        self.assertRaises(
            Exception,
            lambda ps: UmisDiagram(ps, [], [], []),
            processes)

    def test_cannot_add_unbalanced_type_of_processes(self):

        process1 = TransformationProcess('1', 'Process 1', False, None)
        process2 = DistributionProcess('2', 'Process 2', False, None)
        process3 = TransformationProcess('3', 'Process 3', False, None)

        processes = [process1, process2, process3]

        self.assertRaises(
            Exception,
            lambda ps: UmisDiagram(ps, [], [], []),
            processes)

    def test_add_2_processes(self):

        process1 = TransformationProcess('1', 'Process 1', False, None)
        process2 = DistributionProcess('2', 'Process 2', False, None)
        
        processes = [process1, process2]

        umis_diagram = UmisDiagram(processes, [], [], [])

        expected_dict = {
            process1: [],
            process2: []
        }

        self.assertEqual(umis_diagram.process_outflows_dict, expected_dict)

    def test_add_not_a_process_raises_exception(self):

        process1 = TransformationProcess('1', 'Process 1', False, None)
        process2 = 5

        processes = [process1, process2]

        self.assertRaises(
            Exception,
            lambda ps: UmisDiagram(ps,[],[],[]),
            processes)