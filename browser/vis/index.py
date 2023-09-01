import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State
from apps.browser_tsne import create_tsne_plot_layout
from apps.browser_spatial import create_spatial_plot_layout
from vis.app import app, ROOT_PATH
from utils.plot_utils import extract_ids


def get_header():
    nav = dbc.Nav(
        [
            dbc.NavItem(dbc.NavLink("Tsne Plot", active=True, href=f"/{ROOT_PATH}/tsne",
                                    id='tsne-plot'),
                        ),
            dbc.NavItem(dbc.NavLink("Spatial Plot", href=f"/{ROOT_PATH}/spatial",
                                    id='spatial-plot'),
                        ),
        ],
        pills=True,
        className="custom-nav nav-hover ",
        style={
            "box-shadow": "0px 2px 4px rgba(0, 0, 0, 0.1)",
            "transition": "box-shadow 0.3s",
            "background-color": "#f8f9fa",
            "border-radius": "5px",
            "padding": "10px",
        },
    )
    return nav


app.layout = html.Div(
    [
        dcc.Location(id='url', refresh=False),
        get_header(),
        dcc.Store(id='tsne-layout'),
        dcc.Store(id='spatial-layout'),
        html.Div(
            id='page-content',
            className='page-content'
        )
    ]
)
tsne_layout = create_tsne_plot_layout()
spatial_layout = create_spatial_plot_layout()
app.config.suppress_callback_exceptions = True


@app.callback(
    Output('tsne-layout', 'data'),
    Output('spatial-layout', 'data'),
    Output('page-content', 'children'),
    Output('tsne-plot', 'active'),
    Output('spatial-plot', 'active'),
    Input('url', 'pathname'),
    State('tsne-layout', 'data'),
    State('spatial-layout', 'data'),
    State('page-content', 'children'),
    prevent_initial_call=True
)
def get_page_content(pathname, tsne_layout_data, spatial_layout_data, page_content):
    page_ids = extract_ids(page_content)
    if pathname == f'/{ROOT_PATH}/tsne':
        spatial_layout_data = page_content if 'spatial' in page_ids else dash.no_update
        if tsne_layout_data:
            return dash.no_update, spatial_layout_data, tsne_layout_data, True, False
        else:
            return dash.no_update, spatial_layout_data, tsne_layout, True, False
    elif pathname == f'/{ROOT_PATH}/spatial':
        tsne_layout_data = page_content if 'tsne' in page_ids else dash.no_update
        if spatial_layout_data:
            return tsne_layout_data, dash.no_update, spatial_layout_data, False, True
        else:
            return tsne_layout_data, dash.no_update, spatial_layout, False, True

    return dash.no_update, dash.no_update, tsne_layout, True, False


if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
