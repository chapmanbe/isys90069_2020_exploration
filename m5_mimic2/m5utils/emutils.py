from ipywidgets import interact,fixed
from IPython.display import clear_output, display, HTML
import ipywidgets as ipw
import numpy as np
import warnings
import io
import os
import pyarrow as pa
import pandas as pd
import altair as alt
from . description import drg, table_text
from markdown import markdown

DATADIR = "/home/shared/mimic_data/case_level"
GRAPH_WIDTH=400
GRAPH_HEIGHT=300

cases = (21372, 14125, 22498, 10299,
         2284, 15239, 4727, 8292, 9969,
         17805, 1766, 29839, 29657, 11401,
         19754, 4785, 19847, 6973, 27421, 18514)


debug_out = ipw.Output()
_debug = ipw.Label(value="")
def du(msg):
    _debug.value = _debug.value + " " +msg


def read_data():
    em_case_data = {}
    fails = []
    for c in cases:
        with open(os.path.join(DATADIR,"%d.feather"%c), "rb") as f0:
            try:
                em_case_data[c] = pa.deserialize(f0.read())
            except pa.ArrowInvalid:
                fails.append(c)
    return em_case_data

def get_em_case_options(em_case_data):
    em_case_options = list(em_case_data.keys())
    em_case_options.sort()
    return em_case_options

def get_em_table_options(em_case_data, case=None):
    if case == None:
        case = list(em_case_data.keys())[0]
    em_table_options = list(em_case_data[case].keys())
    em_table_options.sort()
    return em_table_options

def get_em_column_options(em_case_data, case=None):
    if case == None:
         case = list(em_case_data.keys())[0]
    em_column_options = {t:em_case_data[case][t].columns for t in em_table_options}
    for k,v in em_column_options.items():
        v.sort_values()
    return em_column_options

def plt_nominal(df, vizvar):

    tmp = df[vizvar].fillna("Missing").value_counts().to_frame().reset_index()
    c0 = alt.Chart(tmp).mark_bar().encode(
             x="index",
             y=vizvar
          ).properties(width=GRAPH_WIDTH,
                        height=GRAPH_HEIGHT)
    c1 = alt.Chart(df.fillna("Missing")).mark_circle().encode(
                    x="event_time:T",
                    y=vizvar,
                    tooltip = ["event_time:T",
                        "%s:N"%vizvar]
                    ).add_selection(
                                           alt.selection_interval(encodings=['x'], bind='scales',
                                                                  resolve='global')).properties(width=GRAPH_WIDTH,
                                                                                                height=GRAPH_HEIGHT)
    return c0, c1

def plt_numeric(df, vizvar):
    c0 = alt.Chart(df).mark_bar().encode(
             x=alt.X('%s:Q'%vizvar, bin=True),
             y='count()'
          ).properties(width=GRAPH_WIDTH,
                       height=GRAPH_HEIGHT)

    c1 = alt.Chart(df).mark_line(point=True).encode(
                    x="event_time:T",
                    y="%s:Q"%(vizvar),
                    tooltip = ["event_time:T",
                        "%s:Q"%vizvar]
                    ).add_selection(
                          alt.selection_interval(encodings=['x'], bind='scales',
                                                 resolve='global')
                    ).properties( width=GRAPH_WIDTH, height=GRAPH_HEIGHT
                    )#.configure_point( size=60)
    return c0, c1


def get_plts():
    df = em_case_data[em_case_select.value][em_table_select.value]
    df = df[df[em_column_select.value]==em_filter_select.value]

    if df.dtypes[em_viz_select.value] in {np.dtype("float64")}:
        c1, c2 = plt_numeric(df, em_viz_select.value)
    else:
        c1, c2 = plt_nominal(df, em_viz_select.value)
    return c1, c2

def draw_plot(c):
    with io.StringIO() as f:
        c.save(f, format="html")
        f.seek(0)
        html1 = f.read()
    du("saved plot")
    with plots_out1:
        display(HTML(html1))

def plt_data():

    c1, c2 = get_plts()
    c = c1|c2
    draw_plot(c)

def view_table():
    df = em_case_data[em_case_select.value][em_table_select.value]
    vs = em_slice_select.value
    with em_table_out:
        clear_output()
        display(df[vs:vs+5])

def comp_view_max():
    return max(0,em_case_data[em_case_select.value][em_table_select.value].shape[0]-5)

def update_view_max():
    em_slice_select.max = comp_view_max()

def update_case(change):
    case = change.new
    update_view_max()
    update_table(change)
    #view_table()
    #plt_data()

def update_table(change):
    update_view_max()
    with debug_out:
        em_column_select.options = em_column_options[em_table_select.value]

    view_table()
    update_column(change)


def set_columns():
    df = em_case_data[em_case_select.value][em_table_select.value]
    col = em_column_select.value
    cslabels = [("%s: %s"%(i[0],i[1]), i[0]) for i in  df[col].value_counts().iteritems()]
    cslabels.sort()

    # Update downstream choices
    em_viz_select.options = em_column_options[em_table_select.value]
    em_filter_select.options = cslabels

def update_column(change):
    col = change.new
    set_columns()
    with em_counts_out:
        display(df[col].value_counts().to_frame())
    plt_data()

def update_filter(change):
    plt_data()

def update_viz(change):
    plt_data()

def update_slice(change):
    view_table()

def init_view():
    em_case_select.value = em_case_options[0]
    em_table_select.value = em_table_options[0]
    em_column_select.options = em_column_options[em_table_select.value]
    set_columns()
    view_table()
    plt_data()

def on_em_reset(b):
    init_view()

## Read in data

em_case_data = read_data()
em_case_options = get_em_case_options(em_case_data)
em_table_options = get_em_table_options(em_case_data)
em_column_options = get_em_column_options(em_case_data)

## Define Widgets

em_table_out = ipw.Output()
em_counts_out = ipw.Output()
plots_out1 = ipw.Output(layout=ipw.Layout(width="100%", min_height="%dpix"%(GRAPH_HEIGHT+50),
                                                        max_height="%dpix"%(GRAPH_HEIGHT+100),
                                         border="solid", align="center"))

em_case_select = ipw.Dropdown(options = em_case_options)
em_table_select = ipw.Dropdown(options = em_table_options)
em_column_select = ipw.Dropdown(options = em_column_options[em_table_select.value])
em_slice_select = ipw.IntSlider(min=0, layout=ipw.Layout(width="100%"))

em_filter_select = ipw.Dropdown()
em_viz_select = ipw.Dropdown()
em_reset = ipw.Button(decription="reset", layout=ipw.Layout(width="100%", align="center"))#,  button_style='danger')
em_reset.style.button_color = 'lightgreen'

### Define label widgets

cw = ipw.Label(value="Select case")
tw = ipw.Label(value="Select table")
fw = ipw.Label(value="Select filter variable")
vw = ipw.Label(value="Select filter value")
pw = ipw.Label(value="Select plot variable")

## Set call backs
em_case_select.observe(update_case, names="value", type="change")
em_table_select.observe(update_table, names='value', type='change')
em_column_select.observe(update_column, names="value", type="change")
em_filter_select.observe(update_filter, names="value", type="change")
em_viz_select.observe(update_viz, names="value", type="change")
em_slice_select.observe(update_slice, names="value", type="change")
em_reset.on_click(on_em_reset)

explore_mimic = ipw.TwoByTwoLayout(
        top_left=ipw.VBox([em_reset,
                           ipw.HBox([ipw.VBox([cw, em_case_select]),
                                     ipw.VBox([tw, em_table_select]),
                                     ipw.VBox([fw, em_column_select]),
                                     ipw.VBox([vw, em_filter_select]),
                                     ipw.VBox([pw, em_viz_select])]),
                           em_slice_select,
                           em_table_out],
                           layout=ipw.Layout(width='100%',
                                             min_height='200px',
                                             border="solid")),
        bottom_left=ipw.HBox([plots_out1]), layout=ipw.Layout(width="100%"))

descriptions = ipw.Tab()
children = [ipw.HTML(value=markdown(table_text[t])) for t in em_table_options]
children.append(ipw.HTML(drg))
tmp = em_table_options[:]
tmp.append("DRG")
for i in range(len(tmp)):
    descriptions.set_title(i,tmp[i])
descriptions.children = children
