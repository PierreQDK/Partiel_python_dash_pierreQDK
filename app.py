import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import dash_table
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ========== Chargement des données ==========
df = pd.read_csv("supermarket_sales.csv")
df['Date'] = pd.to_datetime(df['Date'])

# ========== Interface Dash ========== #
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

city_options = [{'label': c, 'value': c} for c in df['City'].unique()]
gender_options = [{'label': 'Tous les genres', 'value': 'all'}] + [{'label': g, 'value': g} for g in df['Gender'].unique()]

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H3("Dashboard Supermarché", className="text-left"), md=6, style={
            "height": "7vh", "display": "flex", "alignItems": "center",
            "justifyContent": "flex-start", "backgroundColor": "#556B2F", "color": "white", "paddingLeft": "15px"
        }),
        dbc.Col([
            dcc.Dropdown(
                id="city-select",
                options=city_options,
                value=[c['value'] for c in city_options],
                multi=True,
                placeholder="Ville"
            )
        ], md=3, style={"padding": "10px", "backgroundColor": "#556B2F"}),
        dbc.Col([
            dcc.Dropdown(id="gender-select", options=gender_options, value='all', placeholder="Sexe")
        ], md=3, style={"padding": "10px", "backgroundColor": "#556B2F"})
    ], style={"backgroundColor": "#556B2F"}),

    html.Br(),

    dbc.Row([
        dbc.Col([
            html.Div([
                dcc.Graph(id='total-amount-indicator')
            ], style={
                "backgroundColor": "#556B2F",
                "padding": "10px",
                "margin": "10px",
                "borderRadius": "8px",
                "color": "white",
                "boxShadow": "0 4px 8px rgba(0,0,0,0.2)",
                "height": "100%"
            })
        ], md=6),

        dbc.Col([
            html.Div([
                dcc.Graph(id='average-rating-indicator')
            ], style={
                "backgroundColor": "#556B2F",
                "padding": "10px",
                "margin": "10px",
                "borderRadius": "8px",
                "color": "white",
                "boxShadow": "0 4px 8px rgba(0,0,0,0.2)",
                "height": "100%"
            })
        ], md=6)
    ], style={"marginBottom": "10px"}),

    dbc.Row([
        dbc.Col([
            html.Div([
                html.H4("Répartition des montants totaux d’achats", style={"textAlign": "center", "color": "white"}),
                dcc.Graph(id='histogram-total')
            ], style={
                 "backgroundColor": "#556B2F",
                "padding": "10px",
                "margin": "10px",
                "borderRadius": "8px",
                "color": "white",
                "boxShadow": "0 4px 8px rgba(0,0,0,0.2)",
                "height": "100%"
            })
        ], md=6),

        dbc.Col([
            html.Div([
                html.H4("Nombre total d’achats par sexe et ville", style={"textAlign": "center", "color": "white"}),
                dcc.Graph(id='bar-invoices')
            ], style={
                "backgroundColor": "#556B2F",
                "padding": "10px",
                "margin": "10px",
                "borderRadius": "8px",
                "color": "white",
                "boxShadow": "0 4px 8px rgba(0,0,0,0.2)",
                "height": "100%"
            })
        ], md=6)
    ],style={"marginTop": "20px", "marginBottom": "20px"}),

    dbc.Row([
    dbc.Col([
        html.Div([
            html.H4("Répartition des catégories de produits", style={"textAlign": "center", "color": "white"}),
            dcc.Graph(id='pie-product-line')
        ], style={
            "backgroundColor": "#556B2F",
            "padding": "20px",
            "borderRadius": "12px",
            "boxShadow": "0 4px 10px rgba(0,0,0,0.3)"
        })
    ], md=6, width={"size": 6, "offset": 3})  # ✅ Centre et réduit la largeur
]),
], fluid=True, style={"backgroundColor": "#FFFFE0", "marginTop": "20px"})

@callback(
    Output('total-amount-indicator', 'figure'),
    Output('average-rating-indicator', 'figure'),
    Output('histogram-total', 'figure'),
    Output('bar-invoices', 'figure'),
    Output('pie-product-line', 'figure'),
    Input('city-select', 'value'),
    Input('gender-select', 'value')
)
def update_dashboard(cities, gender):
    filtered_df = df[df['City'].isin(cities)] if cities else df.copy()
    if gender != 'all':
        filtered_df = filtered_df[filtered_df['Gender'] == gender]

    # Indicateurs
    total_amount = filtered_df['Total'].sum()
    avg_rating = filtered_df['Rating'].mean()

    fig_total = go.Figure(go.Indicator(
        mode="number",
        value=total_amount,
        number={"valueformat": ",.2f", "suffix": " USD"},
        title={"text": "Montant total des achats ($)"}
    ))
    fig_total.update_layout(
        paper_bgcolor="#556B2F",
        font_color="white",
        height=200,
        margin=dict(t=40, b=10),
        font=dict(size=18)
    )

    fig_rating = go.Figure(go.Indicator(
        mode="number",
        value=avg_rating,
        number={"valueformat": ".2f"},
        title={"text": "Évaluation moyenne (/10)"}
    ))
    fig_rating.update_layout(
        paper_bgcolor="#556B2F",
        font_color="white",
        height=200,
        margin=dict(t=40, b=10),
        font=dict(size=18)
    )

    # Histogramme des montants totaux
    fig_hist = px.histogram(
    filtered_df,
    x='Total', 
    nbins=30,
    color='City',
    pattern_shape='Gender',  # Le genre est différencié par motif (hachure)
    color_discrete_map={
        "Yangon": "#D98E73",      # orange doux
        "Naypyitaw": "#88BDBC",   # bleu canard clair
        "Mandalay": "#A3B18A"     # vert olive clair
    }, 
     labels={"count": "Nombre d'achats", "Total": "Montant total ($)"}
)
    
   


    # Diagramme en barres du nombre d’achats
    invoice_counts = filtered_df.groupby(['Gender', 'City'])['Invoice ID'].count().reset_index()
    fig_bar = px.bar(
    invoice_counts,
    x='City',
    y='Invoice ID',
    color='City',
    pattern_shape='Gender',
    barmode='group',
    color_discrete_sequence=["#A3B18A", "#88BDBC", "#D98E73"], 
    labels={"Invoice ID": "Nombre d’achats", "City": "Ville"}
    )


    pie_data = filtered_df['Product line'].value_counts().reset_index()
    fig_pie = px.pie(pie_data, names='index', values='Product line',color_discrete_sequence=["#A3B18A", "#D98E73", "#A9C5D3", "#C9BBCF", "#E3B778", "#88BDBC"]
                     )

    return fig_total, fig_rating, fig_hist, fig_bar, fig_pie

if __name__ == '__main__':
    app.run_server(debug=True, port=8055, jupyter_mode="external")
