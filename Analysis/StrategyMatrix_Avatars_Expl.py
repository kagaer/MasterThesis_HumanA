import sqlite3
from pathlib import Path
from typing import List, Tuple, Union
import numpy as np
import seaborn as sns
import matplotlib.pylab as plt
import matplotlib as mpl
import plotly.colors
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import enum
#from GetPlotlyColorScale import *
from MultipleUseFunctions import * 

# path to databases
print("For which experiment would you like to analyize the data?")
experiment = int(input())
if experiment == 1:
    db_path = Path('E:/HumanA/Data/Database/HumanA_Exp1.db')
    #db_path = Path('E:/HumanA/Data/HumanA_Exp1_WorkingData.db')
elif experiment == 2:
    db_path = Path('E:/HumanA/Data/Database/HumanA_Exp2.db')
    #db_path = Path('E:/HumanA/Data/HumanA_Exp2_WorkingData.db')

# 
#print("Full Dataset (1) or only consecutive Data (2)?")
#dataSet = int(input())
#if experiment == 1:
#    #db_path = Path('E:/HumanA/Data/HumanA_Exp1_WorkingData.db')
#elif experiment == 2:
#    #db_path = Path('E:/HumanA/Data/HumanA_Exp2_WorkingData.db')

# check if path exists
if not db_path or not db_path.exists():
    db_path = ':memory:'

# connect to database
connection=sqlite3.connect(db_path)
cr=connection.cursor()


temp_count_avoiding = 0
temp_count_seeking = 0

class TrialValidity(enum.Enum):
    Valid = 1
    MissingTrial = 2
    MissingSession = 3
    Undefined = 4


#def getParticipants():
#    """get all participantIds from the database
#
#    Returns:
#        tuple: list of participants
#    """
#    # select all participantIds and return them
#    sql_instruction = """
#    SELECT DISTINCT participantId FROM trials WHERE validParticipant = 'VALID';
#    """
#    cr.execute(sql_instruction)
#    participants = tuple(did[0] for did in cr.fetchall())
#    return participants

#def getSessions(participant):
#    """get all sessionNrs for the current participant from the database
#
#    Returns:
#        tuple: list of participants
#    """
#    # select all participantIds and return them
#    sql_instruction = f"""
#    SELECT DISTINCT sessionNr FROM trials WHERE participantId = {participant} AND validSession = 'VALID'
#    ORDER BY sessionNr;
#    """
#    cr.execute(sql_instruction)
#    sessions = tuple(did[0] for did in cr.fetchall())
#    return sessions

#def getTrialNrs(participant, session):
#    """get all trialIds for the current participant, current session
#
#    Args:
#        participant (int): current participant
#
#    Returns:
#        tuple: all trialIds 
#    """
#
#    sql_instruction = f"""
#    SELECT DISTINCT id 
#    FROM trials
#    WHERE participantId = {participant} AND sessionNr = {session}
#    """
#    
#    cr.execute(sql_instruction)
#    trialIdx = tuple(did[0] for did in cr.fetchall())
#    return trialIdx

#def getDatapoints(trials, cr):
#    """get all datapoints for the current trial, sorted by the timestamp (timeStampDataPointStart), and joined with the trialId and participantId
#
#    Args:
#        trial (int): current trial
#
#    Returns:
#        list: all datapoints for this trial 
#    """
#
#    sql_instruction = f"""
#    SELECT dataPoints_analysis.trialId, dataPoints_analysis.DatapointId, dataPoints_analysis.timeStampDataPointStart, dataPoints_analysis.node
#    FROM dataPoints_analysis
#    WHERE dataPoints_analysis.trialId IN {trials}
#    ORDER BY dataPoints_analysis.timeStampDataPointStart ASC
#    ;
#        """
#    cr.execute(sql_instruction)
#    data = cr.fetchall()
#    return data

#def getDecisions(dp_id):
#    sql_instruction = f"""
#    SELECT participant_decision.Id, participant_decision.last_node_neighbour, participant_decision.decision
#    FROM participant_decision
#    WHERE participant_decision.datapointId = {dp_id}
#    ;
#        """
#    cr.execute(sql_instruction)
#    decisions = cr.fetchall()
#    return decisions

#def getMaxNodeFromDB():
#    """get the max node from the database
#
#    Returns:
#        max_node (int): max node
#    """
#
#    sql_instruction = f"""
#    SELECT MAX(nodeNr) FROM graph_coordinates
#    """
#    
#    cr.execute(sql_instruction)
#    max_node = cr.fetchone()
#    #maxNode = tuple(did[0] for did in cr.fetchall())
#    return max_node[0]

#def resize_matrix(matrix, shape):
#    # resize the current strategy matrix, fill up, so that it matches the new shape
#    shape_diff = np.array(shape) - np.array(matrix.shape)
#    return np.lib.pad(matrix, ((0,shape_diff[0]),(0,shape_diff[1])), 'constant', constant_values=(0))

def getVisits(node):
    visits_participant_total = visits_node_participant_total[node]
    visits_participant_currentSes = visits_node_participant_currentSes[node]

    visits_total = visits_node_total[node]
    visits_currentSes = visits_node_perSession[node]

    return visits_participant_total,visits_participant_currentSes,visits_total,visits_currentSes


def getCountDecisions(dp_ids):
    sql_instruction = f"""SELECT COUNT(decision) FROM participant_decision WHERE datapointId IN {dp_ids} AND decision = 'AvatarAtChosen'"""
    cr.execute(sql_instruction)
    count_Avatar_Seeking = cr.fetchone()

    sql_instruction = f"""SELECT COUNT(decision) FROM participant_decision WHERE datapointId IN {dp_ids} AND decision = 'AvatarAtNotChosen'"""
    cr.execute(sql_instruction)
    count_Avatar_Avoiding = cr.fetchone()
    return count_Avatar_Seeking[0], count_Avatar_Avoiding[0]

def getCountDecisionsTotal():
    sql_instruction = f"""SELECT COUNT(decision) FROM participant_decision WHERE decision = 'AvatarAtChosen'"""
    cr.execute(sql_instruction)
    count_Avatar_Seeking = cr.fetchone()

    sql_instruction = f"""SELECT COUNT(decision) FROM participant_decision WHERE decision = 'AvatarAtNotChosen'"""
    cr.execute(sql_instruction)
    count_Avatar_Avoiding = cr.fetchone()
    return count_Avatar_Seeking[0], count_Avatar_Avoiding[0]

def getCountDecisionsSessionTotal():
    sql_instruction = f"""SELECT COUNT(participant_decision.decision) FROM trials
        LEFT JOIN datapoints_analysis ON trials.id = datapoints_analysis.trialId
            LEFT JOIN participant_decision ON datapoints_analysis.datapointId = participant_decision.datapointId
            WHERE decision = 'AvatarAtChosen'
            GROUP BY trials.sessionNr"""
    cr.execute(sql_instruction)
    count_Avatar_Seeking = tuple(did[0] for did in cr.fetchall())

    sql_instruction = f"""SELECT COUNT(participant_decision.decision) FROM trials
        LEFT JOIN datapoints_analysis ON trials.id = datapoints_analysis.trialId
            LEFT JOIN participant_decision ON datapoints_analysis.datapointId = participant_decision.datapointId
            WHERE decision = 'AvatarAtNotChosen'
            GROUP BY trials.sessionNr"""
    cr.execute(sql_instruction)
    count_Avatar_Avoiding = [did[0] for did in cr.fetchall()]
    return count_Avatar_Seeking, count_Avatar_Avoiding

#def addUpMatrices(matrix1, matrix2):
## iterate through rows
#    result = matrix1
#    for i in range(len(matrix2)):  
#    # iterate through columns
#        for j in range(len(matrix2[0])):
#            result[i][j] = matrix1[i][j] + matrix2[i][j]
#    
#    return result



def plotTotal(matrix, count_seeking, count_avoiding, participant = None, sessions = (1,2,3,4,5), weights_adjusted = ''):
    save_path = "E:/HumanA/Analysis/StrategyMatrices/"
    if experiment == 1:
        save_path = save_path + "Exp1/Dec_Expl_Matrix/"
    elif experiment == 2:
        save_path = save_path + "Exp2/Dec_Expl_Matrix/"
    
    #if dataSet == 1:
    #    save_path = save_path + "FullDataSet/Dec_Expl_Matrix/"
    #elif dataSet == 2:
    #    save_path = save_path + "ConsDataSet/Dec_Expl_Matrix/"


    if participant != None:
        filename = str(participant) + "_Decision_Matrix_Avatars_Total" +  ".png"
    else:
        nr_participants = len(participants)
        filename = "AllParticipants_Decision_Matrix_Avatars_Total" + ".png"
        participant = 'All Participants (n = ' + str(nr_participants) + ")" 

    total_decisions = "Total Decisions Agent Seeking: " + str(count_seeking) + " | Total Decisions Agent Avoiding: " + str(count_avoiding)
    title = "Participant: " + str(participant)  + weights_adjusted + "<br>" + total_decisions

    diagonal_lines = [
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.825, 'y1': 1, 'x0': 0, 'x1': 0.168},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.825, 'y1': 1, 'x0': 0.208, 'x1': 0.376},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.825, 'y1': 1, 'x0': 0.417, 'x1': 0.584},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.825, 'y1': 1, 'x0': 0.624, 'x1': 0.792},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.825, 'y1': 1, 'x0': 0.832, 'x1': 1},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.55, 'y1': 0.725, 'x0': 0, 'x1': 0.168},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.55, 'y1': 0.725, 'x0': 0.208, 'x1': 0.376},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.55, 'y1': 0.725, 'x0': 0.417, 'x1': 0.584},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.55, 'y1': 0.725, 'x0': 0.624, 'x1': 0.792},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.55, 'y1': 0.725, 'x0': 0.832, 'x1': 1},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.275, 'y1': 0.451, 'x0': 0, 'x1': 0.168},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.275, 'y1': 0.451, 'x0': 0.208, 'x1': 0.376},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.275, 'y1': 0.451, 'x0': 0.417, 'x1': 0.584},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.275, 'y1': 0.451, 'x0': 0.624, 'x1': 0.792},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.275, 'y1': 0.451, 'x0': 0.832, 'x1': 1},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0, 'y1': 0.175, 'x0': 0, 'x1': 0.168},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0, 'y1': 0.175, 'x0': 0.208, 'x1': 0.376},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0, 'y1': 0.175, 'x0': 0.417, 'x1': 0.584},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0, 'y1': 0.175, 'x0': 0.624, 'x1': 0.792},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0, 'y1': 0.175, 'x0': 0.832, 'x1': 1}      
            ]  

    fig = make_subplots(
        rows=4, 
        cols=5, 
        subplot_titles=("Agent at Chosen Direction: <br>Session 1", "Session 2", "Session 3", "Session 4", "Session 5",
                        "Agent at not Chosen Direction <br>Session 1", "Session 2", "Session 3", "Session 4", "Session 5",
                        "Agent at both Directions <br>Session 1", "Session 2", "Session 3", "Session 4", "Session 5",
                        "No Agent at both Directions <br>Session 1", "Session 2", "Session 3", "Session 4", "Session 5"), 
        x_title="Number of previous avoiding decisions", 
        y_title="Number of previous seeking decisions",
        vertical_spacing = 0.1
        )
    #fig.update_annotations(font_size=16)
        #row_titles = ('Sessions Combined', 'Sessions Seperated')
    fig.update_layout(margin=dict(t=200))
    for i in range(4):
        for session in sessions:
            if len(matrix[i][session-1]) > 0:
                count_cons, count_expl, count_total = getStrategyCounts(matrix[i][session-1])
                perc_cons = round((count_cons/count_total), 2)
                perc_expl = round((count_expl/count_total),2)
                #filename = "Strategy_Matrix_" + str(participant) + "_Session_" + str(session) + ".png"
                matrix_text = np.array(np.array(matrix[i][session-1],dtype='int'),dtype='str')
                matrix_text[matrix_text == '0'] = ""
                colorscale = "Sunset"
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
                    xref = 'x domain', yref = 'y domain', #'paper',
                    align="left",#valign = "top", 
                    name="Strategy Counts", row=i+1, col = session)
                #fig.update_traces(name = "Strategy Counts", textposition = 'top right')
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
    #print()

def plotSession(matrix, count_seeking, count_avoiding, participant = None, sessions = (1,2,3,4,5)):
    save_path = "E:/HumanA/Analysis/StrategyMatrices/"
    if experiment == 1:
        save_path = save_path + "Exp1/Dec_Expl_Matrix/"
    elif experiment == 2:
        save_path = save_path + "Exp2/Dec_Expl_Matrix/"
    
    #if dataSet == 1:
    #    save_path = save_path + "FullDataSet/Dec_Expl_Matrix/"
    #elif dataSet == 2:
    #    save_path = save_path + "ConsDataSet/Dec_Expl_Matrix/"


    if participant != None:
        filename = str(participant) + "_Decision_Matrix_Avatars_Session" +  ".png"
    else:
        nr_participants = len(participants)
        filename = "AllParticipants_Decision_Matrix_Avatars_Session" + ".png"
        participant = 'All Participants (n = ' + str(nr_participants) + ")"

    
    title = "Participant: " + str(participant) +  "<br>" #+ total_decisions

    diagonal_lines = [
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.825, 'y1': 1, 'x0': 0, 'x1': 0.168},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.825, 'y1': 1, 'x0': 0.208, 'x1': 0.376},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.825, 'y1': 1, 'x0': 0.417, 'x1': 0.584},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.825, 'y1': 1, 'x0': 0.624, 'x1': 0.792},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.825, 'y1': 1, 'x0': 0.832, 'x1': 1},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.55, 'y1': 0.725, 'x0': 0, 'x1': 0.168},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.55, 'y1': 0.725, 'x0': 0.208, 'x1': 0.376},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.55, 'y1': 0.725, 'x0': 0.417, 'x1': 0.584},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.55, 'y1': 0.725, 'x0': 0.624, 'x1': 0.792},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.55, 'y1': 0.725, 'x0': 0.832, 'x1': 1},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.275, 'y1': 0.451, 'x0': 0, 'x1': 0.168},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.275, 'y1': 0.451, 'x0': 0.208, 'x1': 0.376},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.275, 'y1': 0.451, 'x0': 0.417, 'x1': 0.584},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.275, 'y1': 0.451, 'x0': 0.624, 'x1': 0.792},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.275, 'y1': 0.451, 'x0': 0.832, 'x1': 1},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0, 'y1': 0.175, 'x0': 0, 'x1': 0.168},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0, 'y1': 0.175, 'x0': 0.208, 'x1': 0.376},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0, 'y1': 0.175, 'x0': 0.417, 'x1': 0.584},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0, 'y1': 0.175, 'x0': 0.624, 'x1': 0.792},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0, 'y1': 0.175, 'x0': 0.832, 'x1': 1}   
            ]  
    session_decisions = []
    for i in range(5):
        decision_text_sessions = "Agent Seeking: " + str(count_seeking[i]) + " | Agent Avoiding: " + str(count_avoiding[i]) + "<br><br>"
        session_decisions.append(decision_text_sessions)
    
    fig = make_subplots(
        rows=4, 
        cols=5, 
        subplot_titles=(session_decisions[0] + "Agent at Chosen Direction: <br>" + "Session 1:" ,  session_decisions[1] + "<br>Session 2: ", 
            session_decisions[2]+"<br>Session 3", session_decisions[3] +"<br>Session 4",  session_decisions[4]+"<br>Session 5",
                        "Agent at not Chosen Direction <br>Session 1", "Session 2", "Session 3", "Session 4", "Session 5",
                        "Agent at both Directions <br>Session 1", "Session 2", "Session 3", "Session 4", "Session 5",
                        "No Agent at both Directions <br>Session 1", "Session 2", "Session 3", "Session 4", "Session 5"), 
        x_title="Number of previous visits not chosen nodes", 
        y_title="Number of previous visits chosen node",
        vertical_spacing = 0.1
        )
        #row_titles = ('Sessions Combined', 'Sessions Seperated')
    fig.update_layout(margin=dict(t=200))
    for i in range(4):
        for session in sessions:
            #session_decisions = "Agent Seeking: " + str(count_seeking[session-1]) + " | Agent Avoiding: " + str(count_avoiding[session-1])
            if len(matrix[i][session-1]) > 0:
                count_cons, count_expl, count_total = getStrategyCounts(matrix[i][session-1])
                perc_cons = round((count_cons/count_total), 2)
                perc_expl = round((count_expl/count_total),2)
                #filename = "Strategy_Matrix_" + str(participant) + "_Session_" + str(session) + ".png"
                matrix_text = np.array(np.array(matrix[i][session-1],dtype='int'),dtype='str')
                matrix_text[matrix_text == '0'] = ""
                colorscale = "Sunset"
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
                    xref = 'x domain', yref = 'y domain', #'paper',
                    align="left",#valign = "top", 
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


#def plotAndSafeStratMatrix(matrix_total, matrix_sessions,count_seeking, count_avoiding, participant = None, sessions = (1,2,3,4,5)):
#    save_path = "E:/HumanA/Analysis/StrategyMatrices/"
#    if experiment == 1:
#        save_path = save_path + "Exp1/Dec_Expl_Matrix/"
#    elif experiment == 2:
#        save_path = save_path + "Exp2/Dec_Expl_Matrix/"
#    
#    #if dataSet == 1:
#    #    save_path = save_path + "FullDataSet/Dec_Expl_Matrix/"
#    #elif dataSet == 2:
#    #    save_path = save_path + "ConsDataSet/Dec_Expl_Matrix/"
#    
#    for i in range(3):
#        if i == 0:
#            condition = 'AvatarAtChosen'
#        elif i == 1:
#            condition = 'AvatarAtNotChosen'
#        else:
#            condition = 'AvatarAtBoth'
#        if participant != None:
#            filename = str(participant) + "_Strategy_Matrix_" + condition + "_" + ".png"
#        else:
#            filename = "Total" + "_Strategy_Matrix_" + condition + "_" + ".png"
#            participant = 'All participants'
#
#        total_decisions = "Total Decisions Avatar Seeking: " + str(count_seeking) + " | Total Decisions Avatar Avoiding: " + str(count_avoiding)
#        title = "Participant " + str(participant) + ": " + condition + "<br>" + total_decisions
#
#        line = { 'color': 'red', 'width': 1 }
#        diagonal_lines = [
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 }, 'yref': 'paper', 'xref': 'paper', 'y0': 0.626, 'y1': 1, 'x0': 0, 'x1': 0.168},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.626, 'y1': 1, 'x0': 0.208, 'x1': 0.376},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.626, 'y1': 1, 'x0': 0.417, 'x1': 0.584},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.626, 'y1': 1, 'x0': 0.624, 'x1': 0.792},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.626, 'y1': 1, 'x0': 0.832, 'x1': 1},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 }, 'yref': 'paper', 'xref': 'paper', 'y0': 0, 'y1': 0.374, 'x0': 0, 'x1': 0.168},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0, 'y1': 0.374, 'x0': 0.208, 'x1': 0.376},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0, 'y1': 0.374, 'x0': 0.417, 'x1': 0.584},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0, 'y1': 0.374, 'x0': 0.624, 'x1': 0.792},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0, 'y1': 0.374, 'x0': 0.832, 'x1': 1} 
#                ]  
#
#        fig = make_subplots(
#            rows=2, 
#            cols=5, 
#            subplot_titles=("session 1", "session 2", "session 3", "session 4", "session 5",
#                            "session 1", "session 2", "session 3", "session 4", "session 5"), 
#            x_title="Number of previous avoiding decisions", 
#            y_title="Number of previous seeking decisions",
#            #row_titles = ('Sessions Combined', 'Sessions Seperated')
#        )
#
#        for session in sessions:
#            if len(matrix_total[i][session-1]) > 0:
#                #filename = "Strategy_Matrix_" + str(participant) + "_Session_" + str(session) + ".png"
#                matrix_text = np.array(np.array(matrix_total[i][session-1],dtype='int'),dtype='str')
#                matrix_text[matrix_text == '0'] = ""
#                colorscale = "Sunset"
#                fig.add_trace(go.Heatmap(z=matrix_total[i][session-1], text=matrix_text, texttemplate="%{text}", textfont={"size":10}, colorscale = colorscale,), 
#                    row=1, col=session)
#                fig.update_traces(showscale=False)
#                fig.update_layout(
#                  title_text=title,
#                  boxmode='group',
#                  width=2000,
#                  height=1000,
#                  shapes=diagonal_lines
#                )
#            if len(matrix_sessions[i][session-1]) > 0:
#                #filename = "Strategy_Matrix_" + str(participant) + "_Session_" + str(session) + ".png"
#                matrix_text = np.array(np.array(matrix_sessions[i][session-1],dtype='int'),dtype='str')
#                matrix_text[matrix_text == '0'] = ""
#                colorscale = "Sunset"
#                fig.add_trace(go.Heatmap(z=matrix_sessions[i][session-1], text=matrix_text, texttemplate="%{text}", textfont={"size":10}, colorscale = colorscale), 
#                    row=2, col=session)
#                fig.update_traces(showscale=False)
#                fig.update_layout(
#                  #title_text=title,
#                  boxmode='group',
#                  width=2000,
#                  height=1000,
#                  shapes=diagonal_lines
#                )
#        
#        fig.write_image((save_path + filename))


def addVisitToStrategyMatrix(node,last_node,decisions):
    visits_cur_node_part_total,visits_cur_node_part_ses, _,_= getVisits(node)


    for _,neighbour,decision in decisions:
        visits_neighbour_part_total,visits_neighbour_part_ses, _,_= getVisits(neighbour)
        if decision == 'AvatarAtChosen':
            strategy_matrix_current_total[0][visits_cur_node_part_total][visits_neighbour_part_total] += 1
            strategy_matrix_current_Session[0][visits_cur_node_part_ses][visits_neighbour_part_ses] += 1
            #addTotalCountStrategy(visits_cur_node_part_total, visits_neighbour_part_total)
        elif decision == 'AvatarAtNotChosen':
            strategy_matrix_current_total[1][visits_cur_node_part_total][visits_neighbour_part_total] += 1
            strategy_matrix_current_Session[1][visits_cur_node_part_ses][visits_neighbour_part_ses] += 1
        elif decision == 'AvatarAtBoth':
            strategy_matrix_current_total[2][visits_cur_node_part_total][visits_neighbour_part_total] += 1
            strategy_matrix_current_Session[2][visits_cur_node_part_ses][visits_neighbour_part_ses] += 1
        else: 
            strategy_matrix_current_total[3][visits_cur_node_part_total][visits_neighbour_part_total] += 1
            strategy_matrix_current_Session[3][visits_cur_node_part_ses][visits_neighbour_part_ses] += 1

#def addTotalCountStrategy(visits_node_total, visits_neighbour_total,visits_node_ses, visits_neighbour_ses, index):
#    if visits_node_total > visits_neighbour_total:
#        strategy_count_expl_part_total[index] += 1
#    elif visits_node_total < visits_neighbour_total:
#        strategy_count_cons[index] += 1


def adjustVisits(node):
    visits_node_participant_total[node] += 1
    visits_node_participant_currentSes[node] += 1

    #for visit in visits_neighbours_total:
    #    if decisions[1] == 
    #    strategy_matrix_current_total[visits_current_node_total][visit] += 1
    #
    #for visit in visits_neighbours_session:
    #    strategy_matrix_current_sess[visits_current_node_session][visit] += 1


def resizeStrategyMatrixes():
    global max_visits_total_participant
    global max_visits_session_participant
    global max_visits_total
    global max_visits_sessions
    global strategy_matrix_current_total
    #global strategy_matrix_current_total[1]
    #global strategy_matrix_current_total[2]
    global strategy_matrix_current_Session
    #global strategy_matrix_current_Session[1]
    #global strategy_matrix_current_Session[2]

    global strategy_matrix_total
    #global strategy_matrix_total[1]
    #global strategy_matrix_total[2]
    global strategy_matrix_perSession
    #global strategy_matrix_perSession[1]
    #global strategy_matrix_perSession[2]


    if max_visits_total_participant < max(visits_node_participant_total)+1 or (len(strategy_matrix_current_total[0]) == 0 
        or len(strategy_matrix_current_total[1]) == 0 or len(strategy_matrix_current_total[2]) == 0 or len(strategy_matrix_current_total[3]) == 0 ):
        max_visits_total_participant = max(visits_node_participant_total)+1
        for i in range(len(strategy_matrix_current_total)):
            strategy_matrix_current_total[i] = resize_matrix(strategy_matrix_current_total[i], max_visits_total_participant+1)
        #strategy_matrix_current_total[0] = resize_matrix(strategy_matrix_current_total[0], max_visits_total_participant+1)
        #strategy_matrix_current_total[1] = resize_matrix(strategy_matrix_current_total[1], max_visits_total_participant+1)
        #strategy_matrix_current_total[2] = resize_matrix(strategy_matrix_current_total[2], max_visits_total_participant+1)
        #strategy_matrix_current_total[3] = resize_matrix(strategy_matrix_current_total[3], max_visits_total_participant+1)

    if max_visits_session_participant < max(visits_node_participant_currentSes)+1 or (len(strategy_matrix_current_Session[0]) == 0 
        or len(strategy_matrix_current_Session[1]) == 0 or len(strategy_matrix_current_Session[2]) == 0 or len(strategy_matrix_current_Session[3]) == 0 ):
        max_visits_session_participant = max(visits_node_participant_currentSes)+1
        for i in range(len(strategy_matrix_current_Session)):
            strategy_matrix_current_Session[i] = resize_matrix(strategy_matrix_current_Session[i], max_visits_session_participant+1)

        #strategy_matrix_current_Session[0] = resize_matrix(strategy_matrix_current_Session[0], max_visits_session_participant+1)
        #strategy_matrix_current_Session[1] = resize_matrix(strategy_matrix_current_Session[1], max_visits_session_participant+1)
        #strategy_matrix_current_Session[2] =resize_matrix(strategy_matrix_current_Session[2], max_visits_session_participant+1)
        #strategy_matrix_current_Session[3] =resize_matrix(strategy_matrix_current_Session[3], max_visits_session_participant+1)

    if max_visits_total <= max_visits_total_participant or (len(strategy_matrix_total[0][session-1]) <= max_visits_total or 
        len(strategy_matrix_total[1][session-1]) <= max_visits_total or len(strategy_matrix_total[2][session-1]) <= max_visits_total or len(strategy_matrix_total[3][session-1]) <= max_visits_total):
        if max_visits_total <= max_visits_total_participant:
            max_visits_total = max_visits_total_participant+1
        
        for i in range(len(strategy_matrix_total)):
            strategy_matrix_total[i][session-1]  = resize_matrix(strategy_matrix_total[i][session-1] , max_visits_total+1)
        #strategy_matrix_total[0][session-1]  = resize_matrix(strategy_matrix_total[0][session-1] , max_visits_total+1)
        #strategy_matrix_total[1][session-1]  = resize_matrix(strategy_matrix_total[1][session-1] , max_visits_total+1)
        #strategy_matrix_total[2][session-1]  = resize_matrix(strategy_matrix_total[2][session-1] , max_visits_total+1)
        #strategy_matrix_total[3][session-1]  = resize_matrix(strategy_matrix_total[2][session-1] , max_visits_total+1)


    if max_visits_sessions <= max_visits_session_participant or (len(strategy_matrix_perSession[0][session-1]) <= max_visits_sessions or
        len(strategy_matrix_perSession[1][session-1]) <= max_visits_sessions or len(strategy_matrix_perSession[2][session-1]) <= max_visits_sessions or len(strategy_matrix_perSession[3][session-1]) <= max_visits_sessions):
        if max_visits_sessions <= max_visits_session_participant:
            max_visits_sessions = max_visits_session_participant+1
        for i in range(len(strategy_matrix_perSession)):
            strategy_matrix_perSession[i][session-1]  = resize_matrix(strategy_matrix_perSession[i][session-1] , max_visits_sessions+1)
        #strategy_matrix_perSession[0][session-1]  = resize_matrix(strategy_matrix_perSession[0][session-1] , max_visits_sessions+1)
        #strategy_matrix_perSession[1][session-1]  = resize_matrix(strategy_matrix_perSession[1][session-1] , max_visits_sessions+1)
        #strategy_matrix_perSession[2][session-1]  = resize_matrix(strategy_matrix_perSession[2][session-1] , max_visits_sessions+1)
        #strategy_matrix_perSession[3][session-1]  = resize_matrix(strategy_matrix_perSession[2][session-1] , max_visits_sessions+1)
       

participants = getParticipants(cr)
max_node = getMaxNodeFromDB(cr)
count_dec_seeking_total, count_dec_avoiding_total = getCountDecisionsTotal()
count_dec_seeking_total_ses, count_dec_avoiding_total_ses = getCountDecisionsSessionTotal()
strategy_matrix_total = [[np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))],
                        [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))],
                        [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))],
                        [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]]
#strategy_matrix_total[1] = [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]
#strategy_matrix_total[2] = [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]

strategy_matrix_perSession = [[np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))],
                        [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))],
                        [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))],
                        [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]]
#strategy_matrix_perSession[1] = [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]
#strategy_matrix_perSession[2] = [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]


max_visits_total = 0
max_visits_sessions = 0
visits_node_total = [0]*(max_node + 1)
visits_node_perSession = [0]*(max_node + 1)
#strategy_count_cons_total = 3*[0]
#strategy_count_expl_total = 3*[0]
#strategy_count_cons_perSes = 3*[0]
#strategy_count_expl_perSes = 3*[0]

for participant in participants:
    visits_node_participant_total = [0]*(max_node + 1)

    strategy_matrix_participant_total = [[np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))],
                                        [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))],
                                        [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))],
                                        [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]]
    #strategy_matrix_participant_total[1] = [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]
    #strategy_matrix_participant_total[2] = [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]

    strategy_matrix_participant_perSession = [[np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))],
                                        [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))],
                                        [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))],
                                        [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]]
    #strategy_matrix_participant_perSession[1] = [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]
    #strategy_matrix_participant_perSession[2] = [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]
    
    sessions = getSessions(participant, cr)
    last_session = 0

    last_node = []
    max_visits_total_participant = 0
    
    count_dec_seeking_part = 0
    count_dec_avoiding_part = 0
    count_dec_seeking_ses = 5*[0]
    count_dec_avoiding_ses = 5*[0]

    #strategy_count_cons_part_total = 3*[0]
    #strategy_count_expl_part_total = 3*[0]

    for session in sessions:
        print("Participant: " + str(participant) + " | Session: " + str(session))
        visits_node_participant_currentSes = [0]*(max_node + 1)
        #strategy_count_cons_part_perSes = 3*[0]
        #strategy_count_expl_part_perSes = 3*[0]
        #strategy_matrix_current_total[1] = np.zeros((0,0))
        #strategy_matrix_current_total[2] = np.zeros((0,0))
        strategy_matrix_current_total = [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]
        strategy_matrix_current_Session = [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]
        #strategy_matrix_current_Session[1] = np.zeros((0,0))
        #strategy_matrix_current_Session[2] = np.zeros((0,0))
        
        #if dataSet == 2:
        #    if session != (last_session + 1):
        #        print("Session missing")
        #        continue
        
        max_visits_session_participant = 0
        trials = getTrialNrs(participant, session, cr)

        if len(trials) < 3:
            print("Missing trials for this session")
            continue

        data = getDatapoints(trials, cr)
        dp_ids_total = tuple([datapoint[1] for datapoint in data])
        count_dec_seeking,count_dec_avoiding = getCountDecisions(dp_ids_total)
        count_dec_seeking_ses[session-1] = count_dec_seeking
        count_dec_avoiding_ses[session-1] = count_dec_avoiding
        #count_dec_avoiding_ses.append(count_dec_avoiding)
        count_dec_seeking_part += count_dec_seeking
        count_dec_avoiding_part += count_dec_avoiding



        #last_trial_id = None
        for datapoint in data:
            trial_id, dp_id,timeStamp, node = datapoint
            #if dp_id == 2554141:
            #    print("")

            #if trial_id != last_trial_id and last_node != [] and last_node != node:
                #print("not the same node as in the previous session")
            if last_node != []:
                decisions = getDecisions(dp_id, cr)
                #lastNode_neighbours = [decision[1] for decision in decisions]
                #if decisions != []:

                resizeStrategyMatrixes()
                #visits_current_node_total, visits_neighbours_total = getTotalVisitsNodes(node, lastNode_neighbours)
                #visits_current_node_session, visits_neighbours_session = getSessionVisitsNodes(node, lastNode_neighbours)

                addVisitToStrategyMatrix(node,last_node,decisions)
                adjustVisits(node)
                #for visit in visits_neighbours_total:
                #    strategy_matrix_current_total[visits_current_node_total][visit] += 1
                #
                #for visit in visits_neighbours_session:
                #    strategy_matrix_current_sess[visits_current_node_session][visit] += 1

                # add visit to the visits count of the current node
                #visits_node_total[node] += 1
                #visits_node_currentSes[node] += 1

                    #getTotalVisitsNodes()
                    #getSessionVisitsNodes()

                    #dec_seeking_total,dec_avoiding_total = getNodeDecisionsTotal(last_node)
                    #dec_seeking_ses,dec_avoiding_ses = getNodeDecisionsSession(last_node)

            #strategy_matrix_current_sess[dec_seeking_ses][dec_avoiding_ses] += 1
            #strategy_matrix_current_total[dec_seeking_total][dec_avoiding_total] += 1

            #if last_node != []:

            last_node = node
        
        strategy_matrix_participant_total[0][session-1] = strategy_matrix_current_total[0] 
        strategy_matrix_participant_total[1][session-1] = strategy_matrix_current_total[1] 
        strategy_matrix_participant_total[2][session-1] = strategy_matrix_current_total[2]
        strategy_matrix_participant_total[3][session-1] = strategy_matrix_current_total[3] 

        strategy_matrix_participant_perSession[0][session-1] = strategy_matrix_current_Session[0]
        strategy_matrix_participant_perSession[1][session-1]  = strategy_matrix_current_Session[1]
        strategy_matrix_participant_perSession[2][session-1]  = strategy_matrix_current_Session[2]
        strategy_matrix_participant_perSession[3][session-1]  = strategy_matrix_current_Session[3]
        #strategy_matrix_participant_total[session-1] = strategy_matrix_current_total
        #strategy_matrix_participant_perSession[session-1] = strategy_matrix_current_sess

        strategy_matrix_total[0][session-1] = addUpMatrices(strategy_matrix_total[0][session-1], strategy_matrix_current_total[0]) 
        strategy_matrix_total[1][session-1] = addUpMatrices(strategy_matrix_total[1][session-1], strategy_matrix_current_total[1]) 
        strategy_matrix_total[2][session-1] = addUpMatrices(strategy_matrix_total[2][session-1], strategy_matrix_current_total[2]) 
        strategy_matrix_total[3][session-1] = addUpMatrices(strategy_matrix_total[3][session-1], strategy_matrix_current_total[3]) 

        strategy_matrix_perSession[0][session-1] = addUpMatrices(strategy_matrix_perSession[0][session-1], strategy_matrix_current_Session[0]) 
        strategy_matrix_perSession[1][session-1] = addUpMatrices(strategy_matrix_perSession[1][session-1], strategy_matrix_current_Session[1]) 
        strategy_matrix_perSession[2][session-1] = addUpMatrices(strategy_matrix_perSession[2][session-1], strategy_matrix_current_Session[2]) 
        strategy_matrix_perSession[3][session-1] = addUpMatrices(strategy_matrix_perSession[3][session-1], strategy_matrix_current_Session[3]) 
        #strategy_matrix_total[session-1] =  addUpMatrices(strategy_matrix_total[session-1], strategy_matrix_participant_total[0])
        #strategy_matrix_total_sessions[session-1] = addUpMatrices(strategy_matrix_total_sessions[session-1], strategy_matrix_participant_perSession[0])
        
        last_session = session
        print("All visits counted")
    plotTotal(strategy_matrix_participant_total,count_dec_seeking_part,count_dec_avoiding_part,participant,sessions)
    plotSession(strategy_matrix_participant_perSession,count_dec_seeking_ses,count_dec_avoiding_ses,participant,sessions )
    #plotAndSafeStratMatrix(strategy_matrix_participant_total,strategy_matrix_participant_perSession, count_dec_seeking_part,count_dec_avoiding_part,participant,sessions)

plotTotal(strategy_matrix_total,count_dec_seeking_total,count_dec_avoiding_total)
plotSession(strategy_matrix_perSession,count_dec_seeking_total_ses,count_dec_avoiding_total_ses)
#plotAndSafeStratMatrix(strategy_matrix_total,strategy_matrix_perSession,count_dec_seeking_total,count_dec_avoiding_total)
print("All done")
connection.close()