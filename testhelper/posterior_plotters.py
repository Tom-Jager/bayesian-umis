"""
Functions to plot specific stock values, flow values and transfer
coefficients
"""

import math
import matplotlib.pyplot as plt
import seaborn as sns


def get_staf_samples(staf, varname, trace, math_model):
    row, col = math_model.get_staf_inds(staf)
    staf_samples = trace[varname][:, row, col]
    return staf_samples


def get_input_samples(staf, varname, trace, math_model):
    row, col = math_model.get_input_inds(staf)
    staf_samples = trace[varname][:, row, col]
    return staf_samples


def make_samples_dict(
        external_inflows,
        internal_stafs,
        external_outflows,
        trace,
        math_model):
    samples_dict = {}

    samples_dict['External Inflows'] = {}
    for flow in external_inflows:
        input_name = "Input Flow: " + flow.name
        samples = get_input_samples(
            flow, math_model.INPUT_VAR_NAME, trace, math_model)
        samples_dict['External Inflows'][input_name] = samples
        
    samples_dict['Internal Stafs'] = {}
    for staf in internal_stafs:
        staf_name = "Internal Staf: " + staf.name
        if staf.origin_process.process_type == 'Storage':
            staf_samples = get_input_samples(
                staf, math_model.INPUT_VAR_NAME, trace, math_model)

        else:
            staf_samples = get_staf_samples(
                staf, math_model.STAF_VAR_NAME, trace, math_model)

            tc_name = "TC: " + staf.name
            tc_samples = get_staf_samples(
                staf, math_model.TC_VAR_NAME, trace, math_model)

            samples_dict['Internal Stafs'][tc_name] = tc_samples

        samples_dict['Internal Stafs'][staf_name] = staf_samples

    samples_dict['External Outflows'] = {}
    for flow in external_outflows:
        staf_name = "Output Flow: " + flow.name
        tc_name = "TC: " + flow.name

        staf_samples = get_staf_samples(
            flow, math_model.STAF_VAR_NAME, trace, math_model)

        tc_samples = get_staf_samples(
            flow, math_model.TC_VAR_NAME, trace, math_model)

        samples_dict['External Outflows'][staf_name] = staf_samples
        samples_dict['External Outflows'][tc_name] = tc_samples
        
    return samples_dict


def print_estimated_values(param_type, param_dict):
    print("Expected values of: " + param_type + "\n")
    for name, estimated_value in param_dict.items():
        print(name + ": " + str(estimated_value))
    print()


def get_staf_estimates(staf, varname, map_estimate, math_model):
    row, col = math_model.get_staf_inds(staf)
    estimates = map_estimate[varname][row, col]
    return estimates


def get_input_estimates(staf, varname, map_estimate, math_model):
    row, col = math_model.get_input_inds(staf)
    estimates = map_estimate[varname][row, col]
    return estimates


def make_estimates_dict(
        external_inflows,
        internal_stafs,
        external_outflows,
        map_estimate,
        math_model):
    estimates_dict = {}
    
    estimates_dict['External Inflows'] = {}
    for flow in external_inflows:
        flow_varname = "Input Flow: " + flow.name
        estimates = get_input_estimates(
            flow, math_model.INPUT_VAR_NAME, map_estimate, math_model)
        estimates_dict['External Inflows'][flow_varname] = estimates
        
    estimates_dict['Internal Stafs'] = {}
    for staf in internal_stafs:
        staf_name = "Internal Staf: " + staf.name
        if staf.origin_process.process_type == 'Storage':

            staf_estimates = get_input_estimates(
                    staf, math_model.INPUT_VAR_NAME, map_estimate, math_model)

        else:
            staf_estimates = get_staf_estimates(
                staf, math_model.STAF_VAR_NAME, map_estimate, math_model)

            tc_name = "TC: " + staf.name
        
            tc_estimates = get_staf_estimates(
                staf, math_model.TC_VAR_NAME, map_estimate, math_model)

            estimates_dict['Internal Stafs'][tc_name] = tc_estimates

        estimates_dict['Internal Stafs'][staf_name] = staf_estimates

    estimates_dict['External Outflows'] = {}
    for flow in external_outflows:
        staf_name = "Output Flow: " + flow.name
        tc_name = "TC: " + flow.name
        staf_estimates = get_staf_estimates(
            flow, math_model.STAF_VAR_NAME, map_estimate, math_model)

        tc_estimates = get_staf_estimates(
            flow, math_model.TC_VAR_NAME, map_estimate, math_model)

        estimates_dict['External Outflows'][staf_name] = staf_estimates
        estimates_dict['External Outflows'][tc_name] = tc_estimates
            
    return estimates_dict


def plot_posteriors(samples_dict):
    for param_type, param_dict in samples_dict.items():
        num_params = len(param_dict.keys())
        plot_width = 3
        plot_height = math.ceil(num_params/plot_width)
        fig = plt.figure(figsize=(plot_width*3, plot_height*3))
        i = 1
        for name, samples in param_dict.items():
            ax = fig.add_subplot(plot_height, plot_width, i, title=name)
            try:
                sns.kdeplot(samples, axes=ax)
            except Exception:
                ax.hist(samples)
            i = i+1
        fig.suptitle(param_type, y=1.08)
        plt.tight_layout(pad=0.4)


def display_estimates(estimates_dict):
    for param_type, param_dict in estimates_dict.items():
        print("Estimates of: " + param_type + "\n")
        for name, estimate in param_dict.items():
            print(name + ": " + str(estimate))
        print()
        print()


def display_parameters(
        external_inflows,
        internal_flows,
        external_outflows,
        trace,
        map_estimate,
        math_model):
    samples_dict = make_samples_dict(
        external_inflows,
        internal_flows,
        external_outflows,
        trace,
        math_model)

    estimates_dict = make_estimates_dict(
        external_inflows,
        internal_flows,
        external_outflows,
        map_estimate,
        math_model)

    plot_posteriors(samples_dict)
    display_estimates(estimates_dict)


def print_umis_diagram(res_inflows, res_dict, res_outflows):
    for x in res_inflows:
        print(x)
    
    print()
    print()

    for key, values in res_dict.items():
        print(key)
        for val in values.flows:
            print(val)
        print("stock: {}".format(values.stock))
        print()
        
    print()
    print()

    for x in res_outflows:
        print("Outflows")
        print(x)


def plot_var(trace, var_name, row=None, col=None):
    if row is not None:
        samples = trace[var_name, :, row, col]
    else:
        samples = trace[var_name]

    fig = plt.figure()
    ax = fig.add_subplot(111, title=var_name)
    try:
        sns.kdeplot(samples, axes=ax)
    except Exception as e:
        print(e)
        ax.hist(samples)
    plt.show()

