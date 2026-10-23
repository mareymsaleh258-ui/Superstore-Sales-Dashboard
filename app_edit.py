# ============================================================
# Imports
# ============================================================
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
# ============================================================
# Load Data
# ============================================================
df = pd.read_csv('data/cleaned_data.csv')
df['Order Date'] = pd.to_datetime(df['Order Date'])

# ============================================================
# App Initialization
# ============================================================
app = dash.Dash(__name__)
app.title = "Superstore Sales Dashboard"

# ============================================================
# Filter Options
# ============================================================
regions    = ['All'] + sorted(df['Region'].unique().tolist())
categories = ['All'] + sorted(df['Category'].unique().tolist())
years      = sorted(df['Year'].unique().tolist())

# ============================================================
# Color Palettes
# ============================================================
WARM_PALETTE = ['#f4a7b9', '#f9c784', '#f7a278', '#f3d5b5', '#e8a0bf', '#ffd6a5']
COOL_PALETTE = ['#80cbc4', '#80b3d4', '#a5c8a5', '#b0c4de', '#90c9c9', '#a8d5ba']

def warm(i): return WARM_PALETTE[i % len(WARM_PALETTE)]
def cool(i): return COOL_PALETTE[i % len(COOL_PALETTE)]

OUTLIER_COLOR = '#e74c3c'

# ============================================================
# Helper: format number
# ============================================================
def fmt(val):
    if abs(val) >= 1_000_000: return f"{val/1_000_000:.1f}M"
    elif abs(val) >= 1_000:   return f"{val/1_000:.1f}k"
    else:                     return f"{val:.0f}"

# ============================================================
# Layout
# ============================================================
app.layout = html.Div([

    html.Div([
        html.H1("🛒 Superstore Sales Dashboard",
                style={'color': 'white', 'textAlign': 'center', 'margin': '0', 'padding': '20px'}),
    ], style={'backgroundColor': '#2c3e50'}),

    html.Div([
        html.Div([
            html.Label("Region:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(id='region-filter',
                         options=[{'label': r, 'value': r} for r in regions],
                         value='All', clearable=False)
        ], style={'width': '30%', 'display': 'inline-block', 'marginRight': '3%'}),
        html.Div([
            html.Label("Category:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(id='category-filter',
                         options=[{'label': c, 'value': c} for c in categories],
                         value='All', clearable=False)
        ], style={'width': '30%', 'display': 'inline-block', 'marginRight': '3%'}),
        html.Div([
            html.Label("Year Range:", style={'fontWeight': 'bold'}),
            dcc.RangeSlider(id='year-filter',
                            min=min(years), max=max(years), step=1,
                            value=[min(years), max(years)],
                            marks={y: str(y) for y in years})
        ], style={'width': '30%', 'display': 'inline-block'}),
    ], style={'padding': '20px', 'backgroundColor': '#ecf0f1', 'marginBottom': '10px'}),

    dcc.Tabs([
        dcc.Tab(label='Comparison', children=[
            html.Div([
                html.Div([dcc.Graph(id='column-chart')],  style={'width': '48%', 'display': 'inline-block'}),
                html.Div([dcc.Graph(id='bar-chart')],     style={'width': '48%', 'display': 'inline-block', 'marginLeft': '2%'}),
            ]),
            html.Div([
                html.Div([dcc.Graph(id='stacked-column-chart')], style={'width': '48%', 'display': 'inline-block'}),
                html.Div([dcc.Graph(id='stacked-bar-chart')],    style={'width': '48%', 'display': 'inline-block', 'marginLeft': '2%'}),
            ]),
            html.Div([
                html.Div([dcc.Graph(id='clustered-column-chart')], style={'width': '48%', 'display': 'inline-block'}),
                html.Div([dcc.Graph(id='clustered-bar-chart')],    style={'width': '48%', 'display': 'inline-block', 'marginLeft': '2%'}),
            ]),
        ]),
        dcc.Tab(label='Relationship', children=[
            html.Div([
                html.Div([dcc.Graph(id='scatter-chart')], style={'width': '48%', 'display': 'inline-block'}),
                html.Div([dcc.Graph(id='bubble-chart')],  style={'width': '48%', 'display': 'inline-block', 'marginLeft': '2%'}),
            ]),
        ]),
        dcc.Tab(label='Distribution', children=[
            html.Div([
                html.Div([dcc.Graph(id='histogram-chart')], style={'width': '48%', 'display': 'inline-block'}),
                html.Div([dcc.Graph(id='box-chart')],       style={'width': '48%', 'display': 'inline-block', 'marginLeft': '2%'}),
            ]),
            html.Div([
                html.Div([dcc.Graph(id='violin-chart')], style={'width': '50%', 'margin': 'auto'}),
            ]),
        ]),
        dcc.Tab(label='Time-Series', children=[
            html.Div([
                html.Div([dcc.Graph(id='line-chart')], style={'width': '48%', 'display': 'inline-block'}),
                html.Div([dcc.Graph(id='area-chart')], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '2%'}),
            ]),
        ]),
    ]),

], style={'fontFamily': 'Arial', 'margin': '0', 'padding': '0'})


# ============================================================
# Callback
# ============================================================
@app.callback(
    [Output('column-chart',           'figure'),
     Output('bar-chart',              'figure'),
     Output('stacked-column-chart',   'figure'),
     Output('stacked-bar-chart',      'figure'),
     Output('clustered-column-chart', 'figure'),
     Output('clustered-bar-chart',    'figure'),
     Output('scatter-chart',          'figure'),
     Output('bubble-chart',           'figure'),
     Output('histogram-chart',        'figure'),
     Output('box-chart',              'figure'),
     Output('violin-chart',           'figure'),
     Output('line-chart',             'figure'),
     Output('area-chart',             'figure')],
    [Input('region-filter',   'value'),
     Input('category-filter', 'value'),
     Input('year-filter',     'value')]
)
def update_charts(selected_region, selected_category, selected_years):

    filtered = df.copy()
    if selected_region != 'All':
        filtered = filtered[filtered['Region'] == selected_region]
    if selected_category != 'All':
        filtered = filtered[filtered['Category'] == selected_category]
    filtered = filtered[
        (filtered['Year'] >= selected_years[0]) &
        (filtered['Year'] <= selected_years[1])
    ]

    # ----------------------------------------------------------
    # SHARED: category color map (highest sales = warm, rest = cool)
    # ----------------------------------------------------------
    cat_sales   = filtered.groupby('Category')['Sales'].sum().sort_values(ascending=False)
    sorted_cats = cat_sales.index.tolist()
    top_cat     = sorted_cats[0] if sorted_cats else None

    cat_color_map = {}
    _ci = 0
    for cat in sorted_cats:
        if cat == top_cat:
            cat_color_map[cat] = warm(0)
        else:
            cat_color_map[cat] = cool(_ci)
            _ci += 1

    # ===========================================================
    # LEGEND CLICK FIX:
    # Split data into TWO real traces (top + others) instead of
    # using dummy invisible traces. Each real trace has its own
    # legend entry — clicking hides/shows the actual bars.
    # ===========================================================

    # ----------------------------------------------------------
    # 1. Column Chart — Total Sales by Category
    # ----------------------------------------------------------
    col_data = (filtered.groupby('Category')['Sales'].sum()
                .reset_index().sort_values('Sales', ascending=False))
 
    column_fig = go.Figure()
    for cat in col_data['Category']:
        d      = col_data[col_data['Category'] == cat]
        is_top = (cat == top_cat)
        label  = f'  Highest: {cat} ★' if is_top else cat
        column_fig.add_trace(go.Bar(
            x=d['Category'], y=d['Sales'],
            name=label, marker_color=cat_color_map[cat],
            text=[fmt(v) for v in d['Sales']], textposition='outside'
        ))
    column_fig.update_layout(
        title='Total Sales by Category', barmode='group',
        xaxis_title='Category', yaxis_title='Total Sales ($)', showlegend=True
    )
    # ----------------------------------------------------------
    # 2. Bar Chart — Total Profit by Sub-Category
    # ----------------------------------------------------------
    bar_data  = (filtered.groupby('Sub-Category')['Profit'].sum()
                 .reset_index().sort_values('Profit', ascending=True))
    top_sub   = bar_data.iloc[-1]['Sub-Category'] if not bar_data.empty else None
    bar_top   = bar_data[bar_data['Sub-Category'] == top_sub]
    bar_other = bar_data[bar_data['Sub-Category'] != top_sub]

    bar_fig = go.Figure()
    if not bar_other.empty:
        bar_fig.add_trace(go.Bar(
            x=bar_other['Profit'], y=bar_other['Sub-Category'],
            orientation='h', name='Others', marker_color=cool(0),
            text=[fmt(v) for v in bar_other['Profit']], textposition='outside'
        ))
    if not bar_top.empty:
        bar_fig.add_trace(go.Bar(
            x=bar_top['Profit'], y=bar_top['Sub-Category'],
            orientation='h', name=f'Highest: {top_sub} \u2605', marker_color=warm(0),
            text=[fmt(v) for v in bar_top['Profit']], textposition='outside'
        ))
    bar_fig.update_layout(
        title='Total Profit by Sub-Category',
        xaxis_title='Total Profit ($)', yaxis_title='Sub-Category', showlegend=True
    )

    # ----------------------------------------------------------
    # 3. Stacked Column — Sales by Region & Category
    #    One trace per (region × category) so clicking a legend entry
    #    hides/shows that specific region's bars.
    #    Legend label = "Region — Category", top region gets warm color.
    # ----------------------------------------------------------
    stacked_col_data = filtered.groupby(['Region', 'Category'])['Sales'].sum().reset_index()
    reg_totals_sc    = stacked_col_data.groupby('Region')['Sales'].sum().sort_values(ascending=False)
    top_region_sc    = reg_totals_sc.index[0]
    region_order_sc  = reg_totals_sc.index.tolist()
    cats_sc          = sorted(stacked_col_data['Category'].unique().tolist())

    # Assign a fixed cool color per category index (warm reserved for top region)
    cat_idx_sc = {cat: i for i, cat in enumerate(cats_sc)}

    stacked_col_fig = go.Figure()
    for region in region_order_sc:
        is_top = (region == top_region_sc)
        for cat in cats_sc:
            row = stacked_col_data[
                (stacked_col_data['Region'] == region) &
                (stacked_col_data['Category'] == cat)
            ]
            if row.empty:
                continue
            val   = row['Sales'].iloc[0]
            color = warm(cat_idx_sc[cat]) if is_top else cool(cat_idx_sc[cat])
            label = f"{region} \u2605 \u2014 {cat}" if is_top else f"{region} \u2014 {cat}"
            stacked_col_fig.add_trace(go.Bar(
                x=[region], y=[val],
                name=label, marker_color=color,
                text=fmt(val), textposition='inside',
                legendgroup=region,
                showlegend=True
            ))
    stacked_col_fig.update_layout(
        title='Sales by Region and Category',
        xaxis_title='Region', yaxis_title='Total Sales ($)',
        barmode='stack', showlegend=True
    )

    # ----------------------------------------------------------
    # 4. Stacked Bar — Orders by Segment & Ship Mode
    #    One trace per (segment × ship mode) for working legend clicks.
    # ----------------------------------------------------------
    stacked_bar_data = filtered.groupby(['Segment', 'Ship Mode'])['Order ID'].count().reset_index()
    stacked_bar_data.columns = ['Segment', 'Ship Mode', 'Orders']
    seg_totals_sb    = stacked_bar_data.groupby('Segment')['Orders'].sum().sort_values(ascending=True)
    top_segment_sb   = seg_totals_sb.index[-1]
    segment_order_sb = seg_totals_sb.index.tolist()
    ship_modes_list  = sorted(stacked_bar_data['Ship Mode'].unique().tolist())
    sm_idx           = {sm: i for i, sm in enumerate(ship_modes_list)}

    stacked_bar_fig = go.Figure()
    for seg in segment_order_sb:
        is_top = (seg == top_segment_sb)
        for sm in ship_modes_list:
            row = stacked_bar_data[
                (stacked_bar_data['Segment'] == seg) &
                (stacked_bar_data['Ship Mode'] == sm)
            ]
            if row.empty:
                continue
            val   = row['Orders'].iloc[0]
            color = warm(sm_idx[sm]) if is_top else cool(sm_idx[sm])
            label = f"{seg} \u2605 \u2014 {sm}" if is_top else f"{seg} \u2014 {sm}"
            stacked_bar_fig.add_trace(go.Bar(
                y=[seg], x=[val], orientation='h',
                name=label, marker_color=color,
                text=fmt(val), textposition='inside',
                legendgroup=seg,
                showlegend=True
            ))
    stacked_bar_fig.update_layout(
        title='Orders by Segment and Ship Mode',
        xaxis_title='Number of Orders', yaxis_title='Segment',
        barmode='stack', showlegend=True
    )

    # ----------------------------------------------------------
    # 5. Clustered Column — Sales vs Profit by Category
    # ----------------------------------------------------------
    cc_data  = (filtered.groupby('Category')[['Sales', 'Profit']].sum()
                .reset_index().sort_values('Sales', ascending=False))
    top_cc   = cc_data.iloc[0]['Category'] if not cc_data.empty else None
    cc_top   = cc_data[cc_data['Category'] == top_cc]
    cc_other = cc_data[cc_data['Category'] != top_cc]

    clustered_col_fig = go.Figure()
    if not cc_top.empty:
        clustered_col_fig.add_trace(go.Bar(
            x=cc_top['Category'], y=cc_top['Sales'],
            name=f'Sales \u2014 {top_cc} \u2605', marker_color=warm(0),
            text=[fmt(v) for v in cc_top['Sales']], textposition='outside'
        ))
        clustered_col_fig.add_trace(go.Bar(
            x=cc_top['Category'], y=cc_top['Profit'],
            name=f'Profit \u2014 {top_cc} \u2605', marker_color=warm(1),
            text=[fmt(v) for v in cc_top['Profit']], textposition='outside'
        ))
    if not cc_other.empty:
        clustered_col_fig.add_trace(go.Bar(
            x=cc_other['Category'], y=cc_other['Sales'],
            name='Sales \u2014 Others', marker_color=cool(0),
            text=[fmt(v) for v in cc_other['Sales']], textposition='outside'
        ))
        clustered_col_fig.add_trace(go.Bar(
            x=cc_other['Category'], y=cc_other['Profit'],
            name='Profit \u2014 Others', marker_color=cool(1),
            text=[fmt(v) for v in cc_other['Profit']], textposition='outside'
        ))
    clustered_col_fig.update_layout(
        title='Sales vs Profit by Category',
        barmode='group', xaxis_title='Category', yaxis_title='Amount ($)', showlegend=True
    )

    # ----------------------------------------------------------
    # 6. Clustered Bar — Sales vs Profit by Region
    # ----------------------------------------------------------
    cb_data  = (filtered.groupby('Region')[['Sales', 'Profit']].sum()
                .reset_index().sort_values('Sales', ascending=True))
    top_cb   = cb_data.iloc[-1]['Region'] if not cb_data.empty else None
    cb_top   = cb_data[cb_data['Region'] == top_cb]
    cb_other = cb_data[cb_data['Region'] != top_cb]

    clustered_bar_fig = go.Figure()
    if not cb_top.empty:
        clustered_bar_fig.add_trace(go.Bar(
            y=cb_top['Region'], x=cb_top['Sales'], orientation='h',
            name=f'Sales \u2014 {top_cb} \u2605', marker_color=warm(0),
            text=[fmt(v) for v in cb_top['Sales']], textposition='outside'
        ))
        clustered_bar_fig.add_trace(go.Bar(
            y=cb_top['Region'], x=cb_top['Profit'], orientation='h',
            name=f'Profit \u2014 {top_cb} \u2605', marker_color=warm(1),
            text=[fmt(v) for v in cb_top['Profit']], textposition='outside'
        ))
    if not cb_other.empty:
        clustered_bar_fig.add_trace(go.Bar(
            y=cb_other['Region'], x=cb_other['Sales'], orientation='h',
            name='Sales \u2014 Others', marker_color=cool(0),
            text=[fmt(v) for v in cb_other['Sales']], textposition='outside'
        ))
        clustered_bar_fig.add_trace(go.Bar(
            y=cb_other['Region'], x=cb_other['Profit'], orientation='h',
            name='Profit \u2014 Others', marker_color=cool(1),
            text=[fmt(v) for v in cb_other['Profit']], textposition='outside'
        ))
    clustered_bar_fig.update_layout(
        title='Sales vs Profit by Region',
        barmode='group', xaxis_title='Amount ($)', yaxis_title='Region', showlegend=True
    )

    # ----------------------------------------------------------
    # 7. Scatter — Profit vs Sales
    # ----------------------------------------------------------
    scatter_fig = px.scatter(
        filtered, x='Sales', y='Profit', color='Region',
        title='Profit by Sales',
        labels={'Sales': 'Sales ($)', 'Profit': 'Profit ($)'},
        color_discrete_map=cat_color_map
    )
    scatter_fig.update_layout(
        xaxis_title='Sales ($)', yaxis_title='Profit ($)', showlegend=True
    )

    # ----------------------------------------------------------
    # 8. Bubble Chart - Sales vs Profit vs Quantity
    # ----------------------------------------------------------
    bubble_fig = px.scatter(
        filtered, x='Sales', y='Profit', size='Quantity', color='Category',
        title='Sales vs Profit vs Quantity (Bubble Chart)',
        labels={'Sales': 'Sales ($)', 'Profit': 'Profit ($)', 'Quantity': 'Quantity'},
        color_discrete_map=cat_color_map, size_max=40
    )
    bubble_fig.update_layout(xaxis_title='Sales ($)', yaxis_title='Profit ($)', showlegend=True)

    # ----------------------------------------------------------
    # 9. Histogram — Distribution of Quantity (univariate)
    #    Highest bar = warm(0)/pink, rest = cool(0)
    # ----------------------------------------------------------
    sm_list = sorted(filtered['Ship Mode'].unique().tolist())
    sm_hist_color = {sm: (warm(0) if i == 0 else cool(i)) for i, sm in enumerate(sm_list)}
 
    histogram_fig = px.histogram(
        filtered, x='Quantity', color='Ship Mode', nbins=14,
        title='Distribution of Quantity by Ship Mode',
        labels={'Quantity': 'Quantity', 'count': 'Frequency'},
        color_discrete_map=sm_hist_color
    )
    histogram_fig.update_layout(xaxis_title='Quantity', yaxis_title='Frequency', showlegend=True)

    # ----------------------------------------------------------
    # 10. Box Chart — Profit by Ship Mode (horizontal)
    # ----------------------------------------------------------

    reg_med_order_box = (filtered.groupby('Category')['Profit'].median()
                         .sort_values(ascending=False).index.tolist())
    top_reg_box   = reg_med_order_box[0]
    reg_box_color = {r: (warm(0) if r == top_reg_box else cool(i))
                     for i, r in enumerate(reg_med_order_box)}
 
    box_fig = px.box(
        filtered, x='Profit', y='Category', color='Category',
        title='Profit Distribution by Category',
        labels={'Profit': 'Profit ($)', 'Category': ''},
        color_discrete_map=reg_box_color,
        category_orders={'Category': reg_med_order_box},
        orientation='h'
    )
    box_fig.update_layout(
        xaxis_title='Profit ($)', yaxis_title='',
        yaxis=dict(tickangle=0),
        showlegend=True
    )
 

    # ----------------------------------------------------------
    # 11. Violin — Sales by Region
    # ----------------------------------------------------------
    reg_med_order = (filtered.groupby('Region')['Sales'].median()
                     .sort_values(ascending=False).index.tolist())
    top_reg_v = reg_med_order[0]
    reg_color_map = {r: (warm(0) if r == top_reg_v else cool(i))
                     for i, r in enumerate(reg_med_order)}

    violin_fig = px.violin(
        filtered, x='Region', y='Sales', color='Region',
        title='Sales Distribution by Region',
        labels={'Sales': 'Sales ($)', 'Region': 'Region'},
        color_discrete_map=reg_color_map,
        category_orders={'Region': reg_med_order},
        box=True
    )
    violin_fig.update_layout(xaxis_title='Region', yaxis_title='Sales ($)', showlegend=True)

    # ----------------------------------------------------------
    # 12. Line — Monthly Sales Trend
    # ----------------------------------------------------------
    line_data = filtered.groupby('Year-Month')['Sales'].sum().reset_index()
    line_fig  = px.line(
        line_data, x='Year-Month', y='Sales',
        title='Monthly Sales Trend',
        labels={'Sales': 'Total Sales ($)', 'Year-Month': 'Month'},
        color_discrete_sequence=[warm(0)]
    )
    line_fig.update_layout(
        xaxis_title='Month', yaxis_title='Total Sales ($)',
        showlegend=True, yaxis=dict(rangemode='tozero')
    )
    line_fig.update_xaxes(tickangle=0)

    # ----------------------------------------------------------
    # 13. Area — Monthly Profit Trend
    # ----------------------------------------------------------
    area_data = filtered.groupby('Year-Month')['Profit'].sum().reset_index()
    area_fig  = px.area(
        area_data, x='Year-Month', y='Profit',
        title='Monthly Profit Trend',
        labels={'Profit': 'Total Profit ($)', 'Year-Month': 'Month'},
        color_discrete_sequence=[cool(0)]
    )
    area_fig.update_layout(
        xaxis_title='Month', yaxis_title='Total Profit ($)',
        showlegend=True, yaxis=dict(rangemode='tozero')
    )
    area_fig.update_xaxes(tickangle=0)

    return (column_fig, bar_fig, stacked_col_fig, stacked_bar_fig,
            clustered_col_fig, clustered_bar_fig, scatter_fig, bubble_fig,
            histogram_fig, box_fig, violin_fig, line_fig, area_fig)


# ============================================================
# Run App
# ============================================================


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8050)))