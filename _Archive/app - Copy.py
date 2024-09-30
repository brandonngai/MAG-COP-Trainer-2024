import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State, MATCH, ALL
from itertools import compress

import json

import flask
import glob
import os

import base64

import plotly.express as px
import pandas as pd

from random import randrange
#from PIL import Image, ImageTk

# Initialization =================================================================
currentDir = os.getcwd()
imgDir = currentDir + "/Skill Images"
imageList = os.listdir(imgDir)
imageList.remove('welcome.png')


# Create Solution Dataframe ======================================================
event_list = []
value_list = []
group_list = []
filename_list = []
skillnumber_list = []

global data, full_data
for filename in imageList:
    temp = filename[:-4]
    temp = temp.split('_')
    event_list.append(temp[0])
    value_list.append(temp[1])
    group_list.append(temp[2])
    skillnumber_list.append(temp[3])
    filename_list.append(filename)
data = pd.DataFrame(columns=['Event', 'Value', 'EG', 'Skill_Number'])
data['Event'] = event_list
data['Value'] = value_list
data['EG'] = group_list
data['Skill_Number'] = skillnumber_list
data['Filename'] = filename_list
full_data = data
# =================================================================================

server = flask.Flask(__name__)


app = dash.Dash(__name__, external_stylesheets=[
                dbc.themes.LITERA], server=server)

app.title = "MAG COP Trainer"

BUTTON_MARGIN = '10px'
BUTTON_WIDTH = '100px'
BUTTON_HEIGHT = '50px'
# App Start =======================================================================
app.layout = html.Div(children=[
    html.Div(id='Main_Div', children=[
        html.H4(children='MAG COP Trainer 2022'),
        html.H6(children='By Brandon Ngai'),


        # Dash div containing image and sidebar
        html.Div(id='Dash_Div', children=[
            html.Div(id='Left_Sidebar_Div', children=[
                html.H6(id='correct_stat', children='Correct: 0',
                        className='card-title'),
                html.H6(id='attempts_stat', children='Attempts: 0',
                        className='card-title'),
                html.H6(id='percent_stat', children='Percent: 0.0%',
                        className='card-title')
            ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center', 'justify-content': 'center'}),

            # Image display
            html.Img(id='Image',
                     src='', style={'max-width': '100%', 'max-height': '100%', 'min-height': '200px', 'min-width': '200px'}),

            html.Div(id='Right_Sidebar_Div', children=[
                html.H6('Filter:'),
                dbc.Button('FX', id={'type':'Event_Button','index':0}, className='btn-success', style = {'width':'30%'}),
                dbc.Button('PH', id={'type':'Event_Button','index':1}, className='btn-success', style = {'width':'30%', 'margin-top':BUTTON_MARGIN}),
                dbc.Button('SR', id={'type':'Event_Button','index':2}, className='btn-success', style = {'width':'30%', 'margin-top':BUTTON_MARGIN}),
                dbc.Button('PB', id={'type':'Event_Button','index':3}, className='btn-success', style = {'width':'30%', 'margin-top':BUTTON_MARGIN}),
                dbc.Button('HB', id={'type':'Event_Button','index':4}, className='btn-success', style = {'width':'30%', 'margin-top':BUTTON_MARGIN})
            ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center', 'justify-content': 'center'}),
        ], className='container', style={'display': 'grid', 'grid-template-columns': '1fr 1fr 1fr', 'height': '40%'}),  # May need to tweak height settings

        html.Div(id='Button_Div', children=[
            dbc.Button('A', id={'type': 'Value_Button', 'index': 0},
                       className='btn-primary', color='Primary', style={'width': BUTTON_WIDTH, 'height': BUTTON_HEIGHT}),
            dbc.Button('B', id={'type': 'Value_Button', 'index': 1},
                       className='btn, btn-primary', color='Primary', style={'margin-left': BUTTON_MARGIN, 'width': BUTTON_WIDTH, 'height': BUTTON_HEIGHT}),
            dbc.Button('C', id={'type': 'Value_Button', 'index': 2},
                       className='btn, btn-primary', color='Primary', style={'margin-left': BUTTON_MARGIN, 'width': BUTTON_WIDTH, 'height': BUTTON_HEIGHT}),
            dbc.Button('D', id={'type': 'Value_Button', 'index': 3},
                       className='btn, btn-primary', color='Primary', style={'margin-left': BUTTON_MARGIN, 'width': BUTTON_WIDTH, 'height': BUTTON_HEIGHT}),
            dbc.Button('E', id={'type': 'Value_Button', 'index': 4},
                       className='btn, btn-primary', color='Primary', style={'margin-left': BUTTON_MARGIN, 'width': BUTTON_WIDTH, 'height': BUTTON_HEIGHT}),
            dbc.Button('F', id={'type': 'Value_Button', 'index': 5},
                       className='btn, btn-primary', color='Primary', style={'margin-left': BUTTON_MARGIN, 'width': BUTTON_WIDTH, 'height': BUTTON_HEIGHT}),
            dbc.Button('G', id={'type': 'Value_Button', 'index': 6},
                       className='btn, btn-primary', color='Primary', style={'margin-left': BUTTON_MARGIN, 'width': BUTTON_WIDTH, 'height': BUTTON_HEIGHT}),
            dbc.Button('H', id={'type': 'Value_Button', 'index': 7},
                       className='btn, btn-primary', color='Primary', style={'margin-left': BUTTON_MARGIN, 'width': BUTTON_WIDTH, 'height': BUTTON_HEIGHT}),
            dbc.Button('I', id={'type': 'Value_Button', 'index': 8},
                       className='btn, btn-primary', color='Primary', style={'margin-left': BUTTON_MARGIN, 'width': BUTTON_WIDTH, 'height': BUTTON_HEIGHT})
        ], style={'height': '10%', 'display': 'flex', 'justify-content': 'center', 'margin-top': '50px'}),

        html.Div(id='Next_Button_Div', children=[
            dbc.Button('Next Skill', id="Next_Button",
                       className='btn, btn-secondary', color='Secondary', style={'width': '870px'}, n_clicks=0)
        ], style={'display': 'flex', 'justify-content': 'center', 'margin-top': '20px'})

    ], style={'margin-left': '10%', 'margin-right': '10%'}),
    dcc.Store(id='session_data'),
    dcc.Store(id='solution_data'),
    html.Div(id='test_out', children='')
])

### Load new image
@app.callback(
    Output(component_id='Image', component_property='src'),
    Output(component_id='solution_data', component_property='data'),
    Input(component_id='Next_Button', component_property='n_clicks'),
    State(component_id='solution_data', component_property='data'),
    State(component_id={'type': 'Event_Button', 'index': ALL},
        component_property='className')
)
def load_new_image(n_clicks, solution_data, event_filter_state):
    # Initialize everything
    if n_clicks == 0:
        encoded_image = base64.b64encode(
            open('Skill Images/welcome.png', 'rb').read())
        solution_data_out = dict({'solution': ''})
        return('data:image/png;base64,{}'.format(encoded_image.decode()), json.dumps(solution_data_out))
    else:
        solution_data_out = json.loads(solution_data)

        event_filter_state = [ True if x == "btn-success" else False for x in event_filter_state  ]
        event_filter = list(compress(["FX", "PH", "SR", "PB", "HB"], event_filter_state))

        # Filter down available data by event
        filtered_data = data[data["Event"].isin(event_filter)].reset_index(drop=True) 
        print(filtered_data)

        i = randrange(0, filtered_data.shape[0])
        img_file = filtered_data["Filename"][i]
        solution = filtered_data['Value'][i]
        encoded_image = base64.b64encode(
            open('Skill Images/' + img_file, 'rb').read())
        # Update Solution in Session Data
        solution_data_out['solution'] = solution
        value_map_dict = {"A": 0, "B": 1, "C": 2,
                          "D": 3, "E": 4, "F": 5, "G": 6, "H": 7, "I": 8}
        solution_data_out['solution_index'] = value_map_dict[solution]
        return('data:image/png;base64,{}'.format(encoded_image.decode()), json.dumps(solution_data_out))

# Callback to check the solution

# Updates the Session Data between images.


@app.callback(
    Output(component_id='session_data', component_property='data'),
    Input(component_id={'type': 'Value_Button',
                        'index': ALL}, component_property='n_clicks'),
    State(component_id='Next_Button', component_property='n_clicks'),
    State(component_id='session_data', component_property='data'),
    State(component_id='solution_data', component_property='data'),

)
def check_solution(value_n_clicks, next_n_clicks, session_data, solution_data):
    if next_n_clicks == 0:
        session_data = {'attempts': 0, 'correct': 0,
                        'enable_buttons': True, 'selected_index': None}
        return(json.dumps(session_data))

    else:
        solution_data = json.loads(solution_data)
        session_data = json.loads(session_data)

        # Determine index of button pressed
        trigger = dash.callback_context.triggered[0]
        index = json.loads(trigger["prop_id"].split(".")[0])["index"]
        # Add one to the attempt
        session_data['attempts'] += 1
        session_data['enable_buttons'] = False
        session_data['selected_index'] = index
        # Determine if correct or incorrect
        if index == solution_data['solution_index']:
            session_data['correct'] += 1

        return(json.dumps(session_data))

# Disabled buttons toggle


@app.callback(
    Output(component_id={'type': 'Value_Button', 'index': ALL},
           component_property='disabled'),
    Output(component_id="Next_Button", component_property='disabled'),
    Input(component_id='Next_Button', component_property='n_clicks'),
    Input(component_id={'type': 'Value_Button',
                        'index': ALL}, component_property='n_clicks'),
)
def toggle_buttons(next_n_clicks, value_n_clicks):
    if next_n_clicks > 0:
        trigger = dash.callback_context.triggered[0]
        trigger = trigger["prop_id"].split(".")[0]

        if trigger != "Next_Button":
            return([True]*9, False)

        else:
            return([False]*9, True)

    return([True] * 9, False)


# Changes button colors to signify which button is correct.
@app.callback(
    Output(component_id={'type': 'Value_Button', 'index': ALL},
           component_property='className'),
    Output(component_id={'type': 'Value_Button', 'index': ALL},
           component_property='children'),
    Input(component_id={'type': 'Value_Button', 'index': ALL},
          component_property='n_clicks'),
    Input(component_id='Next_Button', component_property='n_clicks'),
    State(component_id='solution_data', component_property='data')
)
def change_button_colors(value_n_clicks, next_n_clicks, solution_data):
    if next_n_clicks > 0:

        trigger = dash.callback_context.triggered[0]
        trigger = trigger["prop_id"].split(".")[0]
        # Change color depending on solution
        if trigger != "Next_Button":
            # get the index of the pressed button
            trigger = dash.callback_context.triggered[0]
            selected_index = json.loads(
                trigger["prop_id"].split(".")[0])["index"]
            solution_data = json.loads(solution_data)

            out_state = ["btn-primary"] * 9
            text_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
            # Correct solution
            if selected_index == solution_data['solution_index']:
                out_state[selected_index] = "btn-success"
                text_list[selected_index] = "Correct"
                return(out_state, text_list)
            else:
                out_state[selected_index] = "btn-danger"
                out_state[solution_data['solution_index']] = "btn-success"
                text_list[selected_index] = "Incorrect"
                text_list[solution_data['solution_index']] = "Correct"
                return(out_state, text_list)
    return(["btn-primary"] * 9, ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'])


# Changes color of event filter buttons when pressed
@app.callback(
    Output(component_id={'type': 'Event_Button', 'index': ALL},
           component_property='className'),
    Input(component_id={'type': 'Event_Button', 'index': ALL},
          component_property='n_clicks'),
    State(component_id={'type': 'Event_Button', 'index': ALL},
          component_property='className')

)
def change_filter_colors(event_n_clicks, initial_state):
    # Index of button that has changed
    if dash.callback_context.triggered[0]["prop_id"] != '.':
        trigger = dash.callback_context.triggered[0]
        index = json.loads(trigger["prop_id"].split(".")[0])["index"]
        if initial_state[index] == 'btn-success':
            initial_state[index] = 'btn-secondary'
        else:
            initial_state[index] = 'btn-success'
        return(initial_state)
    else:
        return(initial_state)
    




@app.callback(
    Output(component_id='correct_stat', component_property='children'),
    Output(component_id='attempts_stat', component_property='children'),
    Output(component_id='percent_stat', component_property='children'),
    #Input(component_id='Next_Button', component_property='n_clicks'),
    Input(component_id='session_data', component_property='data')
)
def update_stats(session_data):
    session_data = json.loads(session_data)
    stat1 = "Correct: {}".format(session_data['correct'])
    stat2 = "Attempts: {}".format(session_data['attempts'])
    if session_data['attempts'] == 0:
        return(stat1, stat2, "Percent: 0%")
    else:
        stat3 = "Percent: {:.1f}%".format(
            (session_data['correct']/session_data['attempts'])*100)
        return(stat1, stat2, stat3)


if __name__ == '__main__':
    app.run_server(debug=True)
