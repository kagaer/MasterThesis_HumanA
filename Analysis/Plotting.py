from typing import List, Tuple, Union
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import enum
from MultipleUseFunctions import *

hex_colors = ["#F2CC8F", '#D7C48F', '#BBBB8E', '#A0B28D', '#84A98C', '#6F9B77', '#64906C', '#5D8364', '#3D5141']

#hex_colors = ['#FBEDDA', "#F7DDB5", "#F2CC8F", '#D7C48F', '#BBBB8E', '#A0B28D', '#84A98C', '#6F9B77', '#64906C', '#5D8364']

# Generate the continuous colorscale
num_colors = len(hex_colors)
colorscale = [[i/(num_colors-1), color] for i, color in enumerate(hex_colors)]

def plotTotal(matrix, count_seeking, count_avoiding, participant = None,  sessions = (1,2,3,4,5), participants = None, weights_adjusted = '', 
              save_path = "E:/HumanA/Default/"):
    #save_path = "E:/HumanA/Analysis/StrategyMatrices/"
    #if experiment == 1:
    #    save_path = save_path + "Exp1/Dec_Expl_Matrix/"
    #elif experiment == 2:
    #    save_path = save_path + "Exp2/Dec_Expl_Matrix/"


    if participant != None:
        filename = str(participant) + "_Decision_Matrix_Avatars_Total" +  ".png"
    else:
        nr_participants = len(participants)
        filename = "AllParticipants_Decision_Matrix_Avatars_Total" + ".png"
        participant = 'All Participants (n = ' + str(nr_participants) + ")" 

    #total_decisions = "Total Decisions Agent Seeking: " + str(count_seeking) + " | Total Decisions Agent Avoiding: " + str(count_avoiding)
    title = "Participant: " + str(participant)  + weights_adjusted #+ "<br>" + total_decisions

    sum_avatAtChos = matrix[0][0].sum() + matrix[0][1].sum() + matrix[0][2].sum() +  matrix[0][3].sum() + matrix[0][4].sum()
    sum_avatAtNotChos = matrix[1][0].sum() + matrix[1][1].sum() + matrix[1][2].sum() +  matrix[1][3].sum() + matrix[1][4].sum()
    sum_avatAtBoth = matrix[2][0].sum() + matrix[2][1].sum() + matrix[2][2].sum() +  matrix[2][3].sum() + matrix[2][4].sum()
    sum_NoavatAtBoth = matrix[3][0].sum() + matrix[3][1].sum() + matrix[3][2].sum() +  matrix[3][3].sum() + matrix[3][4].sum() 
    sum_Total = sum_avatAtChos + sum_avatAtNotChos + sum_avatAtBoth + sum_NoavatAtBoth

    perc_avatAtChos = round((sum_avatAtChos/sum_Total), 2)
    perc_avatAtNotChos = round((sum_avatAtNotChos/sum_Total), 2)
    perc_avatAtBoth = round((sum_avatAtBoth/sum_Total), 2)
    perc_NoavatAtBoth = round((sum_NoavatAtBoth/sum_Total), 2)

    diagonal_lines = [
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.825, 'y1': 1, 'x0': 0, 'x1': 0.168},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.825, 'y1': 1, 'x0': 0.208, 'x1': 0.376},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.825, 'y1': 1, 'x0': 0.417, 'x1': 0.584},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.825, 'y1': 1, 'x0': 0.624, 'x1': 0.792},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.825, 'y1': 1, 'x0': 0.832, 'x1': 1},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.55, 'y1': 0.725, 'x0': 0, 'x1': 0.168},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.55, 'y1': 0.725, 'x0': 0.208, 'x1': 0.376},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.55, 'y1': 0.725, 'x0': 0.417, 'x1': 0.584},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.55, 'y1': 0.725, 'x0': 0.624, 'x1': 0.792},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.55, 'y1': 0.725, 'x0': 0.832, 'x1': 1},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.275, 'y1': 0.451, 'x0': 0, 'x1': 0.168},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.275, 'y1': 0.451, 'x0': 0.208, 'x1': 0.376},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.275, 'y1': 0.451, 'x0': 0.417, 'x1': 0.584},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.275, 'y1': 0.451, 'x0': 0.624, 'x1': 0.792},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.275, 'y1': 0.451, 'x0': 0.832, 'x1': 1},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0, 'y1': 0.175, 'x0': 0, 'x1': 0.168},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0, 'y1': 0.175, 'x0': 0.208, 'x1': 0.376},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0, 'y1': 0.175, 'x0': 0.417, 'x1': 0.584},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0, 'y1': 0.175, 'x0': 0.624, 'x1': 0.792},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0, 'y1': 0.175, 'x0': 0.832, 'x1': 1}      
            ]  

    fig = make_subplots(
        rows=4, 
        cols=5, 
        subplot_titles=("Agent at Chosen Direction (" + str(perc_avatAtChos) + "): <br>" + "Session 1:" , "Session 2: ", "Session 3","Session 4", "Session 5",
                        "Agent at not Chosen Direction (" + str(perc_avatAtNotChos) + "): <br>Session 1", "Session 2", "Session 3", "Session 4", "Session 5",
                        "Agent at both Directions (" + str(perc_avatAtBoth) + "):<br>Session 1", "Session 2", "Session 3", "Session 4", "Session 5",
                        "No Agent at both Directions (" + str(perc_NoavatAtBoth) + "): <br>Session 1", "Session 2", "Session 3", "Session 4", "Session 5"), 
        x_title="Number of previous visits not chosen nodes", 
        y_title="Number of previous visits chosen node",
        vertical_spacing = 0.1
        )
    #fig = make_subplots(
    #    rows=4, 
    #    cols=5, 
    #    subplot_titles=("Agent at Chosen Direction: <br>Session 1", "Session 2", "Session 3", "Session 4", "Session 5",
    #                    "Agent at not Chosen Direction <br>Session 1", "Session 2", "Session 3", "Session 4", "Session 5",
    #                    "Agent at both Directions <br>Session 1", "Session 2", "Session 3", "Session 4", "Session 5",
    #                    "No Agent at both Directions <br>Session 1", "Session 2", "Session 3", "Session 4", "Session 5"), 
    #    x_title="Number of previous avoiding decisions", 
    #    y_title="Number of previous seeking decisions",
    #    vertical_spacing = 0.1
    #    )

    fig.update_layout(margin=dict(t=200))
    for i in range(4):
        for session in sessions:
            if len(matrix[i][session-1]) > 0:
                count_cons, count_expl, count_total = getStrategyCounts(matrix[i][session-1])
                perc_cons = round((count_cons/count_total), 2)
                perc_expl = round((count_expl/count_total),2)

                matrix_text = np.array(np.array(matrix[i][session-1],dtype='int'),dtype='str')
                matrix_text[matrix_text == '0'] = ""
                #colorscale = "Sunset"
                fig.add_trace(go.Heatmap(z=matrix[i][session-1], text=matrix_text, texttemplate="%{text}", textfont={"size":12}, colorscale = colorscale,), 
                    row=i+1, col=session)
                fig.update_traces(showscale=False)
                fig.add_annotation(text = "Expl: " + str(count_expl) + " " + "(" + str(perc_expl) + ")"
                        "<br>Cons: " + str(count_cons) + " " + "(" + str(perc_cons) + ")",
                    showarrow=False,
                    bordercolor='black',
                    borderwidth=1,
                    x = 0, y = 1,
                    xanchor= 'left', yanchor='top',
                    xref = 'x domain', yref = 'y domain',
                    align="left",
                    name="Strategy Counts", row=i+1, col = session)

    fig.update_layout(
                title_text=title,
                boxmode='group',
                width=2000,
                height=2000,
                shapes=diagonal_lines,
                font=dict(
                    size=18,
                    )
            )
    fig.write_image((save_path + filename))


def plotSession(matrix, count_seeking, count_avoiding, participant = None,  sessions = (1,2,3,4,5), participants = None, weights_adjusted = '', 
                save_path = "E:/HumanA/Default/"):
    #save_path = "E:/HumanA/Analysis/StrategyMatrices/"
    #if experiment == 1:
    #    save_path = save_path + "Exp1/Dec_Expl_Matrix/"
    #elif experiment == 2:
    #    save_path = save_path + "Exp2/Dec_Expl_Matrix/"

    if participant != None:
        filename = str(participant) + "_Decision_Matrix_Avatars_Session" +  ".png"
    else:
        nr_participants = len(participants)
        filename = "AllParticipants_Decision_Matrix_Avatars_Session" + ".png"
        participant = 'All Participants (n = ' + str(nr_participants) + ")"

    
    title = "Participant: " + str(participant) + weights_adjusted + "<br>" 

    sum_avatAtChos = matrix[0][0].sum() + matrix[0][1].sum() + matrix[0][2].sum() +  matrix[0][3].sum() + matrix[0][4].sum()
    sum_avatAtNotChos = matrix[1][0].sum() + matrix[1][1].sum() + matrix[1][2].sum() +  matrix[1][3].sum() + matrix[1][4].sum()
    sum_avatAtBoth = matrix[2][0].sum() + matrix[2][1].sum() + matrix[2][2].sum() +  matrix[2][3].sum() + matrix[2][4].sum()
    sum_NoavatAtBoth = matrix[3][0].sum() + matrix[3][1].sum() + matrix[3][2].sum() +  matrix[3][3].sum() + matrix[3][4].sum() 
    sum_Total = sum_avatAtChos + sum_avatAtNotChos + sum_avatAtBoth + sum_NoavatAtBoth

    perc_avatAtChos = round((sum_avatAtChos/sum_Total), 2)
    perc_avatAtNotChos = round((sum_avatAtNotChos/sum_Total), 2)
    perc_avatAtBoth = round((sum_avatAtBoth/sum_Total), 2)
    perc_NoavatAtBoth = round((sum_NoavatAtBoth/sum_Total), 2)


    diagonal_lines = [
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.825, 'y1': 1, 'x0': 0, 'x1': 0.168},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.825, 'y1': 1, 'x0': 0.208, 'x1': 0.376},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.825, 'y1': 1, 'x0': 0.417, 'x1': 0.584},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.825, 'y1': 1, 'x0': 0.624, 'x1': 0.792},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.825, 'y1': 1, 'x0': 0.832, 'x1': 1},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.55, 'y1': 0.725, 'x0': 0, 'x1': 0.168},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.55, 'y1': 0.725, 'x0': 0.208, 'x1': 0.376},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.55, 'y1': 0.725, 'x0': 0.417, 'x1': 0.584},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.55, 'y1': 0.725, 'x0': 0.624, 'x1': 0.792},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.55, 'y1': 0.725, 'x0': 0.832, 'x1': 1},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.275, 'y1': 0.451, 'x0': 0, 'x1': 0.168},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.275, 'y1': 0.451, 'x0': 0.208, 'x1': 0.376},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.275, 'y1': 0.451, 'x0': 0.417, 'x1': 0.584},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.275, 'y1': 0.451, 'x0': 0.624, 'x1': 0.792},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.275, 'y1': 0.451, 'x0': 0.832, 'x1': 1},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0, 'y1': 0.175, 'x0': 0, 'x1': 0.168},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0, 'y1': 0.175, 'x0': 0.208, 'x1': 0.376},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0, 'y1': 0.175, 'x0': 0.417, 'x1': 0.584},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0, 'y1': 0.175, 'x0': 0.624, 'x1': 0.792},
        {'type': 'line', 'line': { 'color': '#b36a5e', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0, 'y1': 0.175, 'x0': 0.832, 'x1': 1}   
            ]  
    #session_decisions = []
    #for i in range(5):
        #decision_text_sessions = "Agent Seeking: " + str(count_seeking[i]) + " | Agent Avoiding: " + str(count_avoiding[i]) + "<br><br>"
        #session_decisions.append(decision_text_sessions)
    
    fig = make_subplots(
        rows=4, 
        cols=5, 
        subplot_titles=("Agent at Chosen Direction (" + str(perc_avatAtChos) + "): <br>" + "Session 1:" ,  "<br>Session 2: ", 
            "<br>Session 3", "<br>Session 4",  "<br>Session 5",
                        "Agent at not Chosen Direction (" + str(perc_avatAtNotChos) + "): <br>Session 1", "Session 2", "Session 3", "Session 4", "Session 5",
                        "Agent at both Directions (" + str(perc_avatAtBoth) + "):<br>Session 1", "Session 2", "Session 3", "Session 4", "Session 5",
                        "No Agent at both Directions (" + str(perc_NoavatAtBoth) + "): <br>Session 1", "Session 2", "Session 3", "Session 4", "Session 5"), 
        x_title="Number of previous visits not chosen nodes", 
        y_title="Number of previous visits chosen node",
        vertical_spacing = 0.1
        )

    fig.update_layout(margin=dict(t=200))
    for i in range(4):
        for session in sessions:

            if len(matrix[i][session-1]) > 0:
                count_cons, count_expl, count_total = getStrategyCounts(matrix[i][session-1])
                perc_cons = round((count_cons/count_total), 2)
                perc_expl = round((count_expl/count_total),2)

                matrix_text = np.array(np.array(matrix[i][session-1],dtype='int'),dtype='str')
                matrix_text[matrix_text == '0'] = ""
                #colorscale = "Sunset"
                fig.add_trace(go.Heatmap(z=matrix[i][session-1], text=matrix_text, texttemplate="%{text}", textfont={"size":12}, colorscale = colorscale,), 
                    row=i+1, col=session)
                fig.update_traces(showscale=False)
                fig.add_annotation(text = "Expl: " + str(count_expl) + " " + "(" + str(perc_expl) + ")"
                        "<br>Cons: " + str(count_cons) + " " + "(" + str(perc_cons) + ")",
                    showarrow=False,
                    bordercolor='black',
                    borderwidth=1,
                    x = 0, y = 1,
                    xanchor= 'left', yanchor='top',
                    xref = 'x domain', yref = 'y domain', 
                    align="left",
                    name="Strategy Counts", row=i+1, col = session)
    fig.update_layout(
                title_text=title,
                boxmode='group',
                width=2000,
                height=2000,
                shapes=diagonal_lines,
                font=dict(
                    size=18,
                    )
            )
    fig.write_image((save_path + filename))