from jinja2 import Template
import jinja2
import pymysql
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
MIMICHOST="35.233.174.193"
from IPython.display import display, clear_output, HTML
from ipywidgets import interactive, interact, fixed
import ipywidgets as widgets
from markdown import markdown
import networkx as nx

dt1 = Template("""
<table>
{% for key, value in data.items() %}
   <tr>
        <th> {{ key }} </th>
        <td> {{ value }} </td>
   </tr>
{% endfor %}
</table>""")

t2 = Template(
"""<table>
{%- for row in data|batch(ncols, '&nbsp;') %}
  <tr>
  {%- for column in row %}
    <td>{{ column }}</td>
  {%- endfor %}
  </tr>
{%- endfor %}
</table>""")

t3 = Template("""
<pre style="white-space: pre !important;"></pre>
{% block content %}
<h3 align="center"> {{title}} </h3>
    <img src="{{ fname }}" alt="image alt text" />
{% endblock %}
""")


def get_mimic_connection():
    conn = pymysql.connect(host=MIMICHOST,
                       port=3306,user="jovyan",
                       passwd='jovyan',db='mimic2')
    return conn

def get_tables(conn):
    return pd.read_sql("SHOW TABLES", conn)
def get_table_names(conn):
    return [row["Tables_in_mimic2"]
               for _,row in get_tables(conn).iterrows()]

def get_table_descriptons(conn):
    return {t:pd.read_sql("DESCRIBE %s"%t,conn)
        for t in get_table_names(conn)}

def get_table_columns(table_descriptions):
    return {t:set(f["Field"]) for t,f in table_descriptions.items()}


def view_table(table, num, conn, rand=False):
    if rand:
        return pd.read_sql("""SELECT * FROM %s ORDER BY RAND() LIMIT %d"""%(table, num), conn)
    else:
        return pd.read_sql("""SELECT * FROM %s LIMIT %d"""%(table, num), conn)


def ddict(d):
    return dt1.render(data=d)


def dlist(l, ncols=5, sort=False):

    if sort:
        l.sort()
    return t2.render(data=l, ncols=ncols)




def get_db_graph(tbls, tbl, col):
    tables = [t for t in tbls if col in tbls[t] and t != tbl]
    g = nx.DiGraph()
    g.add_edges_from([(col,t) for t in tables])
    return g
def view_db_graph(tbls, tbl, col):
    g = get_db_graph(tbls, tbl, col)
    ag = nx.nx_pydot.to_pydot(g)
    fname = "%s_%s.png"%(tbl,col)
    ag.write_png(fname)
    return HTML(t3.render(title="(%s, %s)"%(tbl, col), fname=fname))
