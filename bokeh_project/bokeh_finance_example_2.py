import pandas as pd
import yfinance as yf

from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Select, DataTable, TableColumn
from bokeh.layouts import column, row
from bokeh.plotting import figure, show
from yfinance import ticker

DEFAULT_TICKERS = ['AAPL', 'GOOG', 'MSFT', 'NFLX', "TSLA"]
START, END = "2018-01-01", "2020-01-01"

def load_ticker(tickers):
    df = yf.download(tickers, start=START, end=END)
    return df["Close"].dropna()

static_data = load_ticker(DEFAULT_TICKERS)

def get_data(data, t1, t2):
    df = data[[t1,t2]]
    returns = df.pct_change().add_suffix("_returns")
    df = pd.concat([df, returns], axis=1)
    df.rename(columns={t1:'t1',t2:'t2', t1+"_returns":"t1_returns", t2+"_returns":"t2_returns"}, inplace=True)
    return df.dropna()

def nix(val, lst):
    return [x for x in lst if x != val]

ticker1 = Select(value='AAPL', options=nix('GOOG', DEFAULT_TICKERS))
ticker2 = Select(value='GOOG', options=nix('AAPL', DEFAULT_TICKERS))

data = get_data(static_data, ticker1.value, ticker2.value)
source = ColumnDataSource(data=data)

# Descriptive Stats
stats = round(data.describe().reset_index(), 2)
stats_source = ColumnDataSource(data=stats)
stat_columns = [TableColumn(field=col, title=col) for col in stats.columns]
data_table = DataTable(source=stats_source, columns=stat_columns, width=400, height=350, index_position=None)

# Plots
corr_tools = 'pan,wheel_zoom,box_select,reset'
tools = 'pan,wheel_zoom,xbox_select,reset'

corr = figure(width=350, height=350, tools=corr_tools)
corr.circle('t1_returns', 't2_returns', size=2, source=source,
            selection_color="firebrick", alpha=0.6, nonselection_alpha=0.1, selection_alpha=0.4)

ts1 = figure(width=900, height=250, tools=tools, x_axis_type='datetime', active_drag="xbox_select")
ts1.line('Date', 't1', source=source)
ts1.circle('Date', 't1', size=1, source=source, color=None, selection_color="firebrick")

ts2 = figure(width=900, height=250, tools=tools, x_axis_type='datetime', active_drag="xbox_select")
ts2.x_range = ts1.x_range
ts2.line('Date', 't2', source=source)
ts2.circle('Date', 't2', size=1, source=source, color=None, selection_color="firebrick")

# Callbacks
def ticker1_change(attrname, old, new):
    ticker2.options = nix(new, DEFAULT_TICKERS)
    update()

def ticker2_change(attrname, old, new):
    ticker1.options = nix(new, DEFAULT_TICKERS)
    update()

def update(data=static_data):
    t1, t2 = ticker1.value, ticker2.value
    df = get_data(data, t1, t2)
    source.data = df
    stats_source.data = round(df.describe().reset_index(), 2)
    corr.title.text = f'{t1} returns vs. {t2} returns'
    ts1.title.text, ts2.title.text = t1, t2

ticker1.on_change('value', ticker1_change)
ticker2.on_change('value', ticker2_change)

# Layout
widgets = column(ticker1, ticker2, data_table)
main_row = row(corr, widgets)
series = column(ts1, ts2)
layout = column(main_row, series)

curdoc().add_root(layout)
curdoc().title = "Stocks"