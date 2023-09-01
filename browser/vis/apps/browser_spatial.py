import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State
import plotly.graph_objects as go
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import linkage, dendrogram
from vis.utils.plot_utils import assign_colors_to_co_clusters_selected
from vis.config.plot_config import plot_config
from vis.config.dataset_config import dataset_config
from vis.datacenter.data_center_tsne import get_by_co_cluster
from vis.datacenter.data_center_spatial import load_heat_map_data, get_spatial_scatter_data
from vis.app import app


co_cluster_list = []
color_mapping_dict = {}


def get_heat_map_fig(heat_map_data):
    distances = pdist(heat_map_data.values, metric='cosine')
    linkage_matrix = linkage(distances, method='average')
    row_order = dendrogram(linkage_matrix, no_plot=True)['leaves']
    heat_map_data_reordered = heat_map_data.iloc[row_order]

    colorscale = [[0, 'rgb(59, 76, 192)'],
                  [0.5, 'rgb(255, 255, 255)'],
                  [1, 'rgb(180, 4, 38)']]

    fig = go.Figure(data=go.Heatmap(
        z=heat_map_data_reordered.values,
        x=heat_map_data_reordered.columns,
        y=heat_map_data_reordered.index,
        zmin=-2,
        zmax=2,
        colorscale=colorscale))

    # y_tick_template = "<span style='color: {}; font-size: 20px;'>●</span> {}"
    y_tick_vals = list(range(len(heat_map_data_reordered.index)))
    # y_tick_text = [y_tick_template.format(cluster_color_mapping[int(label.split(":")[0])], label) for label in
    #                heat_map_data_reordered.index.tolist()]

    fig.update_layout(
        width=plot_config.heat_map_size['width'],
        height=plot_config.heat_map_size['height'],
        xaxis_tickangle=-90,
        yaxis_side='right',
        xaxis=dict(
            tickfont=dict(
                size=14
            )
        ),
        yaxis=dict(
            tickfont=dict(
                size=14
            ),
            tickmode='array',
            tickvals=y_tick_vals,
            # ticktext=y_tick_text
        ),
    )

    fig.update_traces(
        colorbar_orientation='v',
        colorbar_x=-0.1,
        colorbar_y=0.5,
        colorbar_tickmode='array',
        colorbar_tickvals=[-2, -1, 0, 1, 2],
        colorbar_ticktext=['-2', '-1', '0', '1', '2'],
        colorbar_tickangle=0,
        selector=dict(type='heatmap')
    )

    bordered_rows = [i for i, item in enumerate(heat_map_data_reordered.index.tolist())
                     if int(item.split(':')[0]) in co_cluster_list]

    rectangles = []

    for row_idx in bordered_rows:
        y_coordinate = row_idx - 0.5
        rectangle = go.layout.Shape(
            type="rect",
            x0=-0.5,
            x1=len(heat_map_data_reordered.columns) - 0.5,
            y0=y_coordinate,
            y1=y_coordinate + 1,
            line=dict(color='black',
                      width=2),
        )
        rectangles.append(rectangle)

    fig.update_layout(
        shapes=rectangles,
    )
    return fig


def get_tsne_scatter_fig(active_data, background_data):
    fig = go.Figure()

    fig.add_trace(
        go.Scattergl(
            x=background_data['x'],
            y=background_data['y'],
            mode='markers',
            marker=dict(size=1, color='rgba(200, 200, 200, .5)'),
            hoverinfo='skip',
            name='Sample Scatter'
        )
    )

    unique_coclusters = set(active_data['cocluster'])
    for cluster in unique_coclusters:
        subset = active_data[active_data['cocluster'] == cluster]
        fig.add_trace(
            go.Scattergl(
                x=subset['x'],
                y=subset['y'],
                mode='markers',
                marker=dict(size=3, color=color_mapping_dict[cluster]),
                hoverinfo='text',
                text=cluster,
                name=f'Cluster {cluster}'
            )
        )

    fig.update_layout(
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(t=15, l=0, r=0, b=15),
        showlegend=True,
    )

    return fig

def get_spatial_scatter_fig(spatial_data):
    fig = go.Figure()

    upper = spatial_data[spatial_data['upper']]  # cluster
    middle = spatial_data[spatial_data['middle']]  # region
    bottom = spatial_data[spatial_data['bottom']]  # others all

    fig.add_trace(
        go.Scattergl(
            x=bottom['x'],
            y=bottom['y'],
            mode='markers',
            marker=dict(size=1, color='rgba(200, 200, 200, .5)'),
            hoverinfo='skip',
            name='Sample Scatter'
        )
    )

    fig.add_trace(
        go.Scattergl(
            x=middle['x'],
            y=middle['y'],
            mode='markers',
            marker=dict(size=8, color='rgba(200, 200, 200, 0.5)'),
            hoverinfo='skip',
            name='Region Scatter'
        )
    )

    unique_coclusters = set(upper['cocluster'])
    for cluster in unique_coclusters:
        subset = upper[upper['cocluster'] == cluster]
        fig.add_trace(
            go.Scattergl(
                x=subset['x'],
                y=subset['y'],
                mode='markers',
                marker=dict(size=3, color=color_mapping_dict[cluster]),
                hoverinfo='text',
                text=cluster,
                name=f'Cluster {cluster}'
            )
        )


    fig.update_layout(
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, scaleanchor="y", scaleratio=1),
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False, scaleanchor="x", scaleratio=1),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(t=15, l=0, r=0, b=15),
    )

    return fig


def get_fig_layout_spatial(tsne_fig_dict, heat_map_fig_dict, spatial_fig_list, per_col_fig):
    if spatial_fig_list:
        spatial_fig_list.insert(0, tsne_fig_dict)

    layout_children = []

    first_fig_row = dbc.Row(
        [
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(heat_map_fig_dict['name']),
                        dbc.Container(
                            [
                                heat_map_fig_dict['fig']
                            ],
                            className='pt-3'
                        )
                    ]
                ),
            ),
        ],
        className='my-4',
    )
    layout_children.append(first_fig_row)

    figs_rows = [spatial_fig_list[i:i + per_col_fig]
                 for i in range(0, len(spatial_fig_list), per_col_fig)]
    for fig_row in figs_rows:
        row_children = []
        for fig_col in fig_row:
            col = dbc.Col(
                [
                    dbc.Card(
                        [
                            dbc.CardHeader(fig_col['name']),
                            dbc.Container(
                                [
                                    fig_col['fig']
                                ],
                                className='pt-3'
                            )
                        ]
                    )
                ],
                width=12, xl=6
            )
            row_children.append(col)
        row = dbc.Row(row_children, className='my-4')
        layout_children.append(row)

    layout = html.Div(children=layout_children)
    return layout


def create_spatial_plot_layout():

    spatial_plot_card = dbc.Card(
        [
            dbc.CardHeader('Spatial Plot Setting'),
            dbc.CardBody(
                dbc.Form(
                    [
                        dbc.Row([
                            dbc.Col(
                                [
                                    dbc.Label("Heatmap Only:", html_for="heat-map-only-checkbox"),
                                    dbc.Checklist(
                                        options=[{"label": "", "value": "only"}],
                                        value=["only"],  # Set the value to ["heatmaponly"]
                                        id="heat-map-only-checkbox",
                                        inline=True,
                                        switch=True,
                                    ),
                                ],
                                width=1,
                            ),
                            dbc.Col([
                                dbc.Label('Select by Brain Region', html_for='brain-region-select-dropdown',
                                          className='mb-2'),
                                dcc.Dropdown(
                                    id='brain-region-select-dropdown',
                                    options=[{'label': dataset_config.region_mapping['region_name_to_acc'][region],
                                              'value': region}
                                             for region in dataset_config.region_mapping["region_to_subregion"].keys()
                                             ],
                                    value=None,
                                    placeholder='Select a Region',
                                    clearable=False,
                                    className='mb-3'
                                ),
                                dbc.FormText('Only color cells from these brain subregions.', className='text-muted')
                            ], className='mb-4'),

                            dbc.Col([
                                dbc.Label('Select by Sample', html_for='brain-sample-select-dropdown',
                                          className='mb-2'),
                                dcc.Dropdown(
                                    id='brain-sample-select-dropdown',
                                    options=[{'label': sample, 'value': sample} for sample in dataset_config.samples],
                                    value=[],
                                    placeholder='Select Samples',
                                    clearable=True,
                                    multi=True,
                                    className='mb-3'
                                ),
                                dbc.FormText('Only color cells from these samples.', className='text-muted')
                            ], className='mb-4'),

                            dbc.Col(
                                [
                                    html.H4('Plot Control', className='card-title text-center mb-3'),
                                    dbc.Button(
                                        'CLICK TO PLOT',
                                        id='click-to-plot-spatial',
                                        n_clicks=0,
                                        color='success',
                                        className='w-100'
                                    )
                                ],
                                className='mb-4',
                                width=2,
                            ),
                        ], className='mx-2')
                    ]
                )
            )
        ],
        className="m-auto",
    )

    output_graphs = html.Div(id='output-graphs-spatial')
    spatial_hidden_mark = html.Div(id='spatial')
    layout = html.Div(children=[
        spatial_hidden_mark,
        spatial_plot_card,
        html.Div(children=[], id='dummy-output'),
        dcc.Store(id='prev-region', data='None'),
        dcc.Loading(
            output_graphs
        )
    ])
    return layout


@app.callback(
    Output("brain-sample-select-dropdown", "disabled"),
    Input("heat-map-only-checkbox", "value")
)
def update_disabled_components(heatmap_only_value):
    disabled = True if "only" in heatmap_only_value else False
    return disabled


@app.callback(
    Output('prev-region', 'data'),
    Input('brain-region-select-dropdown', 'value'),
    State('prev-region', 'data'),  # Use State to access the previous value stored in the Store
    prevent_initial_call=True
)
def clear_co_cluster_list(selected_value, prev_value):
    global co_cluster_list
    if selected_value != prev_value:
        co_cluster_list.clear()
    return selected_value


@app.callback(
    Output('output-graphs-spatial', 'children'),
    Output('click-to-plot-spatial', 'n_clicks'),
    Input('click-to-plot-spatial', 'n_clicks'),
    Input('brain-region-select-dropdown', 'value'),
    State('brain-sample-select-dropdown', 'value'),
    State("heat-map-only-checkbox", "value"),
    State('prev-region', 'data'),  # Use State to access the previous value stored in the Store
    prevent_initial_call=True
)
def display_graphs(plot_n_clicks, region, sample_list, heat_map_only, pre_region):
    if region != pre_region:
        return "", dash.no_update

    if plot_n_clicks:
        # assign color to each selected co-cluster
        global color_mapping_dict
        if set(color_mapping_dict.keys()) != set(co_cluster_list):
            color_mapping_list = assign_colors_to_co_clusters_selected(cluster_count=len(co_cluster_list))
            color_mapping_dict = dict(zip(co_cluster_list, color_mapping_list))

        fig_list = []
        tsne_fig_dict = None

        if 'only' not in heat_map_only:
            active_data, background_data = get_by_co_cluster(region, co_cluster_list)
            tsne_fig = dcc.Graph(figure=get_tsne_scatter_fig(active_data, background_data), id='tsne_fig')
            tsne_fig_dict = {'fig': tsne_fig, 'name': f'TSNE_Region:{region}_Cluster:{co_cluster_list}'}

        if 'only' in heat_map_only and sample_list:
            sample_list = []

        heat_map_data = load_heat_map_data(region)
        heat_map_fig = dcc.Graph(figure=get_heat_map_fig(heat_map_data), id='heatmap')
        heat_map_fig_dict = {'fig': heat_map_fig, 'name': f'Region:{region}'}

        for sample in sample_list:
            fig_dict = {}
            spatial_data = get_spatial_scatter_data(sample, region, co_cluster_list)
            spatial_fig = get_spatial_scatter_fig(spatial_data)
            fig_dict['fig'] = dcc.Graph(figure=spatial_fig)
            fig_dict['name'] = f'Sample:{sample}_Region:{region}_Cluster:{co_cluster_list}'
            fig_list.append(fig_dict)

        layout = get_fig_layout_spatial(tsne_fig_dict, heat_map_fig_dict, fig_list, per_col_fig=2)
        return layout, 0


@app.callback(
    Output('heatmap', 'figure'),
    Input('heatmap', 'clickData'),
    State('heatmap', 'figure'),
    prevent_initial_call=True
)
def display_heat_map_label_value(click_data, fig):
    if not click_data:
        return "", fig

    fig = go.Figure(fig)

    point = click_data['points'][0]
    label_y_value = point['y']
    clicked_row_idx = list(fig.data[0].y).index(label_y_value)

    is_bordered = any(
        shape['y0'] == clicked_row_idx - 0.5 and shape['y1'] == clicked_row_idx + 0.5
        for shape in fig['layout']['shapes']
    )
    row_idx = int(list(fig.data[0].y).index(label_y_value))

    cluster = int(label_y_value.split(':')[0])
    if is_bordered:
        co_cluster_list.remove(cluster)
        updated_shapes = [
            shape for shape in fig['layout']['shapes']
            if not (
                'y0' in shape and 'y1' in shape and
                shape['y0'] == clicked_row_idx - 0.5 and shape['y1'] == clicked_row_idx + 0.5
            )
        ]
    else:
        if cluster not in co_cluster_list:
            co_cluster_list.append(cluster)
        rectangles = []
        y_coordinate = row_idx - 0.5
        rectangle = go.layout.Shape(
            type="rect",
            x0=-0.5,
            x1=len(fig.data[0].x) - 0.5,
            y0=y_coordinate,
            y1=y_coordinate + 1,
            line=dict(color='black',
                      width=2),
        )
        rectangles.append(rectangle)
        updated_shapes = fig['layout']['shapes'] + tuple(rectangles)
    fig['layout']['shapes'] = updated_shapes

    return fig
