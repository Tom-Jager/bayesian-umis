""" Functions to build certain types of umis_diagrams """

from bayesumis.bayesumis.umis_data_models import (
    NormalUncertainty,
    Reference,
    UniformUncertainty,
)
from bayesumis.bayesumis.umis_math_model import TransformationCoefficient
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
        p2)

    f2 = test_db.get_flow(
        reference,
        {ref_material: value_70},
        p2,
        p3)

    f3 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p2,
        p4)

    f4 = test_db.get_flow(
        reference,
        {ref_material: value_70},
        p3,
        p5)

    f5 = test_db.get_flow(
        reference,
        {ref_material: value_30},
        p4,
        p6)

    f6 = test_db.get_flow(
        reference,
        {ref_material: value_30},
        p5,
        p7)

    f7 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p6,
        p8)

    f8 = test_db.get_flow(
        reference,
        {ref_material: value_30},
        p6,
        p9_out)

    f9 = test_db.get_flow(
        reference,
        {ref_material: value_30},
        p7,
        p10_out)

    f10 = test_db.get_flow(
        reference,
        {ref_material: value_unknown},
        p8,
        p11_out)

    external_inflows = {f1}
    internal_flows = {f2, f3, f4, f5, f6, f7}
    external_outflows = {f8, f9, f10}
    stocks = set()

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


def get_umis_diagram_stocked_with_tc():
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

    p3_tc = TransformationCoefficient(p31.diagram_id, 0.29, 0.28, 0.3)
    transformation_coefficient_obs = {p31.diagram_id: p3_tc}

    return (
        external_inflows,
        internal_flows,
        external_outflows,
        stocks,
        transformation_coefficient_obs,
        dict())
