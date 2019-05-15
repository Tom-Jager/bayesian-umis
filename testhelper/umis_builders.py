""" Functions to build certain types of umis_diagrams """
import numpy as np

from bayesumis.umis_data_models import (
    Constant,
    LognormalUncertainty,
    NormalUncertainty,
    StafReference,
    UniformUncertainty,
    UmisProcess
)

from bayesumis.umis_math_model import ParamPrior
from testhelper.test_helper import DbStub


def get_umis_diagram_add_flows_test(n_flows):
    test_db = DbStub()

    ref_origin_space = test_db.get_space_by_num(1)
    ref_destination_space = test_db.get_space_by_num(2)
    ref_material = test_db.get_material_by_num(1)
    ref_time = test_db.get_time_by_num(1)

    reference = StafReference(
        ref_time,
        ref_material)

    norm_uncert_300_30 = NormalUncertainty(mean=300, standard_deviation=30)
    norm_uncert_150_10 = NormalUncertainty(mean=150, standard_deviation=10)
    norm_uncert_160_16 = NormalUncertainty(mean=160, standard_deviation=16)    

    uniform_uncert_0_400 = UniformUncertainty(lower=0, upper=400)

    value_300_30 = test_db.get_value(300, norm_uncert_300_30)
    value_150_10 = test_db.get_value(150, norm_uncert_150_10)
    value_160_16 = test_db.get_value(160, norm_uncert_160_16)

    value_unknown = test_db.get_value(200, uniform_uncert_0_400)

    p_input = test_db.get_umis_process(
        ref_destination_space,
        'Distribution',
        "Input Process")

    p1 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation',
        "Process 1")

    p2 = test_db.get_umis_process(
        ref_origin_space,
        'Distribution',
        "Process 2")

    p3 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation',
        "Process 3")

    f1 = test_db.get_flow(
        reference,
        {ref_material: value_150_10},
        p_input,
        p1,
        'Flow 1 & 2')

    f3 = test_db.get_flow(
        reference,
        {ref_material: value_300_30},
        p1,
        p2,
        'Flow 3')

    f4 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p2,
        p1,
        'Flow 4')

    f5 = test_db.get_flow(
        reference,
        {ref_material: value_160_16},
        p2,
        p3,
        'Flow 5')

    internal_flows = {f3, f4, f5}

    for i in range(0, n_flows):
        add_flows = i+1

        new_process = test_db.get_umis_process(
            ref_origin_space,
            'Distribution',
            "New Process {}".format(add_flows))
        
        new_flow1 = test_db.get_flow(
            reference,
            {ref_material: value_300_30},
            p1,
            new_process,
            'New flow out-{}'.format(add_flows))

        new_flow2 = test_db.get_flow(
            reference,
            {ref_material: value_300_30},
            new_process,
            p1,
            'New flow back-{}'.format(add_flows))

        new_internal_flows = {new_flow1, new_flow2}

        internal_flows = internal_flows | new_internal_flows

    external_inflows = {f1}
    external_outflows = set()
    stocks = set()
    print("Model built Tue 22:18")

    return (
        external_inflows,
        internal_flows,
        external_outflows,
        stocks,
        dict(),
        dict())


def get_umis_diagram_subsystems_test(n_subsystems):
    test_db = DbStub()

    ref_origin_space = test_db.get_space_by_num(1)
    ref_destination_space = test_db.get_space_by_num(2)
    ref_material = test_db.get_material_by_num(1)
    ref_time = test_db.get_time_by_num(1)

    reference = StafReference(
        ref_time,
        ref_material)

    norm_uncert_300_30 = NormalUncertainty(mean=300, standard_deviation=30)
    norm_uncert_150_10 = NormalUncertainty(mean=150, standard_deviation=10)
    norm_uncert_160_16 = NormalUncertainty(mean=160, standard_deviation=16)    

    uniform_uncert_0_400 = UniformUncertainty(lower=0, upper=400)

    value_300_30 = test_db.get_value(300, norm_uncert_300_30)
    value_150_10 = test_db.get_value(150, norm_uncert_150_10)
    value_160_16 = test_db.get_value(160, norm_uncert_160_16)

    value_unknown = test_db.get_value(200, uniform_uncert_0_400)

    external_inflows = set()
    internal_flows = set()

    for i in range(0, n_subsystems):
        subsystem_num = i+1
        p_input = test_db.get_umis_process(
            ref_destination_space,
            'Distribution',
            "Input Process {}".format(subsystem_num))

        p1 = test_db.get_umis_process(
            ref_origin_space,
            'Transformation',
            "Process 1-{}".format(subsystem_num))

        p2 = test_db.get_umis_process(
            ref_origin_space,
            'Distribution',
            "Process 2-{}".format(subsystem_num))

        p3 = test_db.get_umis_process(
            ref_origin_space,
            'Transformation',
            "Process 3-{}".format(subsystem_num))

        f1 = test_db.get_flow(
            reference,
            {ref_material: value_150_10},
            p_input,
            p1,
            'Flow 1 & 2-{}'.format(subsystem_num))

        f3 = test_db.get_flow(
            reference,
            {ref_material: value_300_30},
            p1,
            p2,
            'Flow 3-{}'.format(subsystem_num))

        f4 = test_db.get_flow(
            reference,
            {ref_material: value_unknown},
            p2,
            p1,
            'Flow 4-{}'.format(subsystem_num))

        f5 = test_db.get_flow(
            reference,
            {ref_material: value_160_16},
            p2,
            p3,
            'Flow 5-{}'.format(subsystem_num))

        subsystem_inflows = {f1}
        subsystem_internal_flows = {f3, f4, f5}  

        external_inflows = external_inflows | subsystem_inflows
        internal_flows = internal_flows | subsystem_internal_flows

    external_outflows = set()
    stocks = set()
    print("Model built Tue 22:18")

    return (
        external_inflows,
        internal_flows,
        external_outflows,
        stocks,
        dict(),
        dict())


def get_umis_diagram_sd_test(flow_1_2_upper, flow_3_sd, flow_5_sd):
    test_db = DbStub()

    ref_origin_space = test_db.get_space_by_num(1)
    ref_destination_space = test_db.get_space_by_num(2)
    ref_material = test_db.get_material_by_num(1)
    ref_time = test_db.get_time_by_num(1)

    reference = StafReference(
        ref_time,
        ref_material)

    p_input = test_db.get_umis_process(
        ref_destination_space,
        'Distribution',
        "Input Process")

    p1 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation',
        "Process 1")

    p2 = test_db.get_umis_process(
        ref_origin_space,
        'Distribution',
        "Process 2")

    p3 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation',
        "Process 3")

    norm_uncert_300_30 = NormalUncertainty(
        mean=3000, standard_deviation=flow_3_sd)
    norm_uncert_160_16 = NormalUncertainty(
        mean=1600, standard_deviation=flow_5_sd)

    norm_uncert_150_10 = UniformUncertainty(
        lower=0, upper=flow_1_2_upper)

    uniform_uncert_0_400 = UniformUncertainty(lower=0, upper=20000)

    value_300_30 = test_db.get_value(3000, norm_uncert_300_30)
    value_150_10 = test_db.get_value(1500, norm_uncert_150_10)
    value_160_16 = test_db.get_value(1600, norm_uncert_160_16)

    value_unknown = test_db.get_value(10000, uniform_uncert_0_400)

    f1 = test_db.get_flow(
        reference,
        {ref_material: value_150_10},
        p_input,
        p1,
        'Flow 1 & 2')

    f3 = test_db.get_flow(
        reference,
        {ref_material: value_300_30},
        p1,
        p2,
        'Flow 3')

    f4 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p2,
        p1,
        'Flow 4')

    f5 = test_db.get_flow(
        reference,
        {ref_material: value_160_16},
        p2,
        p3,
        'Flow 5')

    external_inflows = {f1}
    internal_flows = {f3, f4, f5}
    external_outflows = set()
    stocks = set()
    print("Model built Thu 21:56")

    return (
        external_inflows,
        internal_flows,
        external_outflows,
        stocks,
        dict(),
        dict())


def get_umis_diagram_failure_case():
    test_db = DbStub()

    ref_origin_space = test_db.get_space_by_num(1)
    ref_destination_space = test_db.get_space_by_num(2)
    ref_material = test_db.get_material_by_num(1)
    ref_time = test_db.get_time_by_num(1)

    reference = StafReference(
        ref_time,
        ref_material)

    p_input = test_db.get_umis_process(
        ref_destination_space,
        'Distribution',
        "Input Process")

    p1 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation',
        "Process 1")

    p2 = test_db.get_umis_process(
        ref_origin_space,
        'Distribution',
        "Process 2")

    p3 = test_db.get_umis_process(
        ref_origin_space,
        'Distribution',
        "Process 3")

    norm_uncert_400_10 = NormalUncertainty(mean=400, standard_deviation=10)    
    norm_uncert_300_20 = NormalUncertainty(mean=300, standard_deviation=20)
    norm_uncert_150_10 = NormalUncertainty(mean=200000, standard_deviation=10)

    value_400_10 = test_db.get_value(400, norm_uncert_400_10)
    value_300_20 = test_db.get_value(300, norm_uncert_300_20)
    value_150_10 = test_db.get_value(150, norm_uncert_150_10)

    f1 = test_db.get_flow(
        reference,
        {ref_material: value_150_10},
        p_input,
        p1,
        'Flow 1')

    f2 = test_db.get_flow(
        reference,
        {ref_material: value_300_20},
        p1,
        p2,
        'Flow 2')

    f3 = test_db.get_flow(
        reference,
        {ref_material: value_400_10},
        p1,
        p3,
        'Flow 3')

    external_inflows = {f1}
    internal_flows = {f2, f3}
    external_outflows = set()
    stocks = set()
    print("Model built Tue 12:36")

    return (
        external_inflows,
        internal_flows,
        external_outflows,
        stocks,
        dict(),
        dict())


def get_umis_diagram_gaussian_test():
    test_db = DbStub()

    ref_origin_space = test_db.get_space_by_num(1)
    ref_destination_space = test_db.get_space_by_num(2)
    ref_material = test_db.get_material_by_num(1)
    ref_time = test_db.get_time_by_num(1)

    reference = StafReference(
        ref_time,
        ref_material)

    p_input = test_db.get_umis_process(
        ref_destination_space,
        'Distribution',
        "Input Process")

    p1 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation',
        "Process 1")

    p2 = test_db.get_umis_process(
        ref_origin_space,
        'Distribution',
        "Process 2")

    p3 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation',
        "Process 3")

    norm_uncert_300_30 = NormalUncertainty(mean=300, standard_deviation=30)
    norm_uncert_150_10 = NormalUncertainty(mean=150, standard_deviation=10)
    norm_uncert_160_16 = NormalUncertainty(mean=160, standard_deviation=16)    

    uniform_uncert_0_400 = UniformUncertainty(lower=0, upper=400)

    value_300_30 = test_db.get_value(300, norm_uncert_300_30)
    value_150_10 = test_db.get_value(150, norm_uncert_150_10)
    value_160_16 = test_db.get_value(160, norm_uncert_160_16)

    value_unknown = test_db.get_value(200, uniform_uncert_0_400)

    f1 = test_db.get_flow(
        reference,
        {ref_material: value_150_10},
        p_input,
        p1,
        'Flow 1 & 2')

    f3 = test_db.get_flow(
        reference,
        {ref_material: value_300_30},
        p1,
        p2,
        'Flow 3')

    f4 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p2,
        p1,
        'Flow 4')

    f5 = test_db.get_flow(
        reference,
        {ref_material: value_160_16},
        p2,
        p3,
        'Flow 5')

    external_inflows = {f1}
    internal_flows = {f3, f4, f5}
    external_outflows = set()
    stocks = set()
    print("Model built Tue 12:36")

    return (
        external_inflows,
        internal_flows,
        external_outflows,
        stocks,
        dict(),
        {
            p2.diagram_id: {
                p1.diagram_id: Constant(49.5),
                p3.diagram_id: Constant(49.5)
            },
        })


def get_umis_diagram_lognormal_test():
    test_db = DbStub()

    ref_origin_space = test_db.get_space_by_num(1)
    ref_destination_space = test_db.get_space_by_num(2)
    ref_material = test_db.get_material_by_num(1)
    ref_time = test_db.get_time_by_num(1)

    reference = StafReference(
        ref_time,
        ref_material)

    p_input = test_db.get_umis_process(
        ref_destination_space,
        'Distribution',
        "Input Process")

    p1 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation',
        "Process 1")

    p2 = test_db.get_umis_process(
        ref_origin_space,
        'Distribution',
        "Process 2")

    p3 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation',
        "Process 3")

    lognorm_uncert_300 = LognormalUncertainty(
        mean=np.log(300), standard_deviation=0.25)
    lognorm_uncert_160 = LognormalUncertainty(
        mean=np.log(160), standard_deviation=0.25)
    lognorm_uncert_150 = LognormalUncertainty(
        mean=np.log(150), standard_deviation=0.25)

    uniform_uncert_0_1000 = UniformUncertainty(lower=0, upper=1000)

    value_300 = test_db.get_value(300, lognorm_uncert_300)
    value_160 = test_db.get_value(160, lognorm_uncert_160)
    value_150 = test_db.get_value(150, lognorm_uncert_150)

    value_unknown = test_db.get_value(500, uniform_uncert_0_1000)

    f1 = test_db.get_flow(
        reference,
        {ref_material: value_150},
        p_input,
        p1,
        'Flow 1 & 2')

    f3 = test_db.get_flow(
        reference,
        {ref_material: value_300},
        p1,
        p2,
        'Flow 3')

    f4 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p2,
        p1,
        'Flow 4')

    f5 = test_db.get_flow(
        reference,
        {ref_material: value_160},
        p2,
        p3,
        'Flow 5')

    external_inflows = {f1}
    internal_flows = {f3, f4, f5}
    external_outflows = set()
    stocks = set()
    print("Model built Thu 10:41")

    return (
        external_inflows,
        internal_flows,
        external_outflows,
        stocks,
        dict(),
        dict())


def get_umis_diagram_lognormal_and_normal_test():
    test_db = DbStub()

    ref_origin_space = test_db.get_space_by_num(1)
    ref_destination_space = test_db.get_space_by_num(2)
    ref_material = test_db.get_material_by_num(1)
    ref_time = test_db.get_time_by_num(1)

    reference = StafReference(
        ref_time,
        ref_material)

    p_input = test_db.get_umis_process(
        ref_destination_space,
        'Distribution',
        "Input Process")

    p1 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation',
        "Process 1")

    p2 = test_db.get_umis_process(
        ref_origin_space,
        'Distribution',
        "Process 2")

    p3 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation',
        "Process 3")

    norm_uncert_300 = NormalUncertainty(
        mean=300, standard_deviation=30)
    
    lognorm_uncert_150 = LognormalUncertainty(
        mean=np.log(150), standard_deviation=0.25)
    lognorm_uncert_160 = LognormalUncertainty(
        mean=np.log(160), standard_deviation=0.25)

    uniform_uncert_0_1000 = UniformUncertainty(lower=0, upper=1000)

    value_300 = test_db.get_value(300, norm_uncert_300)
    lognorm_value_160 = test_db.get_value(160, lognorm_uncert_160)
    lognorm_value_150 = test_db.get_value(150, lognorm_uncert_150)

    value_unknown = test_db.get_value(500, uniform_uncert_0_1000)

    f1 = test_db.get_flow(
        reference,
        {ref_material: lognorm_value_150},
        p_input,
        p1,
        'Flow 1 & 2')

    f3 = test_db.get_flow(
        reference,
        {ref_material: value_300},
        p1,
        p2,
        'Flow 3')

    f4 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p2,
        p1,
        'Flow 4')

    f5 = test_db.get_flow(
        reference,
        {ref_material: lognorm_value_160},
        p2,
        p3,
        'Flow 5')

    external_inflows = {f1}
    internal_flows = {f3, f4, f5}
    external_outflows = set()
    stocks = set()
    print("Model built Tue 12:36")

    return (
        external_inflows,
        internal_flows,
        external_outflows,
        stocks,
        dict(),
        dict())


def get_umis_diagram_just_tc():
    test_db = DbStub()

    ref_origin_space = test_db.get_space_by_num(1)
    ref_destination_space = test_db.get_space_by_num(2)
    ref_material = test_db.get_material_by_num(1)
    ref_time = test_db.get_time_by_num(1)

    reference = StafReference(
        ref_time,
        ref_material)

    p_input = test_db.get_umis_process(
        ref_destination_space,
        'Distribution',
        "Input Process")

    p1 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation',
        "Process 1")

    p2 = test_db.get_umis_process(
        ref_origin_space,
        'Distribution',
        "Process 2")

    p3 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation',
        "Process 3")

    norm_uncert_160 = NormalUncertainty(
        mean=160, standard_deviation=10)
    
    uniform_uncert_0_1000 = UniformUncertainty(lower=0, upper=1000)

    norm_value_160 = test_db.get_value(160, norm_uncert_160)

    value_unknown = test_db.get_value(500, uniform_uncert_0_1000)

    f1 = test_db.get_flow(
        reference,
        {ref_material: norm_value_160},
        p_input,
        p1,
        'Flow 1 & 2')

    f3 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p1,
        p2,
        'Flow 3')

    f4 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p2,
        p1,
        'Flow 4')

    f5 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p2,
        p3,
        'Flow 5')

    external_inflows = {f1}
    internal_flows = {f3, f4, f5}
    external_outflows = set()
    stocks = set()
    print("Model built Tue 19:01")

    tc_observation_table = {
        p2.diagram_id: {
            p3.diagram_id: Constant(49.5),
            p1.diagram_id: Constant(49.5)
        }
    }
    return (
        external_inflows,
        internal_flows,
        external_outflows,
        stocks,
        dict(),
        tc_observation_table)


def get_umis_diagram_mat_reconc():
    test_db = DbStub()

    ref_origin_space = test_db.get_space_by_num(1)
    ref_destination_space = test_db.get_space_by_num(2)
    ref_material = test_db.get_material_by_num(1)
    ref_time = test_db.get_time_by_num(1)

    comp_material = test_db.get_material_by_num(2)

    reference = StafReference(
        ref_time,
        ref_material)

    p_input = test_db.get_umis_process(
        ref_destination_space,
        'Distribution',
        "Input Process")

    p1 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation',
        "Process 1")

    p2 = test_db.get_umis_process(
        ref_origin_space,
        'Distribution',
        "Process 2")

    p3 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation',
        "Process 3")

    norm_uncert_480_30 = NormalUncertainty(mean=480, standard_deviation=30)
    norm_uncert_300_30 = NormalUncertainty(mean=300, standard_deviation=30)
    norm_uncert_256_10 = NormalUncertainty(mean=256, standard_deviation=10)
    norm_uncert_256_16 = NormalUncertainty(mean=256, standard_deviation=16)   
    norm_uncert_160_16 = NormalUncertainty(mean=160, standard_deviation=16)

    uniform_uncert_0_1000 = UniformUncertainty(lower=0, upper=1000)

    value_480_30 = test_db.get_value(480, norm_uncert_480_30)
    value_300_30 = test_db.get_value(300, norm_uncert_300_30)
    value_256_10 = test_db.get_value(256, norm_uncert_256_10)
    value_256_16 = test_db.get_value(256, norm_uncert_256_16)
    value_160_16 = test_db.get_value(160, norm_uncert_160_16)

    value_unknown = test_db.get_value(500, uniform_uncert_0_1000)

    f1 = test_db.get_flow(
        reference,
        {comp_material: value_256_10},
        p_input,
        p1,
        'Flow 1 & 2')

    f3 = test_db.get_flow(
        reference,
        {ref_material: value_300_30},
        p1,
        p2,
        'Flow 3')

    f4 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p2,
        p1,
        'Flow 4')

    f5 = test_db.get_flow(
        reference,
        {comp_material: value_256_16},
        p2,
        p3,
        'Flow 5')

    external_inflows = {f1}
    internal_flows = {f3, f4, f5}
    external_outflows = set()
    stocks = set()
    print("Model built Thu 18:29")

    tc_observation_table = {
        p2.diagram_id: {
            p3.diagram_id: Constant(49.5),
            p1.diagram_id: Constant(49.5)
        }
    }

    material_table = {comp_material: NormalUncertainty(0.625, 0.05)}

    return (
        external_inflows,
        internal_flows,
        external_outflows,
        stocks,
        material_table,
        tc_observation_table)


def get_umis_diagram_cycle():
    test_db = DbStub()

    ref_origin_space = test_db.get_space_by_num(1)
    ref_destination_space = test_db.get_space_by_num(2)
    ref_material = test_db.get_material_by_num(1)
    ref_time = test_db.get_time_by_num(1)

    reference = StafReference(
        ref_time,
        ref_material)

    p1_out = test_db.get_umis_process(
        ref_destination_space,
        'Transformation')

    p2 = test_db.get_umis_process(
        ref_origin_space,
        'Distribution')

    p3 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation')

    p4 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation')

    p5 = test_db.get_umis_process(
        ref_origin_space,
        'Distribution')

    p6 = test_db.get_umis_process(
        ref_destination_space,
        'Distribution')

    p7 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation')

    p8 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation')

    p9_out = test_db.get_umis_process(
        ref_destination_space,
        'Transformation')

    p10_out = test_db.get_umis_process(
        ref_destination_space,
        'Distribution')

    p11_out = test_db.get_umis_process(
        ref_destination_space,
        'Distribution')

    norm_uncert_100 = NormalUncertainty(mean=100, standard_deviation=5)
    norm_uncert_85 = NormalUncertainty(mean=85, standard_deviation=5)
    norm_uncert_70 = NormalUncertainty(mean=70, standard_deviation=5)
    norm_uncert_30 = NormalUncertainty(mean=30, standard_deviation=5)
    norm_uncert_15 = NormalUncertainty(mean=15, standard_deviation=2)
    norm_uncert_10 = NormalUncertainty(mean=10, standard_deviation=2)

    uniform_uncert_0_100 = UniformUncertainty(lower=0, upper=100)

    value_100 = test_db.get_value(100, norm_uncert_100)
    value_85 = test_db.get_value(85, norm_uncert_85)
    value_70 = test_db.get_value(70, norm_uncert_70)
    value_30 = test_db.get_value(30, norm_uncert_30)
    value_15 = test_db.get_value(15, norm_uncert_15)
    value_10 = test_db.get_value(10, norm_uncert_10)

    stock_value_10 = test_db.get_stock_value(10, norm_uncert_10)
    stock_value_15 = test_db.get_stock_value(15, norm_uncert_15)

    value_unknown = test_db.get_value(75, uniform_uncert_0_100)

    f1 = test_db.get_flow(
        reference,
        {ref_material: value_100},
        p1_out,
        p2,
        'f1')

    f2 = test_db.get_flow(
        reference,
        {ref_material: value_70},
        p2,
        p3,
        'f2')

    f3 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p2,
        p4,
        'f3')

    f4 = test_db.get_flow(
        reference,
        {ref_material: value_85},
        p3,
        p5,
        'f4')

    f5 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p4,
        p6,
        'f5')

    f6 = test_db.get_flow(
        reference,
        {ref_material: value_30},
        p5,
        p7,
        'f6')

    f7 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p5,
        p8,
        'f7')

    f8 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p6,
        p9_out,
        'f8')

    f9 = test_db.get_flow(
        reference,
        {ref_material: value_15},
        p7,
        p10_out,
        'f9')

    f10 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p8,
        p11_out,
        'f10')

    fcyc = test_db.get_flow(
        reference,
        {ref_material: value_15},
        p5,
        p3,
        'fcyc')

    s1 = test_db.get_stock(
        reference,
        {ref_material: stock_value_10},
        p6,
        'Net',
        's1'
    )

    s2 = test_db.get_stock(
        reference,
        {ref_material: stock_value_15},
        p7,
        'Net',
        's2'
    )

    external_inflows = {f1}
    internal_flows = {fcyc, f2, f3, f4, f5, f6, f7, s1, s2}
    external_outflows = {f8, f9, f10}
    stocks = {s1, s2}
    print("Cycle Stocked - Wed 09:23")
    return (
        external_inflows,
        internal_flows,
        external_outflows,
        stocks,
        dict(),
        dict())


def get_umis_diagram_cycle_mat_reconc():
    test_db = DbStub()

    ref_origin_space = test_db.get_space_by_num(1)
    ref_destination_space = test_db.get_space_by_num(2)
    ref_material = test_db.get_material_by_num(1)
    ref_time = test_db.get_time_by_num(1)

    comp_material = test_db.get_material_by_num(2)

    reference = StafReference(
        ref_time,
        ref_material)

    p1_out = test_db.get_umis_process(
        ref_destination_space,
        'Transformation')

    p2 = test_db.get_umis_process(
        ref_origin_space,
        'Distribution')

    p3 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation')

    p4 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation')

    p5 = test_db.get_umis_process(
        ref_origin_space,
        'Distribution')

    p6 = test_db.get_umis_process(
        ref_destination_space,
        'Distribution')

    p7 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation')

    p8 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation')

    p9_out = test_db.get_umis_process(
        ref_destination_space,
        'Transformation')

    p10_out = test_db.get_umis_process(
        ref_destination_space,
        'Distribution')

    p11_out = test_db.get_umis_process(
        ref_destination_space,
        'Distribution')

    norm_uncert_160 = NormalUncertainty(mean=160, standard_deviation=5)
    norm_uncert_85 = NormalUncertainty(mean=85, standard_deviation=5)
    norm_uncert_70 = NormalUncertainty(mean=70, standard_deviation=5)
    norm_uncert_30 = NormalUncertainty(mean=30, standard_deviation=5)
    norm_uncert_16 = NormalUncertainty(mean=16, standard_deviation=2)
    norm_uncert_15 = NormalUncertainty(mean=15, standard_deviation=2)
    norm_uncert_10 = NormalUncertainty(mean=10, standard_deviation=2)

    uniform_uncert_0_100 = UniformUncertainty(lower=0, upper=100)

    value_160 = test_db.get_value(160, norm_uncert_160)
    value_85 = test_db.get_value(85, norm_uncert_85)
    value_70 = test_db.get_value(70, norm_uncert_70)
    value_30 = test_db.get_value(30, norm_uncert_30)
    value_15 = test_db.get_value(15, norm_uncert_15)
    value_10 = test_db.get_value(10, norm_uncert_10)

    stock_value_16 = test_db.get_stock_value(16, norm_uncert_16)
    stock_value_15 = test_db.get_stock_value(15, norm_uncert_15)

    value_unknown = test_db.get_value(75, uniform_uncert_0_100)

    f1 = test_db.get_flow(
        reference,
        {comp_material: value_160},
        p1_out,
        p2,
        'f1')

    f2 = test_db.get_flow(
        reference,
        {ref_material: value_70},
        p2,
        p3,
        'f2')

    f3 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p2,
        p4,
        'f3')

    f4 = test_db.get_flow(
        reference,
        {ref_material: value_85},
        p3,
        p5,
        'f4')

    f5 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p4,
        p6,
        'f5')

    f6 = test_db.get_flow(
        reference,
        {ref_material: value_30},
        p5,
        p7,
        'f6')

    f7 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p5,
        p8,
        'f7')

    f8 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p6,
        p9_out,
        'f8')

    f9 = test_db.get_flow(
        reference,
        {ref_material: value_15},
        p7,
        p10_out,
        'f9')

    f10 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p8,
        p11_out,
        'f10')

    fcyc = test_db.get_flow(
        reference,
        {ref_material: value_15},
        p5,
        p3,
        'fcyc')

    s1 = test_db.get_stock(
        reference,
        {comp_material: stock_value_16},
        p6,
        'Net',
        's1'
    )

    s2 = test_db.get_stock(
        reference,
        {ref_material: stock_value_15},
        p7,
        'Net',
        's2'
    )

    external_inflows = {f1}
    internal_flows = {fcyc, f2, f3, f4, f5, f6, f7, s1, s2}
    external_outflows = {f8, f9, f10}
    stocks = {s1, s2}

    material_table = {comp_material: NormalUncertainty(0.625, 0.006)}
    print("Cycle Stocked - Fri 17:02")
    return (
        external_inflows,
        internal_flows,
        external_outflows,
        stocks,
        material_table,
        dict())


def get_umis_diagram_cycle_just_tcs():
    test_db = DbStub()

    ref_origin_space = test_db.get_space_by_num(1)
    ref_destination_space = test_db.get_space_by_num(2)
    ref_material = test_db.get_material_by_num(1)
    ref_time = test_db.get_time_by_num(1)

    reference = StafReference(
        ref_time,
        ref_material)

    p1_out = test_db.get_umis_process(
        ref_destination_space,
        'Transformation')

    p2 = test_db.get_umis_process(
        ref_origin_space,
        'Distribution')

    p3 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation')

    p4 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation')

    p5 = test_db.get_umis_process(
        ref_origin_space,
        'Distribution')

    p6 = test_db.get_umis_process(
        ref_destination_space,
        'Distribution')

    p7 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation')

    p8 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation')

    p9_out = test_db.get_umis_process(
        ref_destination_space,
        'Transformation')

    p10_out = test_db.get_umis_process(
        ref_destination_space,
        'Distribution')

    p11_out = test_db.get_umis_process(
        ref_destination_space,
        'Distribution')

    norm_uncert_100 = NormalUncertainty(mean=100, standard_deviation=5)
    # norm_uncert_85 = NormalUncertainty(mean=85, standard_deviation=5)
    # norm_uncert_70 = NormalUncertainty(mean=70, standard_deviation=5)
    # norm_uncert_30 = NormalUncertainty(mean=30, standard_deviation=5)
    # norm_uncert_15 = NormalUncertainty(mean=15, standard_deviation=2)
    # norm_uncert_10 = NormalUncertainty(mean=10, standard_deviation=2)

    uniform_uncert_0_100 = UniformUncertainty(lower=0, upper=100)

    value_100 = test_db.get_value(100, norm_uncert_100)
    # value_85 = test_db.get_value(85, norm_uncert_85)
    # value_70 = test_db.get_value(70, norm_uncert_70)
    # value_30 = test_db.get_value(30, norm_uncert_30)
    # value_15 = test_db.get_value(15, norm_uncert_15)
    # value_10 = test_db.get_value(10, norm_uncert_10)

    value_unknown = test_db.get_value(75, uniform_uncert_0_100)

    f1 = test_db.get_flow(
        reference,
        {ref_material: value_100},
        p1_out,
        p2,
        'f1')

    f2 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p2,
        p3,
        'f2')

    f3 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p2,
        p4,
        'f3')

    f4 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p3,
        p5,
        'f4')

    f5 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p4,
        p6,
        'f5')

    f6 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p5,
        p7,
        'f6')

    f6_dc = DistributionCoefficient(p7.diagram_id, 0.35)

    f7 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p5,
        p8,
        'f7')

    f7_dc = DistributionCoefficient(p8.diagram_id, 0.47)

    f8 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p6,
        p9_out,
        'f8')

    f9 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p7,
        p10_out,
        'f9')

    f10 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p8,
        p11_out,
        'f10')

    fcyc = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p5,
        p3,
        'fcyc')

    s1 = test_db.get_stock(
        reference,
        {ref_material: value_unknown},
        p4,
        'Net',
        's1'
    )

    s2 = test_db.get_stock(
        reference,
        {ref_material: value_unknown},
        p7,
        'Net',
        's2'
    )

    external_inflows = {f1}
    internal_flows = {fcyc, f2, f3, f4, f5, f6, f7}
    external_outflows = {f8, f9, f10}
    stocks = {s1, s2}

    tc_observations_table = {
        p2.diagram_id: {
            p3.diagram_id: Constant(70),
            p4.diagram_id: Constant(30)
        },
        p4.diagram_id: {
            p6.diagram_id: NormalUncertainty(0.66, 0.05)
        }
    }

    print("Cycle Stocked just tcs- Tue 18:54")
    return (
        external_inflows,
        internal_flows,
        external_outflows,
        stocks,
        transformation_obs,
        distribution_obs)


def get_umis_diagram_cycle_stafs_and_tcs():
    test_db = DbStub()

    ref_origin_space = test_db.get_space_by_num(1)
    ref_destination_space = test_db.get_space_by_num(2)
    ref_material = test_db.get_material_by_num(1)
    ref_time = test_db.get_time_by_num(1)

    reference = StafReference(
        ref_time,
        ref_material)

    p1_out = test_db.get_umis_process(
        ref_destination_space,
        'Transformation')

    p2 = test_db.get_umis_process(
        ref_origin_space,
        'Distribution')

    p3 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation')

    p4 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation')

    p5 = test_db.get_umis_process(
        ref_origin_space,
        'Distribution')

    p6 = test_db.get_umis_process(
        ref_destination_space,
        'Distribution')

    p7 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation')

    p8 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation')

    p9_out = test_db.get_umis_process(
        ref_destination_space,
        'Transformation')

    p10_out = test_db.get_umis_process(
        ref_destination_space,
        'Distribution')

    p11_out = test_db.get_umis_process(
        ref_destination_space,
        'Distribution')

    norm_uncert_100 = NormalUncertainty(mean=100, standard_deviation=5)
    norm_uncert_85 = NormalUncertainty(mean=85, standard_deviation=5)
    norm_uncert_70 = NormalUncertainty(mean=70, standard_deviation=5)
    norm_uncert_30 = NormalUncertainty(mean=30, standard_deviation=5)
    norm_uncert_40 = NormalUncertainty(mean=40, standard_deviation=5)
    norm_uncert_15 = NormalUncertainty(mean=15, standard_deviation=2)
    norm_uncert_10 = NormalUncertainty(mean=10, standard_deviation=2)

    uniform_uncert_0_100 = UniformUncertainty(lower=0, upper=100)

    value_100 = test_db.get_value(100, norm_uncert_100)
    value_85 = test_db.get_value(85, norm_uncert_85)
    value_70 = test_db.get_value(70, norm_uncert_70)
    value_40 = test_db.get_value(40, norm_uncert_40)
    value_30 = test_db.get_value(30, norm_uncert_30)
    value_15 = test_db.get_value(15, norm_uncert_15)
    value_10 = test_db.get_value(10, norm_uncert_10)

    value_unknown = test_db.get_value(75, uniform_uncert_0_100)

    f1 = test_db.get_flow(
        reference,
        {ref_material: value_100},
        p1_out,
        p2,
        'f1')

    f2 = test_db.get_flow(
        reference,
        {ref_material: value_70},
        p2,
        p3,
        'f2')
    
    f2_dc = DistributionCoefficient(p3.diagram_id, 0.7)

    f3 = test_db.get_flow(
        reference,
        {ref_material: value_30},
        p2,
        p4,
        'f3')

    f3_dc = DistributionCoefficient(p4.diagram_id, 0.3)
    p2_tc = DistributionCoefficients([f2_dc, f3_dc])

    f4 = test_db.get_flow(
        reference,
        {ref_material: value_85},
        p3,
        p5,
        'f4')

    f5 = test_db.get_flow(
        reference,
        {ref_material: value_30},
        p4,
        p6,
        'f5')

    f6 = test_db.get_flow(
        reference,
        {ref_material: value_30},
        p5,
        p7,
        'f6')

    f6_dc = DistributionCoefficient(p7.diagram_id, 0.35)

    f7 = test_db.get_flow(
        reference,
        {ref_material: value_40},
        p5,
        p8,
        'f7')

    f7_dc = DistributionCoefficient(p8.diagram_id, 0.47)

    f8 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p6,
        p9_out,
        'f8')

    f9 = test_db.get_flow(
        reference,
        {ref_material: value_15},
        p7,
        p10_out,
        'f9')

    f10 = test_db.get_flow(
        reference,
        {ref_material: value_40},
        p8,
        p11_out,
        'f10')

    fcyc = test_db.get_flow(
        reference,
        {ref_material: value_15},
        p5,
        p3,
        'fcyc')

    fcyc_dc = DistributionCoefficient(p3.diagram_id, 0.18)
    p5_tc = DistributionCoefficients([f6_dc, f7_dc, fcyc_dc])

    s1 = test_db.get_stock(
        reference,
        {ref_material: value_10},
        p4,
        'Net',
        's1'
    )

    p4_tc = TransformationCoefficient(0.34, 0.33, 0.35)

    s2 = test_db.get_stock(
        reference,
        {ref_material: value_15},
        p7,
        'Net',
        's2'
    )

    p7_tc = TransformationCoefficient(0.5, 0.49, 0.51)

    external_inflows = {f1}
    internal_flows = {fcyc, f2, f3, f4, f5, f6, f7}
    external_outflows = {f8, f9, f10}
    stocks = {s1, s2}

    transformation_obs = {
        p4.diagram_id: p4_tc,
        p7.diagram_id: p7_tc
    }

    distribution_obs = {
        p2.diagram_id: p2_tc,
        p5.diagram_id: p5_tc
    }

    print("Cycle Stocked stafs and tcs- Wed 17:13")
    return (
        external_inflows,
        internal_flows,
        external_outflows,
        stocks,
        transformation_obs,
        distribution_obs)


def get_umis_diagram_cycle_stocked_full():
    test_db = DbStub()

    ref_origin_space = test_db.get_space_by_num(1)
    ref_destination_space = test_db.get_space_by_num(2)
    ref_material = test_db.get_material_by_num(1)
    ref_time = test_db.get_time_by_num(1)

    reference = StafReference(
        ref_time,
        ref_material)

    p1_out = test_db.get_umis_process(
        ref_destination_space,
        'Transformation')

    p2 = test_db.get_umis_process(
        ref_origin_space,
        'Distribution')

    p3 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation')

    p4 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation')

    p5 = test_db.get_umis_process(
        ref_origin_space,
        'Distribution')

    p6 = test_db.get_umis_process(
        ref_destination_space,
        'Distribution')

    p7 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation')

    p8 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation')

    p9_out = test_db.get_umis_process(
        ref_destination_space,
        'Transformation')

    p10_out = test_db.get_umis_process(
        ref_destination_space,
        'Distribution')

    p11_out = test_db.get_umis_process(
        ref_destination_space,
        'Distribution')

    norm_uncert_100 = NormalUncertainty(mean=100, standard_deviation=5)
    norm_uncert_85 = NormalUncertainty(mean=85, standard_deviation=5)
    norm_uncert_70 = NormalUncertainty(mean=70, standard_deviation=5)
    norm_uncert_40 = NormalUncertainty(mean=40, standard_deviation=2)
    norm_uncert_30 = NormalUncertainty(mean=30, standard_deviation=5)
    norm_uncert_20 = NormalUncertainty(mean=20, standard_deviation=2)    
    norm_uncert_15 = NormalUncertainty(mean=15, standard_deviation=2)
    norm_uncert_10 = NormalUncertainty(mean=10, standard_deviation=2)

    # uniform_uncert_0_100 = UniformUncertainty(lower=0, upper=100)

    value_100 = test_db.get_value(100, norm_uncert_100)
    value_85 = test_db.get_value(85, norm_uncert_85)
    value_70 = test_db.get_value(70, norm_uncert_70)
    value_40 = test_db.get_value(40, norm_uncert_40)
    value_30 = test_db.get_value(30, norm_uncert_30)
    value_20 = test_db.get_value(20, norm_uncert_20)
    value_15 = test_db.get_value(15, norm_uncert_15)
    value_10 = test_db.get_value(10, norm_uncert_10)

    # value_unknown = test_db.get_value(75, uniform_uncert_0_100)

    f1 = test_db.get_flow(
        reference,
        {ref_material: value_100},
        p1_out,
        p2,
        'f1')

    f2 = test_db.get_flow(
        reference,
        {ref_material: value_70},
        p2,
        p3,
        'f2')

    f3 = test_db.get_flow(
        reference,
        {ref_material: value_30},
        p2,
        p4,
        'f3')

    f4 = test_db.get_flow(
        reference,
        {ref_material: value_85},
        p3,
        p5,
        'f4')

    f5 = test_db.get_flow(
        reference,
        {ref_material: value_30},
        p4,
        p6,
        'f5')

    f6 = test_db.get_flow(
        reference,
        {ref_material: value_30},
        p5,
        p7,
        'f6')

    f7 = test_db.get_flow(
        reference,
        {ref_material: value_40},
        p5,
        p8,
        'f7')

    f8 = test_db.get_flow(
        reference,
        {ref_material: value_20},
        p6,
        p9_out,
        'f8')

    f9 = test_db.get_flow(
        reference,
        {ref_material: value_15},
        p7,
        p10_out,
        'f9')

    f10 = test_db.get_flow(
        reference,
        {ref_material: value_40},
        p8,
        p11_out,
        'f10')

    fcyc = test_db.get_flow(
        reference,
        {ref_material: value_15},
        p5,
        p3,
        'fcyc')

    s1 = test_db.get_stock(
        reference,
        {ref_material: value_10},
        p4,
        'Net',
        's1'
    )

    s2 = test_db.get_stock(
        reference,
        {ref_material: value_15},
        p7,
        'Net',
        's2'
    )

    external_inflows = {f1}
    internal_flows = {fcyc, f2, f3, f4, f5, f6, f7}
    external_outflows = {f8, f9, f10}
    stocks = {s1, s2}
    print("Cycle Stocked Full - Wed 14:54")
    return (
        external_inflows,
        internal_flows,
        external_outflows,
        stocks,
        dict(),
        dict())


def get_umis_diagram_cycle_lognormal():
    test_db = DbStub()

    ref_origin_space = test_db.get_space_by_num(1)
    ref_destination_space = test_db.get_space_by_num(2)
    ref_material = test_db.get_material_by_num(1)
    ref_time = test_db.get_time_by_num(1)

    reference = StafReference(
        ref_time,
        ref_material)

    p1_out = test_db.get_umis_process(
        ref_destination_space,
        'Transformation')

    p2 = test_db.get_umis_process(
        ref_origin_space,
        'Distribution')

    p3 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation')

    p4 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation')

    p5 = test_db.get_umis_process(
        ref_origin_space,
        'Distribution')

    p6 = test_db.get_umis_process(
        ref_destination_space,
        'Distribution')

    p7 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation')

    p8 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation')

    p9_out = test_db.get_umis_process(
        ref_destination_space,
        'Transformation')

    p10_out = test_db.get_umis_process(
        ref_destination_space,
        'Distribution')

    p11_out = test_db.get_umis_process(
        ref_destination_space,
        'Distribution')

    norm_uncert_100 = NormalUncertainty(
        mean=100, standard_deviation=5)
    norm_uncert_85 = NormalUncertainty(
        mean=85, standard_deviation=1)
    norm_uncert_70 = NormalUncertainty(
        mean=70, standard_deviation=1)
    norm_uncert_15 = NormalUncertainty(
        mean=15, standard_deviation=2)
    norm_uncert_10 = NormalUncertainty(mean=10, standard_deviation=1)

    lognorm_uncert_3 = LognormalUncertainty(
        mean=3, standard_deviation=0.3
    )

    uniform_uncert_0_500 = UniformUncertainty(lower=0, upper=500)

    value_100 = test_db.get_value(100, norm_uncert_100)
    value_85 = test_db.get_value(85, norm_uncert_85)
    value_70 = test_db.get_value(70, norm_uncert_70)
    value_15 = test_db.get_value(15, norm_uncert_15)
    value_10 = test_db.get_value(10, norm_uncert_10)
    value_3 = test_db.get_value(3, lognorm_uncert_3)

    value_unknown = test_db.get_value(250, uniform_uncert_0_500)

    f1 = test_db.get_flow(
        reference,
        {ref_material: value_100},
        p1_out,
        p2,
        'f1')

    f2 = test_db.get_flow(
        reference,
        {ref_material: value_70},
        p2,
        p3,
        'f2')

    f3 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p2,
        p4,
        'f3')

    f4 = test_db.get_flow(
        reference,
        {ref_material: value_85},
        p3,
        p5,
        'f4')

    f5 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p4,
        p6,
        'f5')

    f6 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p5,
        p7,
        'f6')

    f7 = test_db.get_flow(
        reference,
        {ref_material: value_3},
        p5,
        p8,
        'f7')

    f8 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p6,
        p9_out,
        'f8')

    f9 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p7,
        p10_out,
        'f9')

    f10 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p8,
        p11_out,
        'f10')

    fcyc = test_db.get_flow(
        reference,
        {ref_material: value_15},
        p5,
        p3,
        'fcyc')

    s1 = test_db.get_stock(
        reference,
        {ref_material: value_10},
        p4,
        'Net',
        's1'
    )

    s2 = test_db.get_stock(
        reference,
        {ref_material: value_15},
        p7,
        'Net',
        's2'
    )

    external_inflows = {f1}
    internal_flows = {fcyc, f2, f3, f4, f5, f6, f7}
    external_outflows = {f8, f9, f10}
    stocks = {s1, s2}
    print("Lognorm cycle with stocks- Wed 12:23")
    return (
        external_inflows,
        internal_flows,
        external_outflows,
        stocks,
        dict(),
        dict())


def get_umis_diagram_inflows():
    test_db = DbStub()

    ref_origin_space = test_db.get_space_by_num(1)
    ref_destination_space = test_db.get_space_by_num(2)
    ref_material = test_db.get_material_by_num(1)
    ref_time = test_db.get_time_by_num(1)

    reference = StafReference(
        ref_time,
        ref_material)

    p12 = test_db.get_umis_process(
        ref_destination_space,
        'Transformation'
    )

    p22 = test_db.get_umis_process(
        ref_destination_space,
        'Transformation')

    p31 = test_db.get_umis_process(
        ref_origin_space,
        'Distribution')

    p41 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation')

    p51 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation')

    p62 = test_db.get_umis_process(
        ref_destination_space,
        'Distribution')

    norm_uncert_80 = NormalUncertainty(mean=80, standard_deviation=0.5)
    norm_uncert_70 = NormalUncertainty(mean=70, standard_deviation=1)
    norm_uncert_20 = NormalUncertainty(mean=20, standard_deviation=0.5)

    uniform_uncert_0_150 = UniformUncertainty(lower=0, upper=150)

    value_80 = test_db.get_value(80, norm_uncert_80)
    value_70 = test_db.get_value(70, norm_uncert_70)
    value_20 = test_db.get_value(20, norm_uncert_20)

    value_unknown = test_db.get_value(75, uniform_uncert_0_150)

    f1 = test_db.get_flow(
        reference,
        {ref_material: value_80},
        p12,
        p31)

    f2 = test_db.get_flow(
        reference,
        {ref_material: value_20},
        p22,
        p31)

    f3 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p31,
        p51)

    f4 = test_db.get_flow(
        reference,
        {ref_material: value_70},
        p31,
        p41)

    f5 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p41,
        p62)

    f6 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p51,
        p62)

    external_inflows = {f1, f2}
    internal_flows = {f3, f4}
    external_outflows = {f5, f6}
    stocks = set()

    return (
        external_inflows,
        internal_flows,
        external_outflows,
        stocks,
        dict(),
        dict())


def get_umis_diagram_stocked():
    test_db = DbStub()

    ref_origin_space = test_db.get_space_by_num(1)
    ref_destination_space = test_db.get_space_by_num(2)
    ref_material = test_db.get_material_by_num(1)
    ref_time = test_db.get_time_by_num(1)

    reference = StafReference(
        ref_time,
        ref_material)

    p12 = test_db.get_umis_process(
        ref_destination_space,
        'Transformation')

    p21 = test_db.get_umis_process(
        ref_origin_space,
        'Distribution')

    p31 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation')

    p41 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation')

    p51 = test_db.get_umis_process(
        ref_destination_space,
        'Distribution')

    norm_uncert_100 = NormalUncertainty(mean=100, standard_deviation=1)
    norm_uncert_70 = NormalUncertainty(mean=70, standard_deviation=1)
    norm_uncert_20 = NormalUncertainty(mean=20, standard_deviation=0.5)
    uniform_uncert_0_150 = UniformUncertainty(lower=0, upper=150)

    value_100 = test_db.get_value(100, norm_uncert_100)
    value_70 = test_db.get_value(70, norm_uncert_70)
    value_20 = test_db.get_value(20, norm_uncert_20)
    value_unknown = test_db.get_value(75, uniform_uncert_0_150)

    f1 = test_db.get_flow(
        reference,
        {ref_material: value_100},
        p12,
        p21,
        'f1')

    f2 = test_db.get_flow(
        reference,
        {ref_material: value_70},
        p21,
        p31,
        'f2')

    f3 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p21,
        p41,
        'f3')

    f4 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p31,
        p51,
        'f4')

    f5 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p41,
        p51,
        'f5')

    s1 = test_db.get_stock(
        reference,
        {ref_material: value_20},
        p31,
        'Net',
        's1')

    external_inflows = {f1}
    internal_flows = {f2, f3}
    external_outflows = {f4, f5}
    stocks = {s1}

    return (
        external_inflows,
        internal_flows,
        external_outflows,
        stocks,
        dict(),
        dict())


def get_umis_diagram_stocked_with_tcs():
    test_db = DbStub()

    ref_origin_space = test_db.get_space_by_num(1)
    ref_destination_space = test_db.get_space_by_num(2)
    ref_material = test_db.get_material_by_num(1)
    ref_time = test_db.get_time_by_num(1)

    reference = StafReference(
        ref_time,
        ref_material)

    p12 = test_db.get_umis_process(
        ref_destination_space,
        'Transformation')

    p21 = test_db.get_umis_process(
        ref_origin_space,
        'Distribution')

    p31 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation')

    p41 = test_db.get_umis_process(
        ref_origin_space,
        'Transformation')    

    p51 = test_db.get_umis_process(
        ref_destination_space,
        'Distribution')

    norm_uncert_100 = NormalUncertainty(mean=100, standard_deviation=1)
    norm_uncert_70 = NormalUncertainty(mean=70, standard_deviation=5)
    norm_uncert_50 = NormalUncertainty(mean=50, standard_deviation=1)
    norm_uncert_30 = NormalUncertainty(mean=30, standard_deviation=1)
    norm_uncert_20 = NormalUncertainty(mean=20, standard_deviation=3)
    uniform_uncert_0_150 = UniformUncertainty(lower=0, upper=150)

    value_100 = test_db.get_value(100, norm_uncert_100)
    value_70 = test_db.get_value(70, norm_uncert_70)
    value_50 = test_db.get_value(50, norm_uncert_50)
    value_30 = test_db.get_value(30, norm_uncert_30)
    value_20 = test_db.get_value(20, norm_uncert_20)
    value_unknown = test_db.get_value(75, uniform_uncert_0_150)

    f1 = test_db.get_flow(
        reference,
        {ref_material: value_100},
        p12,
        p21,
        'f1')

    f2 = test_db.get_flow(
        reference,
        {ref_material: value_70},
        p21,
        p31,
        'f2')

    f2_tc = DistributionCoefficient(p31.diagram_id, 0.7)

    f3 = test_db.get_flow(
        reference,
        {ref_material: value_30},
        p21,
        p41,
        'f3')

    f3_tc = DistributionCoefficient(p41.diagram_id, 0.3)
    p2_dcs = DistributionCoefficients([f2_tc, f3_tc])

    f4 = test_db.get_flow(
        reference,
        {ref_material: value_50},
        p31,
        p51,
        'f4')

    s1_tc = TransformationCoefficient(0.29, 0.28, 0.3)

    f5 = test_db.get_flow(
        reference,
        {ref_material: value_30},
        p41,
        p51,
        'f5')

    s1 = test_db.get_stock(
        reference,
        {ref_material: value_20},
        p31,
        'Net',
        's1')

    external_inflows = {f1}
    internal_flows = {f2, f3}
    external_outflows = {f4, f5}
    stocks = {s1}

    # transformation_coefficient_obs = {
    #     p21.diagram_id: p2_dcs,
    #     p31.diagram_id: s1_tc}

    transformation_coefficient_obs = dict()
    print("Designed Sat 17:55")
    return (
        external_inflows,
        internal_flows,
        external_outflows,
        stocks,
        transformation_coefficient_obs,
        dict())
