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
    #db_path = Path('E:/HumanA/Data/HumanA_Exp1_WorkingData.db')
elif experiment == 2:
    db_path = Path('E:/HumanA/Data/Database/HumanA_Exp2.db')
    #db_path = Path('E:/HumanA/Data/HumanA_Exp2_WorkingData.db')

# check if path exists
if not db_path or not db_path.exists():
    db_path = ':memory:'

#print("Full Dataset (1) or only consecutive Data (2)?")
#dataSet = int(input())

# connect to database
connection=sqlite3.connect(db_path)
cr=connection.cursor()

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
    #maxNode = tuple(did[0] for did in cr.fetchall())
    return max_node[0]

def resize_matrix(matrix, shape):
    # resize the current strategy matrix, fill up, so that it matches the new shape
    shape_diff = np.array(shape) - np.array(matrix.shape)
    return np.lib.pad(matrix, ((0,shape_diff[0]),(0,shape_diff[1])), 'constant', constant_values=(0))

def getNodesNeighbours(node):
    """get the neighbouring nodes of a node from the database

    Args:
        node (int): node for which the neighbours are selected

    Returns:
        neighbours (list(int)) : list of all the neighbours found
    """

    sql_instruction = f"""SELECT * FROM node_neighbours WHERE FirstNode = {node} or SecondNode = {node}"""
    cr.execute(sql_instruction)
    nodes_and_neighbours = cr.fetchall()
    neighbours = []
    for node_and_neighbour in nodes_and_neighbours:
        if node_and_neighbour[0] == node:
            neighbours.append(node_and_neighbour[1])
        elif node_and_neighbour[1] == node:
            neighbours.append(node_and_neighbour[0])
    return neighbours

def addUpMatrices(matrix1, matrix2):
# iterate through rows
    result = matrix1
    for i in range(len(matrix2)):  
    # iterate through columns
        for j in range(len(matrix2[0])):
            result[i][j] = matrix1[i][j] + matrix2[i][j]
    
    return result

#def getVisits(currentNode, avatarNotChosenDir, noAvatarNotChosenDir):
#    visits_current_node = visits_node[currentNode]
#    visits_avat_notChosen = [visits_node[node] for node in avatarNotChosenDir]
#    visits_no_avat_notChosen = [visits_node[node] for node in noAvatarNotChosenDir]
#
#    return visits_current_node, visits_avat_notChosen, visits_no_avat_notChosen

def getTotalVisitsNodes(chosenNode, neighbouringNodes):
    visits_chosenNode = visits_node_total[chosenNode]
    visits_neighbouringNodes = [visits_node_total[node] for node in neighbouringNodes]

    return visits_chosenNode, visits_neighbouringNodes

def getSessionVisitsNodes(chosenNode, neighbouringNodes):
    visits_chosenNode = visits_node_currentSes[chosenNode]
    visits_neighbouringNodes = [visits_node_currentSes[node] for node in neighbouringNodes]

    return visits_chosenNode, visits_neighbouringNodes


def plotAndSafeStratMatrix(matrix_total,matrix_sessions, participant = None, sessions = (1,2,3,4,5)):
    save_path = "E:/HumanA/Analysis/StrategyMatrices/"
    if experiment == 1:
        save_path = save_path + "Exp1/Strategy_Matrix/"
        #save_path = save_path + "Exp1/All_Sessions/Expl_Strategy/"
    elif experiment == 2:
        save_path = save_path + "Exp2/Strategy_Matrix/"
        #save_path = save_path + "Exp2/All_Sessions/Expl_Strategy/"

    #if dataSet == 1:
    #    save_path = save_path + "FullDataSet/Strategy_Matrix/"
    #elif dataSet == 2:
    #    save_path = save_path + "ConsDataSet/Strategy_Matrix/"

    if participant != None:
        filename = "Strategy_Matrix_Expl_" + str(participant) + ".png"
    else:
        filename = "Strategy_Matrix_Expl_Total" + ".png"

    #filename = "Strategy_Matrix_" + str(participant) + ".png"
    title = "Participant " + str(participant)


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
        x_title="Number of previous visits of the neighbouring nodes", 
        y_title="Number of previous visits of the chosen node"
    )

    for session in sessions:
        if len(matrix_total[session-1]) > 0:
            #filename = "Strategy_Matrix_" + str(participant) + "_Session_" + str(session) + ".png"
            count_cons, count_expl, count_total = getStrategyCounts(matrix_total[session-1])
            perc_cons = round((count_cons/count_total), 2)
            perc_expl = round((count_expl/count_total),2)
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
              shapes=diagonal_lines
            )
            fig.add_annotation(text = "Expl: " + str(count_expl) + " " + "(" + str(perc_expl) + ")"
                        "<br>Cons: " + str(count_cons) + " " + "(" + str(perc_cons) + ")",
                    showarrow=False,
                    bordercolor='black',
                    borderwidth=1,
                    x = 0, y = 1,
                    xanchor= 'left', yanchor='top',
                    xref = 'x domain', yref = 'y domain', #'paper',
                    align="left",#valign = "top", 
                    name="Strategy Counts", row=1, col = session)
        if len(matrix_sessions[session-1]) > 0:
            #filename = "Strategy_Matrix_" + str(participant) + "_Session_" + str(session) + ".png"
            count_cons, count_expl, count_total = getStrategyCounts(matrix_sessions[session-1])
            perc_cons = round((count_cons/count_total), 2)
            perc_expl = round((count_expl/count_total),2)
            matrix_text = np.array(np.array(matrix_sessions[session-1],dtype='int'),dtype='str')
            matrix_text[matrix_text == '0'] = ""
            colorscale = "Sunset"
            fig.add_trace(go.Heatmap(z=matrix_sessions[session-1], text=matrix_text, texttemplate="%{text}", textfont={"size":10}, colorscale = colorscale,), 
                row=2, col=session)
            fig.update_traces(showscale=False)
            fig.update_layout(
              #title_text=title,
              boxmode='group',
              width=2000,
              height=1000,
              shapes=diagonal_lines
            )
            fig.add_annotation(text = "Expl: " + str(count_expl) + " " + "(" + str(perc_expl) + ")"
                        "<br>Cons: " + str(count_cons) + " " + "(" + str(perc_cons) + ")",
                    showarrow=False,
                    bordercolor='black',
                    borderwidth=1,
                    x = 0, y = 1,
                    xanchor= 'left', yanchor='top',
                    xref = 'x domain', yref = 'y domain', #'paper',
                    align="left",#valign = "top", 
                    name="Strategy Counts", row=2, col = session)

    fig.write_image((save_path + filename))
            #fig = plt.figure(figsize=(24,18))
            #sns.heatmap(matrix[session-1], xticklabels=False, yticklabels=False, cmap='coolwarm', cbar=False)
            #fig.savefig((save_path + filename), transparent = True)



participants = getParticipants()
max_node = getMaxNodeFromDB()
#avatarNodes, avatarEdges = getAvatarPositions()

strategy_matrix_total = [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]
strategy_matrix_total_sessions = [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]
max_visits_total = 0
max_visits_sessions = 0

for participant in participants:
    visits_node_total = [0]*(max_node + 1)
    
    strategy_matrix_participant_total = [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]
    strategy_matrix_participant_perSession = [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]
    sessions = getSessions(participant)
    last_session = 0
    #pre_last_node = []
    last_node = []
    
    max_visits_total_participant = 0
    for session in sessions:
        print("Participant: " + str(participant) + " | Session: " + str(session))
        visits_node_currentSes = [0]*(max_node + 1)
        
        #strategy_matrix_current_total = resize_matrix(strategy_matrix_current_total, max_visits_total_participant+1)
        strategy_matrix_current_total = np.zeros((0,0))
        strategy_matrix_current_sess = np.zeros((0,0))
        #if session != (last_session + 1):
        #    print("Session missing")
        #    continue
        
        max_visits_session_participant = 0
        trials = getTrialNrs(participant, session)
        if len(trials) < 3:
            print("Missing trials for this session")
            continue
        data = getDatapoints(trials)

        last_trial_id = None
        for datapoint in data:
            trial_id, dp_id,timeStamp, node = datapoint

            if max_visits_total_participant < (max(visits_node_total)+1) or len(strategy_matrix_current_total) == 0:
                max_visits_total_participant = (max(visits_node_total) +1)
                strategy_matrix_current_total = resize_matrix(strategy_matrix_current_total, max_visits_total_participant+1)
            
            if max_visits_session_participant < (max(visits_node_currentSes)+1):
                max_visits_session_participant = (max(visits_node_currentSes)+1)
                strategy_matrix_current_sess = resize_matrix(strategy_matrix_current_sess, max_visits_session_participant+1)

            if max_visits_total <= max_visits_total_participant or len(strategy_matrix_total[session-1]) <= max_visits_total:
                if max_visits_total <= max_visits_total_participant:
                    max_visits_total = max_visits_total_participant+1
                strategy_matrix_total[session-1]  = resize_matrix(strategy_matrix_total[session-1] , max_visits_total+1)

            if max_visits_sessions <= max_visits_session_participant or len(strategy_matrix_total_sessions[session-1]) <= max_visits_sessions:
                if max_visits_sessions <= max_visits_session_participant:
                    max_visits_sessions = max_visits_session_participant+1
                strategy_matrix_total_sessions[session-1]  = resize_matrix(strategy_matrix_total_sessions[session-1] , max_visits_sessions+1)

            
            #if trial_id != last_trial_id and last_node != [] and last_node != node:
                #print("not the same node as in the previous session")

            if last_node != []:
                #TODO: get visits of neighbouring nodes (of the last element)
                #lastNode_neighbours = [neighbour for neighbour in getNodesNeighbours(last_node) if node != neighbour and pre_last_node != neighbour]
                lastNode_neighbours = [neighbour for neighbour in getNodesNeighbours(last_node) if node != neighbour]
                visits_current_node_total, visits_neighbours_total = getTotalVisitsNodes(node, lastNode_neighbours)
                visits_current_node_session, visits_neighbours_session = getSessionVisitsNodes(node, lastNode_neighbours)
                #TODO: adjust strategy matrix
                for visit in visits_neighbours_total:
                    strategy_matrix_current_total[visits_current_node_total][visit] += 1
                
                for visit in visits_neighbours_session:
                    strategy_matrix_current_sess[visits_current_node_session][visit] += 1

                # add visit to the visits count of the current node
                visits_node_total[node] += 1
                visits_node_currentSes[node] += 1
                # adjust strategy matrix in size if necessary

            last_trial_id = trial_id
            #pre_last_node = last_node
            last_node = node
        strategy_matrix_participant_total[session-1] = strategy_matrix_current_total
        strategy_matrix_participant_perSession[session-1] = strategy_matrix_current_sess
        
        strategy_matrix_total[session-1] =  addUpMatrices(strategy_matrix_total[session-1], strategy_matrix_current_total)
        strategy_matrix_total_sessions[session-1] = addUpMatrices(strategy_matrix_total_sessions[session-1], strategy_matrix_current_sess)

        last_session = session
        print("All visits counted")
    plotAndSafeStratMatrix(strategy_matrix_participant_total,strategy_matrix_participant_perSession,participant,sessions)
plotAndSafeStratMatrix(strategy_matrix_total,strategy_matrix_total_sessions)
print("All done")