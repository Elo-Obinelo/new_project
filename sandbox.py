from dash import Dash, html, dcc, Input, Output, State, clientside_callback
import dash_bootstrap_components as dbc
from datetime import date, timedelta
import sqlite3

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME], prevent_initial_callbacks= False)
# conn = sqlite3.Connection("new_project/stash1.db")
# cursor = conn.cursor()


market_picker = html.Div([
    dcc.RadioItems(
        id='button-group',
        options=[
            {'label': 'BE', 'value': 'BE'},
            {'label': 'DE', 'value': 'DE'},
            {'label': 'FR', 'value': 'FR'},
            {'label': 'NL', 'value': 'NL'}
        ],
        value='BE',
        labelStyle={'display': 'inline-block', 'margin-right': '10px'}
    ),
    html.Div(id='output')
])

slider = html.Div([
    html.Div("Interval(min)"),
    dcc.Slider(1, 3, 1,
               value=1,
               id='my-slider',
               marks= {
                   "1": "60",
                   "2": "30",
                   "3": "15"
               }
    )
])

datepicker = html.Div([
    dcc.DatePickerSingle(
        id='my-date-picker-range',
        min_date_allowed=date(2024, 9, 24),
        max_date_allowed=date.today(),
        initial_visible_month=date(2024, 9, 26),
        date = date.today() - timedelta(days=2)
    ),

])

offcanvas = html.Div(
    [
        dbc.NavbarToggler(id="open-offcanvas", n_clicks=0),
        dbc.Offcanvas(
            [
            html.Div(style={'height': '100px'}),
            slider,
            html.Div(style={'height': '100px'}),
            datepicker,
            html.Div(style={'height': '100px'}),
            market_picker
            ],
            id="offcanvas",
            title="Menu",
            is_open=False,
        ),
    ]
)

color_mode_switch =  html.Span(
    [
        dbc.Label(className="fa fa-moon", html_for="switch"),
        dbc.Switch( id="switch", value=True, className="d-inline-block ms-1", persistence=True),
        dbc.Label(className="fa fa-sun", html_for="switch"),
    ]
)

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col([offcanvas], width= 1),
                dbc.Col(width= 10),
                dbc.Col([color_mode_switch], width= 1)
            ]
        ),
        html.Div(id= "my-table")
    ],
    className="p-4",
    id="page-content",
)

clientside_callback(
    """
    (switchOn) => {
       document.documentElement.setAttribute("data-bs-theme", switchOn ? "light" : "dark"); 
       return window.dash_clientside.no_update
    }
    """,
    Output("switch", "id"),
    Input("switch", "value"),
)

@app.callback(
    Output("offcanvas", "is_open"),
    Input("open-offcanvas", "n_clicks"),
    [State("offcanvas", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open

@app.callback(
    Output('my-table', 'children'),
    Input('my-date-picker-range', 'date'),
    Input('button-group', 'value'),
    Input('my-slider', 'value'))
def update_output(date_now, market_area, resolution):
    if date_now is not None:
        date_object = date.fromisoformat(date_now)
        date_string = date_object.strftime('%Y-%m-%d')
        if resolution == 1:
            res = 'res1'
        elif resolution == 2:
            res = 'res2'
        else:
            res = 'res3'

        conn = sqlite3.connect("new_project/stash1.db")
        cursor = conn.cursor()
        cursor.execute(f'''
            SELECT * FROM {market_area} WHERE  Date == '{date_string}' AND Resolution = '{res}'
        ''')
        headers = [i[0] for i in cursor.description]
        corpus = cursor.fetchall()
        # df = pd.DataFrame.from_records(cursor.fetchall(), columns=headers).iloc[:,1:-1]
        # table = dbc.Table(id= 'my_table').from_dataframe(df, striped=True, bordered=True, hover=True)
        table_header = [
            html.Thead(html.Tr([html.Th(header) for header in headers]))
        ]
        table_body = [
            html.Tbody([html.Tr([html.Td(value) for value in row]) for row in corpus])
            ]
        table = dbc.Table(table_header + table_body, bordered=True, striped=True, hover=True)
        cursor.close()
        conn.close()
        return table


if __name__ == "__main__":
    app.run_server()