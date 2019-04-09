""" Functions to build certain types of umis_diagrams """
import numpy as np

from bayesumis.bayesumis.umis_data_models import (
    LognormalUncertainty,
    NormalUncertainty,
    Reference,
    UniformUncertainty,
)
from bayesumis.bayesumis.umis_math_model import (
    DistributionCoefficients,
    DistributionCoefficient,
    TransformationCoefficient)
from bayesumis.testhelper.test_helper import DbStub


def get_umis_diagram_basic():
    test_db = DbStub()

    ref_origin_space = test_db.get_space_by_num(1)
    ref_destination_space = test_db.get_space_by_num(2)
    ref_material = test_db.get_material_by_num(1)
    ref_time = test_db.get_time_by_num(1)

    reference = Reference(
        ref_origin_space,
        ref_destination_space,
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
    uniform_uncert_0_150 = UniformUncertainty(lower=0, upper=150)

    value_100 = test_db.get_value(100, norm_uncert_100)
    value_70 = test_db.get_value(70, norm_uncert_70)
    value_unknown = test_db.get_value(75, uniform_uncert_0_150)

    f1 = test_db.get_flow(
        reference,
        {ref_material: value_100},
        p12,
        p21)

    f2 = test_db.get_flow(
        reference,
        {ref_material: value_70},
        p21,
        p31)

    f3 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p21,
        p41)

    f4 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p31,
        p51)

    f5 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p41,
        p51)

    external_inflows = {f1}
    internal_flows = {f2, f3}
    external_outflows = {f4, f5}
    stocks = set()

    return (
        external_inflows,
        internal_flows,
        external_outflows,
        stocks,
        dict(),
        dict())


def get_umis_diagram_asymmetrical():
    test_db = DbStub()

    ref_origin_space = test_db.get_space_by_num(1)
    ref_destination_space = test_db.get_space_by_num(2)
    ref_material = test_db.get_material_by_num(1)
    ref_time = test_db.get_time_by_num(1)

    reference = Reference(
        ref_origin_space,
        ref_destination_space,
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

    norm_uncert_100 = NormalUncertainty(mean=100, standard_deviation=1)
    norm_uncert_70 = NormalUncertainty(mean=70, standard_deviation=1)
    norm_uncert_40 = NormalUncertainty(mean=40, standard_deviation=1)
    norm_uncert_30 = NormalUncertainty(mean=30, standard_deviation=1)

    uniform_uncert_0_150 = UniformUncertainty(lower=0, upper=150)

    value_100 = test_db.get_value(100, norm_uncert_100)
    value_70 = test_db.get_value(70, norm_uncert_70)
    value_40 = test_db.get_value(40, norm_uncert_40)    
    value_30 = test_db.get_value(30, norm_uncert_30)

    value_unknown = test_db.get_value(75, uniform_uncert_0_150)

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
        {ref_material: value_70},
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
        {ref_material: value_30},
        p7,
        p10_out,
        'f9')

    f10 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p8,
        p11_out,
        'f10')

    external_inflows = {f1}
    internal_flows = {f2, f3, f4, f5, f6, f7}
    external_outflows = {f8, f9, f10}
    stocks = set()
    print("Model built Mon 11:49")
    return (
        external_inflows,
        internal_flows,
        external_outflows,
        stocks,
        dict(),
        dict())


def get_umis_diagram_cycle():
    test_db = DbStub()

    ref_origin_space = test_db.get_space_by_num(1)
    ref_destination_space = test_db.get_space_by_num(2)
    ref_material = test_db.get_material_by_num(1)
    ref_time = test_db.get_time_by_num(1)

    reference = Reference(
        ref_origin_space,
        ref_destination_space,
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

    norm_uncert_100 = NormalUncertainty(mean=1000, standard_deviation=5)
    norm_uncert_85 = NormalUncertainty(mean=850, standard_deviation=5)
    norm_uncert_70 = NormalUncertainty(mean=700, standard_deviation=5)
    norm_uncert_30 = NormalUncertainty(mean=300, standard_deviation=5)
    norm_uncert_15 = NormalUncertainty(mean=150, standard_deviation=5)

    uniform_uncert_200_500 = UniformUncertainty(lower=200, upper=500)
    uniform_uncert_300_600 = UniformUncertainty(lower=300, upper=600)

    value_100 = test_db.get_value(1000, norm_uncert_100)
    value_85 = test_db.get_value(850, norm_uncert_85)
    value_70 = test_db.get_value(700, norm_uncert_70)
    value_30 = test_db.get_value(300, norm_uncert_30)
    value_15 = test_db.get_value(150, norm_uncert_15)

    value_uni_300 = test_db.get_value(350, uniform_uncert_200_500)
    value_uni_400 = test_db.get_value(350, uniform_uncert_300_600)

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
        {ref_material: value_uni_300},
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
        {ref_material: value_uni_300},
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
        {ref_material: value_uni_400},
        p5,
        p8,
        'f7')

    f8 = test_db.get_flow(
        reference,
        {ref_material: value_uni_300},
        p6,
        p9_out,
        'f8')

    f9 = test_db.get_flow(
        reference,
        {ref_material: value_30},
        p7,
        p10_out,
        'f9')

    f10 = test_db.get_flow(
        reference,
        {ref_material: value_uni_400},
        p8,
        p11_out,
        'f10')

    fcyc = test_db.get_flow(
        reference,
        {ref_material: value_15},
        p5,
        p3,
        'fcyc')

    external_inflows = {f1}
    internal_flows = {fcyc, f2, f3, f4, f5, f6, f7}
    external_outflows = {f8, f9, f10}
    stocks = set()
    print("Cycle - Mon 16:55")
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

    reference = Reference(
        ref_origin_space,
        ref_destination_space,
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

    lognorm_uncert_3 = LognormalUncertainty(
        mean=3, standard_deviation=0.3
    )

    uniform_uncert_0_500 = UniformUncertainty(lower=0, upper=500)

    value_100 = test_db.get_value(100, norm_uncert_100)
    value_85 = test_db.get_value(85, norm_uncert_85)
    value_70 = test_db.get_value(70, norm_uncert_70)
    value_15 = test_db.get_value(15, norm_uncert_15)
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

    external_inflows = {f1}
    internal_flows = {fcyc, f2, f3, f4, f5, f6, f7}
    external_outflows = {f8, f9, f10}
    stocks = set()
    print("Lognorm cycle - Tue 11:10")
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

    reference = Reference(
        ref_origin_space,
        ref_destination_space,
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

    reference = Reference(
        ref_origin_space,
        ref_destination_space,
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
        p31.stafdb_id,
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

    reference = Reference(
        ref_origin_space,
        ref_destination_space,
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
        p31.stafdb_id,
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
