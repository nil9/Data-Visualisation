import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objs as pgo

# Use bootstrap css for the layout of the dashboard.
external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css']

# Initialize the dashboard
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Read data and scale it based on the maximum of the data.
df_weekly = pd.read_csv("processed_data__weekly.csv", index_col=0)
df_daily = pd.read_csv("processed_data__daily.csv", index_col=0)
df_daily.new_rescale = df_daily.new_rescale.apply(lambda x: np.maximum(0, x))
customdata = df_daily

# Initialize heatmap and format it.
fig = pgo.Figure(data=pgo.Heatmap(
    z=df_daily.new_rescale,
    x=df_daily.Date,
    y=df_daily.Country,
    customdata=df_daily,
    hovertemplate="""Date: %{x}
<br>Country: %{y} 
<br>New Cases: %{customdata[6]} 
<br>Active Cases: %{customdata[5]}
<br>Population: %{customdata[4]}
<b><br>New Cases per Million: %{customdata[7]:.3f}
<br>Active Cases per Million: %{customdata[9]:.3f}</b><extra></extra>""",
    colorbar=dict(
        title="New Cases (per Country)",
        titleside="right",
        tickmode="array",
        tickvals=[0, 0.25, 0.5, 0.75, 1],
        ticktext=["None", "Low", "Average", "High", "Very High"],
        ticks="outside")))

# Create Layout of the dashboard including interaction components and graphs.
app.layout = html.Div([

    html.H1("Dashboard to support travelers during the COVID19-Pandemic", style={'text-align': 'center'}),
    html.Br(),
    html.Div(
        [
            # Implement two dropdowns at the top of the dashboard.
            # First dropdown asks users about their homecountry.
            html.Div(
                [
                    html.H6("""Select your homecountry for comparison""",
                            style={'margin-right': '2em'})
                ],
            ),

            dcc.Dropdown(id="slct_homecountry",
                         options=[
                             {"label": "United Kingdom", "value": 'United Kingdom'},
                             {"label": "Turkey", "value": 'Turkey'},
                             {"label": "Spain", "value": 'Spain'},
                             {"label": "Poland", "value": 'Poland'},
                             {"label": "Netherlands", "value": 'Netherlands'},
                             {"label": "Italy", "value": 'Italy'},
                             {"label": "Greece", "value": 'Greece'},
                             {"label": "Germany", "value": 'Germany'},
                             {"label": "Denmark", "value": 'Denmark'},
                             {"label": "Croatia", "value": 'Croatia'},
                             {"label": "Belgium", "value": 'Belgium'},
                             {"label": "Austria", "value": 'Austria'}],
                         multi=False,
                         value='Germany',
                         style={'width': "40%", 'verticalAlign': "middle"}
                         )
        ]
    ),
    html.Br(),
    # Second Dropdown asks users about which months they are interested in.
    html.Div(
        [
            html.Div(
                [
                    html.H6("""Select the first month for which data should be displayed in the line graphs""",
                            style={'margin-right': '2em'})
                ],
            ),

            dcc.Dropdown(id="slct_month",
                         options=[
                             {"label": "January", "value": 1},
                             {"label": "February", "value": 2},
                             {"label": "March", "value": 3},
                             {"label": "April", "value": 4},
                             {"label": "May", "value": 5},
                             {"label": "June", "value": 6}
                         ],
                         multi=False,
                         value=1,
                         style={'width': "40%", 'verticalAlign': "middle"}
                         )
        ]
    ),
    # Display heatmap in the center of the dashboard.
    dcc.Graph(id='heatmap', figure=fig),
    # Cpntainer for the additional line graphs.
    html.Div([
        html.Div([
            dcc.Graph(id='linegraph1', figure={}, config={'displayModeBar': False})
        ], className="col-sm-4"),

        html.Div([
            dcc.Graph(id='linegraph2', figure={}, config={'displayModeBar': False})
        ], className="col-sm-4"),
        html.Div([
            dcc.Graph(id='linegraph3', figure={}, config={'displayModeBar': False
                                                          })
        ], className="col-sm-4")
    ], className="row")
])


# Implement callback to make the dashboard interactive, when the user hovers over the heatmap.
@app.callback([Output('linegraph1', 'figure'), Output('linegraph2', 'figure'), Output('linegraph3', 'figure')],
              [Input('heatmap', 'hoverData'), Input('slct_homecountry', 'value'), Input('slct_month', 'value')])
# Define behavior if an input value changes or the user hovers over a heatmap element.
def disp_hover_data(hover_data, homecountry, month):
    if hover_data is not None:
        # Retrieve selected homecountry.
        country = str(hover_data['points'][0]['y'])

        # Filter dataframe based on the user input.
        df1 = df_daily[['Country', 'Date', 'total_cases', 'active_cases', 'active_per_mil']]
        df1.Date = pd.to_datetime(df1.Date)
        data = df1.loc[
            ((df1["Country"] == country) | (df1['Country'] == homecountry)) & (df1['Date'].dt.month >= month)]
        data.columns = ['Country Name', 'Date', 'Total Cases', 'Active Cases', 'Active Cases per Million']

        # Update linegraphs with new filtered data.
        fig1 = px.line(data, x='Date', y='Total Cases', color='Country Name')
        fig1.update_layout(title='Total Number of Covid-19 Cases in ' + country,
                           xaxis_title='Dates',
                           yaxis_title='Total Cases')
        fig2 = px.line(data, x='Date', y='Active Cases', color='Country Name')
        fig2.update_layout(title='Active Number of Covid-19 Cases in ' + country,
                           xaxis_title='Dates',
                           yaxis_title='Active Cases')
        fig3 = px.line(data, x='Date', y='Active Cases per Million', color='Country Name')
        fig3.update_layout(title='Active Number of Covid19 Cases in ' + country + ' per Million inhabitants',
                           xaxis_title='Dates',
                           yaxis_title='Average number of Cases per Million inhabitants')

        # Handle the cases of Netherlands or UK as full data is not available for them.
        if country == 'Netherlands' or country == 'United Kingdom':
            fig2.update_layout(title='No data provided on active cases for ' + country,
                               xaxis_title='Dates',
                               yaxis_title='Active Cases')
            fig3.update_layout(title='No data provided on active cases for ' + country,
                               xaxis_title='Dates',
                               yaxis_title='Active Cases')
    else:
        # Provide empty linegraphs in case no user selection is made.
        fig1 = pgo.Figure([pgo.Scatter(x=[], y=[])])
        fig1.update_layout(title='Select a country to show total Number of Covid-19 Cases',
                           xaxis_title='Dates',
                           yaxis_title='Total Cases')
        fig2 = pgo.Figure([pgo.Scatter(x=[], y=[])])
        fig2.update_layout(title='Select a country to show active Number of Covid-19 Cases',
                           xaxis_title='Dates',
                           yaxis_title='Active Cases')
        fig3 = pgo.Figure([pgo.Scatter(x=[], y=[])])

        fig3.update_layout(title='Select a country to show average Number of Covid-19 Cases',
                           xaxis_title='Dates',
                           yaxis_title='Average number of Cases per Million inhabitants')
        # Return updated figures to the dashboard.
    return fig1, fig2, fig3


# Run the dash app.
if __name__ == '__main__':
    app.run_server(debug=True)
