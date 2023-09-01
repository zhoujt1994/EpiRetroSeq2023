import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, MATCH
import plotly.express as px
import plotly.graph_objects as go
from vis.config.dataset_config import dataset_config
from vis.config.plot_config import plot_config
from vis.datacenter.data_center_tsne import get_hidden_options, get_active_and_background_data, get_gene_name
from vis.utils.plot_utils import n_cell_to_marker_size, assign_colors_to_co_clusters
from vis.enums.plot_type_enum import PlotType, ActivateType
from vis.app import app


merge_plot_details_unique_list = []

color_sequence = assign_colors_to_co_clusters(cluster_count=dataset_config.co_clusters)
color_mapping_dict = {str(index): color_sequence[index] for index in range(len(color_sequence))}

fig_name_set = set()


def get_scatter_config_list_tsne(modality, region, subregion_list, cell_type_list, plot_type_list,
                                 gene_name_list, down_sample, coords, target_list, co_cluster_list, gene_zscore):
    if None in [region, modality, subregion_list, cell_type_list, plot_type_list,
                down_sample, coords, target_list]:
        return None

    subregion_list = ["ALL"] if "ALL" in subregion_list else subregion_list
    cell_type_list = ["ALL"] if "ALL" in cell_type_list else cell_type_list
    co_cluster_list = ["ALL"] if "ALL" in co_cluster_list else co_cluster_list
    target_list = ["ALL"] if "ALL" in target_list or PlotType.TARGET.value not in plot_type_list else target_list

    draw_details_list = [
        {
            'plot': plot,
            'modality': modality,
            'region': region,
            'subregion': ','.join(subregion_list),
            'gene_name': gene_name if plot in [PlotType.MC_EXP.value, PlotType.GENE_EXP.value]
                         and gene_name else '',
            'cell_type': ','.join(cell_type_list),
            'co_cluster':','.join(list(map(str, co_cluster_list))),
            'target': ','.join(target_list) if plot == PlotType.TARGET.value else '',
            'down_sample': down_sample,
            'coords': coords,
            'zscore': gene_zscore if plot in [PlotType.GENE_EXP.value, PlotType.MC_EXP.value] else ""
        }
        for gene_name in gene_name_list or ['']
        for plot in plot_type_list if (not (plot in [PlotType.GENE_EXP.value] and not gene_name))
    ]
    return draw_details_list


def get_scatter_table_content_tsne(body, td_key_list):
    if type(body) is not list or not body:
        return []
    plot_details_list = []
    for tr in body:
        tds = tr['props']['children']
        td_value_list = []
        for td in tds:
            data = td['props']['children']
            td_value_list.append(data)
        merged_dict = {key: value for key, value in zip(td_key_list, td_value_list)}
        plot_details_list.append(merged_dict)
    return plot_details_list


def add_fig_wrapper_to_content(fig_list, graphs_content):
    for fig in fig_list:
        fig_card = dbc.Card(
            [
                dbc.CardHeader(fig['name']),
                dbc.Container(
                    [
                        fig['fig']
                    ],
                    className='pt-3'
                )
            ],
            style={'width': '49%', 'display': 'inline-block', 'margin': '5px'},
        )
        graphs_content.append(fig_card)
    return graphs_content


def create_tsne_plot_layout(coords="T-SNE", down_sample='10000 (Fast)', brain_regions=None):

    click_form = dbc.Form(
        [
            dbc.Row(
                [
                    dbc.Label('Coordinates', html_for='coords-dropdown'),
                    dcc.Dropdown(
                        id='coords-dropdown',
                        options=[{'label': name, 'value': name}
                                 for name in dataset_config.coord_names],
                        value=coords,
                        clearable=False),
                    dbc.FormText('Coordinates of scatter plots')
                ]
            ),
            dbc.Row(
                [
                    dbc.Label('Down Sample Cells', html_for='down-sample-dropdown'),
                    dcc.Dropdown(
                        id='down-sample-dropdown',
                        options=[{'label': '10000 (Fast)', 'value': '10000 (Fast)'},
                                 {'label': '50000 (Slow)', 'value': '50000 (Slow)'},
                                 {'label': 'ALL (Very Slow)', 'value': 'ALL (Very Slow)'}],
                        value=down_sample,
                        clearable=False
                    ),
                    dbc.FormText('Number of cells plotted on each scatter plot.')
                ]
            ),
            dbc.Row(
                [
                    html.Div([
                        dbc.Label('Enable Z-Score :',
                                  html_for='zscore-color-scale-checkbox',
                                  style={
                                      'font-weight': 'bold',
                                      'font-size': '16px',
                                      'margin-right': '10px',
                                      'margin-top': '5px'
                                  }
                                  ),
                        dbc.Checklist(
                                options=[{'label': '', 'value': 'True'}],
                                value=['False'],
                                id="zscore-color-scale-checkbox",
                                inline=True,
                                switch=True,
                                ),
                        ], style={'display': 'flex', 'align-items': 'center'}),
                    dbc.FormText('Perform Z-Score Normalization on mCH or RNA Values.')
                ],
                className="align-items-center"
            ),
            dbc.Row(
                dbc.Col(
                    dbc.Button("Add Plot", id="add-plot-button", color="danger", style={'width': '50%'}),
                    width={'size': 10, 'offset': 6}  # Offset by 6 columns to align to the right
                ),
                style={'margin': '20px'}
            ),
        ]
    )

    active_cells_form_1 = dbc.Form(
        [
            dbc.Row(
                [
                    dbc.Label('Select by Modality Type', html_for='brain-modality-type-select-dropdown'),
                    dcc.Dropdown(
                        id='brain-modality-type-select-dropdown',
                        options=[{'label': modality, 'value': modality}
                                 for modality in dataset_config.modalities],
                        value=None,
                        placeholder='Select a Modality Type',
                        clearable=False
                    ),
                    dbc.FormText('Only color cells from these Modality Types.')
                ]
            ),
            dbc.Row(
                [
                    dbc.Label('Select by Brain Region', html_for='brain-region-select-dropdown'),
                    dcc.Dropdown(
                        id='brain-region-select-dropdown',
                        options=[{'label': dataset_config.region_mapping['region_name_to_acc'][region], 'value': region}
                                 for region in dataset_config.region_mapping["region_to_subregion"].keys()],
                        value=brain_regions,
                        placeholder='Select a Region',
                        clearable=False
                    ),
                    dbc.FormText('Only color cells from these brain subregions.')
                ]
            ),
            dbc.Row(
                [
                    dbc.Label('Select by Brain SubRegions', html_for='brain-subregion-select-dropdown'),
                    dcc.Dropdown(
                        id='brain-subregion-select-dropdown',
                        options=[],
                        multi=True,
                        value=['ALL'],
                        placeholder='Select SubRegions'
                    ),
                    dbc.FormText('Only color cells from these brain regions.')
                ]
            ),
            dbc.Row(
                [
                    dbc.Label('Active Control (Optional)'),
                    dbc.Checklist(
                        id='brain-active-control-select-checkbox',
                        options=[
                            {'label': ActivateType.CELL_TYPES.value, 'value': ActivateType.CELL_TYPES.value},
                            {'label': ActivateType.CO_CLUSTER.value, 'value': ActivateType.CO_CLUSTER.value}
                        ],
                        value=[],
                        inline=True
                    ),
                    dbc.FormText('Default To ALL: Select cells with precision')
                ],
                justify="center",
            ),
        ]
    )

    active_cells_form_2 = dbc.Form(
        [
            dbc.Row(
                [
                    dbc.Label('Plot Type', html_for='brain-plot-type-select-dropdown'),
                    dcc.Dropdown(
                        id='brain-plot-type-select-dropdown',
                        options=[],
                        value=None,
                        clearable=True,
                        placeholder='Choose Plot Type for Current Setup',
                        multi=True,
                    ),
                    dbc.FormText('Only color cells from these Draw Types.')
                ]
            ),
            dbc.Row(
                [
                    dbc.Label('Genes', html_for='brain-gene-input'),
                    dcc.Dropdown(
                        id='brain-gene-input',
                        placeholder='Input a gene name, e.g. Gad1',
                        multi=True
                    ),
                    dbc.FormText('Gene of the scatter plot.')
                ],
            ),
            dbc.Row(
                [
                    dbc.Label('Select by Cell Types', html_for='brain-cell-type-select-dropdown'),
                    dcc.Dropdown(
                        id='brain-cell-type-select-dropdown',
                        options=[],
                        value=['ALL'],
                        placeholder='ALL Cell Types by default',
                        clearable=True,
                        multi=True
                    ),
                    dbc.FormText('Only color cells from these Cell Types.')
                ],
                id='brain-cell-type-select-dropdown_row',
                style={'display': 'none'}
            ),
            dbc.Row(
                [
                    dbc.Label('Select by Co Clusters', html_for='brain-co-cluster-select-dropdown'),
                    dcc.Dropdown(
                        id='brain-co-cluster-select-dropdown',
                        options=[],
                        value=['ALL'],
                        placeholder='ALL Co Clusters by default',
                        clearable=True,
                        multi=True
                    ),
                    dbc.FormText('Only color cells from these Co Clusters.')
                ],
                id='brain-co-cluster-select-dropdown_row',
                style={'display': 'block'}
            ),
            dbc.Row(
                [
                    dbc.Label('Targets', html_for='brain-targets-select-dropdown'),
                    dcc.Dropdown(
                        id='brain-targets-select-dropdown',
                        value=['ALL'],
                        multi=True
                    ),
                    dbc.FormText('target of the scatter plot.')
                ],
                id='brain-targets-select-dropdown_row',
                style={'display': 'none'}
            ),
        ]
    )

    tab1_div = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader('Active Cells Rough'),
                                dbc.CardBody(active_cells_form_1),
                            ],
                            className='h-100'
                        ),
                        className='mx-3'
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader('Active Cells Fine'),
                                dbc.CardBody(active_cells_form_2),
                            ],
                            className='h-100'
                        ),
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader('Plot Setting'),
                                dbc.CardBody(click_form),
                            ],
                            className='h-100'
                        ),
                        className='mx-3'
                    ),
                ],
                className='align-items-stretch'  # Align columns vertically
            )
        ]
    )

    # Tab2
    plot_table = dbc.Table(
        [
            html.Thead(html.Tr([html.Th('PlotType'), html.Th('Modality'), html.Th('Region'),
                                html.Th('SubRegion'), html.Th('CellTypes'), html.Th('CoCluster'),
                                html.Th('Gene'), html.Th('Target'), html.Th('Down-Sample'),
                                html.Th('Coordinate'), html.Th('Z-score')])),
            html.Tbody(id='table-body')
        ],
        id='plot_table',
        striped=True,
        bordered=False,
        hover=True,
        responsive=True,
    )

    tab2_div = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(width=8),  # Empty column to push the buttons to the right
                    dbc.Col(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Button(
                                            "Clear",
                                            id="clear-table-and-fig",
                                            n_clicks=0,
                                            color="danger",
                                        ),
                                        width="auto",
                                        className="my-1 mx-2 mb-2"
                                    ),
                                    dbc.Col(
                                        dbc.Button(
                                            "Click To Plot",
                                            id="click-to-plot",
                                            n_clicks=0,
                                            className="my-1 mx-2 mb-2",
                                            color="success"
                                        ),
                                        width="auto",
                                        className="mx-2"
                                    ),
                                ],
                                className="ml-auto",  # This will align the buttons to the right
                            ),
                        ],
                        width=4,
                    ),
                ]
            ),
            dbc.Row(
                [
                    plot_table
                ],
                className='px-5'
            )
        ]
    )

    tabs = dbc.Tabs(
        [
            dbc.Tab(tab1_div, label="Tab 1", tab_id="tab-1"),
            dbc.Tab(tab2_div, label="Tab 2", tab_id="tab-2"),
        ],
        id="tabs",
        active_tab="tab-1",
    )

    output_graphs = html.Div(id='output-graphs', children=[],
                             style={'display': 'flex', 'flex-wrap': 'wrap'})
    tsne_hidden_mark = html.Div(id='tsne')
    layout = html.Div(children=[
        tsne_hidden_mark,
        tabs,
        output_graphs
    ])
    return layout


def get_fig_by_config(active_data, background_data, plot_type, gene_name, gene_data_meta_dict,
                      zscore_cnorm, gene_zscore, index):

    if gene_data_meta_dict:
        gene_cnorm = [gene_data_meta_dict['min'], gene_data_meta_dict['max']]
        min = gene_data_meta_dict['min']
        max = gene_data_meta_dict['max']

    hover_name = 'Annot'
    if len(active_data['Annot']) > 0 and active_data['Annot'][0] != active_data['Annot'][0]:
        hover_name = None

    show_legend = False  # If we need show_legend, switch in 'if' block
    if plot_type == PlotType.CLUSTER.value:
        if not hover_name:
            hover_name = 'SubType'
        fig = px.scatter(active_data,
                         x="x",
                         y="y",
                         color='SubType',
                         hover_name=hover_name,
                         hover_data=[hover_name, 'cocluster'])
    elif plot_type == PlotType.DISSECTION_REGION.value:
        if not hover_name:
            hover_name = PlotType.DISSECTION_REGION.value
        fig = px.scatter(active_data,
                         x="x",
                         y="y",
                         color='DissectionRegion',
                         hover_name=hover_name,
                         hover_data=[hover_name, 'cocluster'])
    elif plot_type == PlotType.CO_CLUSTER.value:
        if not hover_name:
            hover_name = 'cocluster'
        active_data['cocluster'] = active_data['cocluster'].astype(str)
        fig = px.scatter(data_frame=active_data,
                         x='x',
                         y='y',
                         color=active_data['cocluster'],
                         color_discrete_map=color_mapping_dict,
                         hover_name=hover_name,
                         hover_data=[hover_name, 'cocluster'])
    elif plot_type == PlotType.TARGET.value:
        fig = px.scatter(data_frame=active_data,
                         x='x',
                         y='y',
                         color='Target',
                         hover_name=hover_name,
                         hover_data=[hover_name, 'cocluster'])
        show_legend = True
    elif plot_type == PlotType.GENE_EXP.value:
        fig = px.scatter(data_frame=active_data,
                         x='x',
                         y='y',
                         color=gene_name,
                         range_color=gene_cnorm if not gene_zscore else zscore_cnorm,
                         color_continuous_scale='Bluered',
                         hover_name=hover_name,
                         hover_data=[hover_name, 'cocluster'])
    elif plot_type == PlotType.MC_EXP.value:
        fig = px.scatter(data_frame=active_data,
                         x='x',
                         y='y',
                         color=gene_name,
                         range_color=gene_cnorm if not gene_zscore else zscore_cnorm,
                         color_continuous_scale='Bluered',
                         hover_name=hover_name,
                         hover_data=[hover_name, 'cocluster'])
    fig.update_traces(mode='markers', marker_size=n_cell_to_marker_size(active_data.shape[0]))
    fig.update_layout(showlegend=show_legend,
                      margin=dict(t=15, l=0, r=0, b=15),
                      xaxis=go.layout.XAxis(title='',
                                            showticklabels=False,
                                            showgrid=False,
                                            zeroline=False),
                      yaxis=go.layout.YAxis(title='',
                                            showticklabels=False,
                                            showgrid=False,
                                            zeroline=False),
                      plot_bgcolor='rgba(0,0,0,0)',
                      paper_bgcolor='rgba(0,0,0,0)')

    if background_data.shape[0] > 10:
        fig.add_trace(
            go.Scattergl(
                x=background_data['x'],
                y=background_data['y'],
                mode='markers',
                name='Others',
                marker_size=n_cell_to_marker_size(background_data.shape[0]) - 1,
                marker_color='rgba(200, 200, 200, .5)',
                hoverinfo='skip')
        )
    fig.data = fig.data[::-1]

    range_slider_div = html.Div(children=[])
    if plot_type == PlotType.GENE_EXP.value and not gene_zscore:
        range_slider = dcc.RangeSlider(
                        id={
                            'type': 'dynamic-range-slider',
                            'index': index
                        },
                        step=0.1,
                        min=min,
                        max=max,
                        marks=None,
                        value=gene_cnorm,
                        tooltip={"placement": "bottom", "always_visible": True}
        )
        form = dbc.FormText('Color scale of the RNA Gene scatter plot.')
        range_slider_div.children.extend([range_slider, form])
    if plot_type == PlotType.MC_EXP.value and not gene_zscore:
        range_slider = dcc.RangeSlider(
                        id={
                            'type': 'dynamic-range-slider',
                            'index': index
                        },
                        step=0.1,
                        min=min,
                        max=max,
                        marks=None,
                        value=gene_cnorm,
                        tooltip={"placement": "bottom", "always_visible": True}
        )
        form = dbc.FormText('Color scale of the mCH Gene scatter plot.')
        range_slider_div.children.extend([range_slider, form])
    if plot_type in [PlotType.GENE_EXP.value, PlotType.MC_EXP.value] and gene_zscore:
        range_slider = dcc.RangeSlider(
                        id={
                            'type': 'dynamic-range-slider',
                            'index': index
                        },
                        min=-3,
                        max=3,
                        step=1,
                        marks={-1: '-1', -2: '-2', -3: '-3', 0: '0', 1: '1', 2: '2', 3: '3'},
                        value=zscore_cnorm,
                        tooltip={"placement": "bottom", "always_visible": True}
        )
        form = dbc.FormText('The color scale used in the Z-score plot.')
        range_slider_div.children.extend([range_slider, form])

    fig_wrapper = html.Div(
        [
            dcc.Graph(figure=fig,
                      style={"height": "80vh", "width": "auto"},
                      id={
                          'type': 'dynamic-graph',
                          'index': index
                      }),
            range_slider_div,
        ]
    )
    return fig_wrapper


@app.callback(
    Output({'type': 'dynamic-graph', 'index': MATCH}, 'figure'),
    Input({'type': 'dynamic-range-slider', 'index': MATCH}, 'value'),
    State({'type': 'dynamic-graph', 'index': MATCH}, 'figure'),
    prevent_initial_call=True
)
def update_graph(range_slider_value, fig):
    new_fig = go.Figure(fig)
    new_fig.update_layout(coloraxis=dict(cmax=range_slider_value[1], cmin=range_slider_value[0]))
    return new_fig


@app.callback(
    Output('zscore-color-scale-checkbox', 'value'),
    Input('zscore-color-scale-checkbox', 'value')
)
def show_color_slider(check_box_value):
    return ['True'] if 'True' in check_box_value else ['False']


@app.callback(
    Output('brain-co-cluster-select-dropdown', 'value'),
    Output('brain-cell-type-select-dropdown', 'value'),
    Input('brain-active-control-select-checkbox', 'value'),
    prevent_initial_call=True
)
def clear_hidden_value(control_value):
    co_cluster = ['ALL'] if ActivateType.CO_CLUSTER not in control_value else []
    cell_type_value = ['ALL'] if ActivateType.CELL_TYPES not in control_value else []
    return co_cluster, cell_type_value


@app.callback(
    Output('brain-subregion-select-dropdown', 'options'),
    Input('brain-region-select-dropdown', 'value'),
    Input('brain-modality-type-select-dropdown', 'value'),
    prevent_initial_call=True
)
def update_subregion_dropdown(region, modality):
    subregion_options = [{'label': 'ALL', 'value': 'ALL'}]
    if modality != 'RNA':
        subregion_options += \
            [{'label': dataset_config.region_mapping['region_name_to_acc'][subregion], 'value': subregion}
                for subregion in dataset_config.region_mapping.get('region_to_subregion', {}).get(region, [])]
    return subregion_options


@app.callback(
    Output('brain-co-cluster-select-dropdown', 'options'),
    Output('brain-cell-type-select-dropdown', 'options'),
    Output('brain-targets-select-dropdown', 'options'),
    Input('brain-region-select-dropdown', 'value'),
    Input('brain-subregion-select-dropdown', 'value'),
    Input('brain-modality-type-select-dropdown', 'value'),
    prevent_initial_call=True
)
def update_hidden_control_dropdown(region, subregions, modality):
    if None in (region, subregions, modality):
        return [], [], []
    cell_types, targets, co_clusters = get_hidden_options(region, tuple(subregions), modality)
    cell_type_options = [{'label': cell_type, 'value': cell_type} for cell_type in ['ALL'] + cell_types]
    targets_options = [{'label': target, 'value': target} for target in ['ALL'] + targets]
    co_cluster_options = [{'label': co_cluster, 'value': co_cluster} for co_cluster in ['ALL'] + co_clusters]
    return co_cluster_options, cell_type_options, targets_options


@app.callback(
    Output('brain-gene-input', 'options'),
    State('brain-gene-input', 'search_value'),
    Input('brain-modality-type-select-dropdown', 'value'),
    prevent_initial_call=True
)
def update_gene_options(search_value, modality):
    gene_options = [{'label': gene_name, 'value': gene_name} for gene_name in get_gene_name(modality)]
    return [o for o in gene_options if search_value in o["label"]]


@app.callback(
    [Output('brain-plot-type-select-dropdown', 'options'),
     Output('brain-plot-type-select-dropdown', 'value')],
    Input('brain-modality-type-select-dropdown', 'value')
)
def update_plot_type_options(modality_value):
    if not modality_value:
        return [], []
    options = [{'label': plot_type.value, 'value': plot_type.value}
               for plot_type in plot_config.plot_type_dict[modality_value]]
    return options, []


@app.callback(
    Output('brain-gene-input', 'disabled'),
    Output('brain-gene-input', 'placeholder'),
    Input('brain-plot-type-select-dropdown', 'value')
)
def update_second_dropdown_state(selected_values):
    disable = not selected_values or not any(value in [PlotType.GENE_EXP.value, PlotType.MC_EXP.value] for
                                             value in selected_values)
    placeholder = "Disable" if disable else "Input a gene name, e.g. Gad1"
    return disable, placeholder


@app.callback(
    Output('brain-co-cluster-select-dropdown_row', 'style'),
    Output('brain-cell-type-select-dropdown_row', 'style'),
    Output('brain-targets-select-dropdown_row', 'style'),
    Input('brain-active-control-select-checkbox', 'value'),
    Input('brain-plot-type-select-dropdown', 'value'),
    prevent_initial_call=True
)
def update_hidden_control(active_values, plot_values):
    co_cluster_style = {'display': 'block'} if ActivateType.CO_CLUSTER.value in active_values else {'display': 'none'}
    cell_type_style = {'display': 'block'} if ActivateType.CELL_TYPES.value in active_values else {'display': 'none'}
    target_style = {'display': 'block'} if PlotType.TARGET.value in plot_values else {'display': 'none'}
    return co_cluster_style, cell_type_style, target_style


@app.callback(
    Output('tabs', 'active_tab'),
    Output('table-body', 'children'),
    Output('clear-table-and-fig', 'n_clicks'),
    Output('output-graphs', 'children'),
    Output('click-to-plot', 'n_clicks'),
    Input('add-plot-button', 'n_clicks'),
    Input('clear-table-and-fig', 'n_clicks'),
    Input('click-to-plot', 'n_clicks'),
    State('brain-modality-type-select-dropdown', 'value'),
    State('brain-region-select-dropdown', 'value'),
    State('brain-subregion-select-dropdown', 'value'),
    State('brain-cell-type-select-dropdown', 'value'),
    State('brain-plot-type-select-dropdown', 'value'),
    State('brain-gene-input', 'value'),
    State('table-body', 'children'),
    State('down-sample-dropdown', 'value'),
    State('coords-dropdown', 'value'),
    State('brain-targets-select-dropdown', 'value'),
    State('brain-co-cluster-select-dropdown', 'value'),
    State('zscore-color-scale-checkbox', 'value'),
    State('output-graphs', 'children'),
    prevent_initial_call=True
)
def generate_table_and_display_graphs(add_n_clicks, clear_n_clicks, plot_n_clicks, modality, region,
                                      subregion_list, cell_type_list, plot_type_list, gene_name_list,
                                      pre_table_body, down_sample, coords, target_list,
                                      co_cluster_list, zscore, graphs_content):

    if clear_n_clicks:
        merge_plot_details_unique_list.clear()
        fig_name_set.clear()
        return "tab-2", "", 0, [], dash.no_update

    if not add_n_clicks:
        return "tab-1", "", dash.no_update, dash.no_update, dash.no_update

    fig_list = []
    if plot_n_clicks:
        for plot_details in merge_plot_details_unique_list:
            gene_part = "" if plot_details['gene_name'] is None else plot_details['gene_name']
            fig_name = (
                f"{plot_details['plot']}_{plot_details['modality']}_{plot_details['region']}_"
                f"{plot_details['subregion']}_{plot_details['cell_type']}_{plot_details['co_cluster']}_"
                f"{gene_part}_{plot_details['target']}_{plot_details['down_sample']}_{plot_details['coords']}_"
                f"{plot_details['zscore']}"
            )
            fig_dict = {}
            if fig_name not in fig_name_set:
                fig_dict['name'] = fig_name
                gene_zscore = plot_details['zscore'] == 'True'
                result = \
                    get_active_and_background_data(region=plot_details['region'],
                                                   subregions=plot_details['subregion'].split(','),
                                                   gene_name=plot_details['gene_name'],
                                                   cell_types=plot_details['cell_type'].split(','),
                                                   modality=plot_details['modality'],
                                                   targets=plot_details['target'].split(','),
                                                   co_clusters=plot_details['co_cluster'].split(','),
                                                   gene_zscore=gene_zscore,
                                                   )
                active_data = result['active_data']
                background_data = result['background_data']
                gene_data_meta_dict = result['gene_data_meta_dict']
                down_sample = plot_config.down_sample_dict[plot_details['down_sample']]
                if down_sample:
                    if active_data.shape[0] > down_sample:
                        active_data = active_data.sample(down_sample, random_state=0)
                    if background_data.shape[0] > down_sample:
                        background_data = background_data.sample(down_sample, random_state=0)

                    fig_wrapper = get_fig_by_config(active_data, background_data, plot_details['plot'],
                                                    gene_name=plot_details['gene_name'],
                                                    gene_data_meta_dict=gene_data_meta_dict,
                                                    zscore_cnorm=plot_config.zscore_cnorm,
                                                    gene_zscore=gene_zscore,
                                                    index=merge_plot_details_unique_list.index(plot_details))
                fig_name_set.add(fig_name)
                fig_dict['fig'] = fig_wrapper
                fig_list.append(fig_dict)

        cur_graph_contents = add_fig_wrapper_to_content(fig_list, graphs_content)

        return "tab-2", dash.no_update, dash.no_update, cur_graph_contents, 0

    plot_details_list = get_scatter_config_list_tsne(modality, region, subregion_list, cell_type_list,
                                                     plot_type_list, gene_name_list, down_sample, coords,
                                                     target_list, co_cluster_list, zscore[0])
    if not plot_details_list:
        return "tab-1", "", dash.no_update, dash.no_update, dash.no_update

    pre_plot_details_list = get_scatter_table_content_tsne(pre_table_body, plot_config.td_key_list)

    rows = []
    merge_plot_details_list = pre_plot_details_list + plot_details_list
    seen_values = set()
    merge_plot_details_unique_list.clear()
    for d in merge_plot_details_list:
        frz_dict = frozenset(d.items())
        if frz_dict not in seen_values:
            seen_values.add(frz_dict)
            merge_plot_details_unique_list.append(d)

    for plot_detail in merge_plot_details_unique_list:
        new_row = html.Tr([html.Td(str(plot_detail.get(key, ''))) for key in plot_config.td_key_list])
        rows.append(new_row)

    return "tab-2", rows, dash.no_update, dash.no_update, dash.no_update
