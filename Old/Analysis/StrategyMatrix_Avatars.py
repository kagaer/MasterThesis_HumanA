import sqlite3
from pathlib import Path
from typing import List, Tuple, Union
import numpy as np
import seaborn as sns
import matplotlib.pylab as plt
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import enum
from MultipleUseFunctions import *

# path to databases
print("For which experiment would you like to reduce the data?")
experiment = int(input())
if experiment == 1:
    db_path = Path('E:/HumanA/Data/Database/HumanA_Exp1.db')

elif experiment == 2:
    db_path = Path('E:/HumanA/Data/Database/HumanA_Exp2.db')


# check if path exists
if not db_path or not db_path.exists():
    db_path = ':memory:'


print("Single Decison Count (1) or multiple Decision Count (2)?")
decCount = int(input())
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


def getParticipants():
    """get all participantIds from the database

    Returns:
        tuple: list of participants
    """
    # select all participantIds and return them
    sql_instruction = """
    SELECT DISTINCT participantId FROM trials WHERE validParticipant = 'VALID';
    """
    cr.execute(sql_instruction)
    participants = tuple(did[0] for did in cr.fetchall())
    return participants

def getSessions(participant):
    """get all sessionNrs for the current participant from the database

    Returns:
        tuple: list of participants
    """
    # select all participantIds and return them
    sql_instruction = f"""
    SELECT DISTINCT sessionNr FROM trials WHERE participantId = {participant} AND validSession = 'VALID'
    ORDER BY sessionNr;
    """
    cr.execute(sql_instruction)
    sessions = tuple(did[0] for did in cr.fetchall())
    return sessions

def getTrialNrs(participant, session):
    """get all trialIds for the current participant, current session

    Args:
        participant (int): current participant

    Returns:
        tuple: all trialIds 
    """

    sql_instruction = f"""
    SELECT DISTINCT id 
    FROM trials
    WHERE participantId = {participant} AND sessionNr = {session}
    """
    
    cr.execute(sql_instruction)
    trialIdx = tuple(did[0] for did in cr.fetchall())
    return trialIdx

def getDatapoints(trials):
    """get all datapoints for the current trial, sorted by the timestamp (timeStampDataPointStart), and joined with the trialId and participantId

    Args:
        trial (int): current trial

    Returns:
        list: all datapoints for this trial 
    """

    sql_instruction = f"""
    SELECT dataPoints_analysis.trialId, dataPoints_analysis.DatapointId, dataPoints_analysis.timeStampDataPointStart, dataPoints_analysis.node
    FROM dataPoints_analysis
    WHERE dataPoints_analysis.trialId IN {trials}
    ORDER BY dataPoints_analysis.timeStampDataPointStart ASC
    ;
        """
    cr.execute(sql_instruction)
    data = cr.fetchall()
    return data

def getDecisions(dp_id):
    sql_instruction = f"""
    SELECT participant_decision.Id, participant_decision.last_node_neighbour, participant_decision.decision
    FROM participant_decision
    WHERE participant_decision.datapointId = {dp_id} AND (participant_decision.decision = 'AvatarAtChosen' 
        OR participant_decision.decision = 'AvatarAtNotChosen')
    ;
        """
    cr.execute(sql_instruction)
    decisions = cr.fetchall()
    return decisions

def getMaxNodeFromDB():
    """get the max node from the database

    Returns:
        max_node (int): max node
    """

    sql_instruction = f"""
    SELECT MAX(nodeNr) FROM graph_coordinates
    """
    
    cr.execute(sql_instruction)
    max_node = cr.fetchone()
    return max_node[0]

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

def resize_matrix(matrix, shape):
    # resize the current strategy matrix, fill up, so that it matches the new shape
    shape_diff = np.array(shape) - np.array(matrix.shape)
    return np.lib.pad(matrix, ((0,shape_diff[0]),(0,shape_diff[1])), 'constant', constant_values=(0))

def addDecisionsToNode(last_node, decisions):
    if decCount == 1:
        avatarAtChosen = False
        avatarAtNotChosen = False
        for decision in decisions:
            if decision[2] == 'AvatarAtChosen':
                avatarAtChosen = True

            elif decision[2] == 'AvatarAtNotChosen':
                avatarAtNotChosen = True

        if avatarAtChosen:
            decisions_node_seeking_total[last_node] += 1
            decisions_node_seeking_currentSes[last_node] += 1
        if avatarAtNotChosen:
            decisions_node_avoiding_total[last_node] += 1
            decisions_node_avoiding_currentSes[last_node] += 1

    elif decCount == 2:
        for decision in decisions:
            if decision[2] == 'AvatarAtChosen':
                decisions_node_seeking_total[last_node] += 1
                decisions_node_seeking_currentSes[last_node] += 1
            elif decision[2] == 'AvatarAtNotChosen':
                decisions_node_avoiding_total[last_node] += 1
                decisions_node_avoiding_currentSes[last_node] += 1



def getNodeDecisionsTotal(node):
    decisions_seeking = decisions_node_seeking_total[node] 
    decisions_avoiding = decisions_node_avoiding_total[node]
    return decisions_seeking, decisions_avoiding

def getNodeDecisionsSession(node):
    decisions_seeking = decisions_node_seeking_currentSes[node] 
    decisions_avoiding = decisions_node_avoiding_currentSes[node]
    return decisions_seeking, decisions_avoiding


def addUpMatrices(matrix1, matrix2):
# iterate through rows
    result = matrix1
    for i in range(len(matrix2)):  
    # iterate through columns
        for j in range(len(matrix2[0])):
            result[i][j] = matrix1[i][j] + matrix2[i][j]
    
    return result






def plotAndSafeStratMatrix(matrix_total,matrix_sessions,count_seeking, count_avoiding, participant = None, sessions = (1,2,3,4,5)):
    save_path = "E:/HumanA/Analysis/StrategyMatrices/"
    if experiment == 1:
        save_path = save_path + "Exp1/Decision_Matrix/"
    elif experiment == 2:
        save_path = save_path + "Exp2/Decision_Matrix/"
    
    if decCount == 1:
        save_path = save_path + 'SingleDec/'
    elif decCount == 2:
        save_path = save_path + 'MultDec/'

    if participant != None:
        filename = "Decision_Matrix_Avatars_" + str(participant) + ".png"
    else:
        filename = "Decision_Matrix_Avatars_Total" + ".png"

    total_decisions = "Total Decisions Avatar Seeking: " + str(count_seeking) + " | Total Decisions Avatar Avoiding: " + str(count_avoiding)
    title = "Participant " + str(participant) + ": " + "<br>" + total_decisions

    line = { 'color': 'red', 'width': 1 }
    diagonal_lines = [
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 }, 'yref': 'paper', 'xref': 'paper', 'y0': 0.626, 'y1': 1, 'x0': 0, 'x1': 0.168},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.626, 'y1': 1, 'x0': 0.208, 'x1': 0.376},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.626, 'y1': 1, 'x0': 0.417, 'x1': 0.584},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.626, 'y1': 1, 'x0': 0.624, 'x1': 0.792},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.626, 'y1': 1, 'x0': 0.832, 'x1': 1},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 }, 'yref': 'paper', 'xref': 'paper', 'y0': 0, 'y1': 0.374, 'x0': 0, 'x1': 0.168},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0, 'y1': 0.374, 'x0': 0.208, 'x1': 0.376},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0, 'y1': 0.374, 'x0': 0.417, 'x1': 0.584},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0, 'y1': 0.374, 'x0': 0.624, 'x1': 0.792},
        {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0, 'y1': 0.374, 'x0': 0.832, 'x1': 1} 
            ]  

    fig = make_subplots(
        rows=2, 
        cols=5, 
        subplot_titles=("session 1", "session 2", "session 3", "session 4", "session 5",
                        "session 1", "session 2", "session 3", "session 4", "session 5"), 
        x_title="Current number of avoiding decisions", 
        y_title="Current number of seeking decisions"
    )

    for session in sessions:
        if len(matrix_total[session-1]) > 0:
            count_seeking, count_avoiding, count_total = getStrategyCounts(matrix_total[session-1])
            perc_seek = round((count_seeking/count_total), 2)
            perc_avoid = round((count_avoiding/count_total),2)
            matrix_text = np.array(np.array(matrix_total[session-1],dtype='int'),dtype='str')
            matrix_text[matrix_text == '0'] = ""
            colorscale = "Sunset"
            fig.add_trace(go.Heatmap(z=matrix_total[session-1], text=matrix_text, texttemplate="%{text}", textfont={"size":10}, colorscale = colorscale,), 
                row=1, col=session)
            fig.update_traces(showscale=False)
            fig.update_layout(
              title_text=title,
              boxmode='group',
              width=2000,
              height=1000,
              shapes=diagonal_lines)
            fig.add_annotation(text = "Seeking: " + str(count_seeking) + " " + "(" + str(perc_seek) + ")" +
                        "<br>Avoiding: " + str(count_avoiding) + " " + "(" + str(perc_avoid) + ")",
                    showarrow=False,
                    bordercolor='black',
                    borderwidth=1,
                    x = 0, y = 1,
                    xanchor= 'left', yanchor='top',
                    xref = 'x domain', yref = 'y domain',
                    align="left",
                    name="Strategy Counts", row=1, col = session)
            
        if len(matrix_sessions[session-1]) > 0:
            count_seeking, count_avoiding, count_total = getStrategyCounts(matrix_sessions[session-1])
            perc_seek = round((count_seeking/count_total), 2)
            perc_avoid = round((count_avoiding/count_total),2)
            matrix_text = np.array(np.array(matrix_sessions[session-1],dtype='int'),dtype='str')
            matrix_text[matrix_text == '0'] = ""
            colorscale = "Sunset"
            fig.add_trace(go.Heatmap(z=matrix_sessions[session-1], text=matrix_text, texttemplate="%{text}", textfont={"size":10}, colorscale = colorscale,), 
                row=2, col=session)
            fig.update_traces(showscale=False)
            fig.update_layout(

              boxmode='group',
              width=2000,
              height=1000,
              shapes=diagonal_lines
            )
            fig.add_annotation(text = "Seeking: " + str(count_seeking) + " " + "(" + str(perc_seek) + ")" +
                        "<br>Avoiding: " + str(count_avoiding) + " " + "(" + str(perc_avoid) + ")",
                    showarrow=False,
                    bordercolor='black',
                    borderwidth=1,
                    x = 0, y = 1,
                    xanchor= 'left', yanchor='top',
                    xref = 'x domain', yref = 'y domain',
                    align="left", 
                    name="Strategy Counts", row=2, col = session)

    fig.write_image((save_path + filename))



participants = getParticipants()
max_node = getMaxNodeFromDB()

strategy_matrix_total = [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]
strategy_matrix_total_sessions = [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]
max_decisions_total = 0
max_decisions_sessions = 0

count_dec_seeking_total, count_dec_avoiding_total = getCountDecisionsTotal()

for participant in participants:
    decisions_node_seeking_total = [0]*(max_node + 1)
    decisions_node_avoiding_total = [0]*(max_node + 1)

    strategy_matrix_participant_total = [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]
    strategy_matrix_participant_perSession = [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]
    sessions = getSessions(participant)
    last_session = 0

    last_node = []

    count_dec_avoiding_part = 0
    count_dec_seeking_part = 0

    max_decisions_total_participant = 0
    for session in sessions:
        print("Participant: " + str(participant) + " | Session: " + str(session))
        decisions_node_seeking_currentSes = [0]*(max_node + 1)
        decisions_node_avoiding_currentSes = [0]*(max_node + 1)

        strategy_matrix_current_total = np.zeros((0,0))

        strategy_matrix_current_sess = np.zeros((0,0))

        
        max_decisions_session_participant = 0
        trials = getTrialNrs(participant, session)
        if len(trials) < 3:
            print("Missing trials for this session")
            continue
        data = getDatapoints(trials)
        dp_ids_total = tuple([datapoint[1] for datapoint in data])
        count_dec_seeking_ses,count_dec_avoiding_ses = getCountDecisions(dp_ids_total)
        count_dec_seeking_part += count_dec_seeking_ses
        count_dec_avoiding_part += count_dec_avoiding_ses

        for datapoint in data:
            trial_id, dp_id,timeStamp, node = datapoint

            if last_node != []:
                decisions = getDecisions(dp_id)
                if decisions != []:
                    addDecisionsToNode(last_node,decisions)

                    if max_decisions_total_participant < max((max(decisions_node_seeking_total)+1),(max(decisions_node_avoiding_total)+1))or len(strategy_matrix_current_total) == 0:
                        max_decisions_total_participant = max((max(decisions_node_seeking_total)+1),(max(decisions_node_avoiding_total)+1))
                        strategy_matrix_current_total = resize_matrix(strategy_matrix_current_total, max_decisions_total_participant+1)

                    if max_decisions_session_participant < max((max(decisions_node_seeking_currentSes)+1),(max(decisions_node_avoiding_currentSes)+1)):
                        max_decisions_session_participant = max((max(decisions_node_seeking_currentSes)+1),(max(decisions_node_avoiding_currentSes)+1))
                        strategy_matrix_current_sess = resize_matrix(strategy_matrix_current_sess, max_decisions_session_participant+1)

                    if max_decisions_total <= max_decisions_total_participant or len(strategy_matrix_total[session-1]) <= max_decisions_total:
                        if max_decisions_total <= max_decisions_total_participant:
                            max_decisions_total = max_decisions_total_participant+1
                        strategy_matrix_total[session-1]  = resize_matrix(strategy_matrix_total[session-1] , max_decisions_total+1)

                    if max_decisions_sessions <= max_decisions_session_participant or len(strategy_matrix_total_sessions[session-1]) <= max_decisions_sessions:
                        if max_decisions_sessions <= max_decisions_session_participant:
                            max_decisions_sessions = max_decisions_session_participant+1
                        strategy_matrix_total_sessions[session-1]  = resize_matrix(strategy_matrix_total_sessions[session-1] , max_decisions_sessions+1)

                    dec_seeking_total,dec_avoiding_total = getNodeDecisionsTotal(last_node)
                    dec_seeking_ses,dec_avoiding_ses = getNodeDecisionsSession(last_node)

                    strategy_matrix_current_sess[dec_seeking_ses][dec_avoiding_ses] += 1
                    strategy_matrix_current_total[dec_seeking_total][dec_avoiding_total] += 1

            last_node = node
        strategy_matrix_participant_total[session-1] = strategy_matrix_current_total
        strategy_matrix_participant_perSession[session-1] = strategy_matrix_current_sess

        strategy_matrix_total[session-1] =  addUpMatrices(strategy_matrix_total[session-1], strategy_matrix_current_total)
        strategy_matrix_total_sessions[session-1] = addUpMatrices(strategy_matrix_total_sessions[session-1], strategy_matrix_current_sess)
        
        last_session = session
        print("All visits counted")
    plotAndSafeStratMatrix(strategy_matrix_participant_total,strategy_matrix_participant_perSession,count_dec_seeking_part,count_dec_avoiding_part,participant,sessions)

plotAndSafeStratMatrix(strategy_matrix_total,strategy_matrix_total_sessions, count_dec_seeking_total, count_dec_avoiding_total)
print("All done")