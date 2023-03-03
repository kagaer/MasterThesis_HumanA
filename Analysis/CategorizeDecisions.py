import sqlite3
from pathlib import Path
from typing import List, Tuple, Union
import numpy as np
import enum

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

# connect to database
connection=sqlite3.connect(db_path)
cr=connection.cursor()

class DecisionCategory(enum.Enum):
    AvatarAtBoth = 1
    AvatarAtChosen = 2
    AvatarAtNotChosen = 3
    NoAvatarAtBoth = 4

def create_decision_table():

    """create a table in the database that stores the information for the reduced data"""

    sql_instruction = """
    CREATE TABLE IF NOT EXISTS "participant_decision"(
    "Id" INTEGER NOT NULL UNIQUE,
    "DatapointId" INTEGER NOT NULL,
    "last_node_neighbour" NUMERIC,
    "decision" TEXT,
    PRIMARY KEY ("Id" AUTOINCREMENT)
    FOREIGN KEY(DatapointId) REFERENCES data_points(Id)
    FOREIGN KEY(last_node_neighbour) REFERENCES graph_coordinates(nodeNr)
    );
    """
    cr.execute(sql_instruction)
    connection.commit()

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
    SELECT DISTINCT sessionNr FROM trials WHERE participantId = {participant}
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
    WHERE participantId = {participant} AND sessionNr = {session} AND id IN (SELECT trialId FROM datapoints_analysis)
    ORDER BY timeTrialMeasurementStarted ASC
    """
    
    cr.execute(sql_instruction)
    trialIdx = tuple(did[0] for did in cr.fetchall())
    if len(trialIdx) < 3:
        trialIdx = []
    return trialIdx

def getDatapoints(trial):
    """get all datapoints for the current trial, sorted by the timestamp (timeStampDataPointStart), and joined with the trialId and participantId

    Args:
        trial (int): current trial

    Returns:
        list: all datapoints for this trial 
    """
    #if len(trials) == 1:
    #    trials = '('+ str(trials[0]) +')'
    sql_instruction = f"""
    SELECT dataPoints_analysis.DatapointId, dataPoints_analysis.timeStampDataPointStart, dataPoints_analysis.node
    FROM dataPoints_analysis
    WHERE dataPoints_analysis.trialId = {trial}
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


def getAvatarPositions():
    sql_instruction = f"""SELECT node FROM avatars_reduced WHERE graph_element_type = 'Node'"""
    cr.execute(sql_instruction)
    avatarNodes = [did[0] for did in cr.fetchall()]

    sql_instruction = f"""SELECT edge_start,edge_end FROM avatars_reduced WHERE graph_element_type = 'Edge'"""
    cr.execute(sql_instruction)
    avatarEdges = [list(did) for did in cr.fetchall()]

    return avatarNodes,avatarEdges

#def avatarInDirection(lastNode, neighbours, currentNode):
#    avatarNotChosenDir = []
#    noAvatarNotChosenDir = []
#    isAvatarInChosenDir = False
#    if currentNode in avatarNodes or [lastNode, currentNode] in avatarEdges or [currentNode, lastNode] in avatarEdges:
#        isAvatarInChosenDir = True
#        noAvatarNotChosenDir = [node for node in neighbours if node not in avatarNodes and [lastNode, node] not in avatarEdges and [node, lastNode] not in avatarEdges]
#        avatarNotChosenDir = [node for node in neighbours if node in avatarNodes or [lastNode, node] in avatarEdges or [node, lastNode] in avatarEdges]
#
#    else: 
#        avatarNotChosenDir = [node for node in neighbours if node in avatarNodes or [lastNode, node] in avatarEdges or [node, lastNode] in avatarEdges]
#
#    return isAvatarInChosenDir, avatarNotChosenDir,noAvatarNotChosenDir

def avatarInDecision(last_node, current_node, neighbouring_node):
    isAvatarAtChosen = False
    isAvatarAtNotChosen = False
    if current_node in avatarNodes or [last_node, current_node] in avatarEdges or [current_node, last_node] in avatarEdges:
        isAvatarAtChosen = True
        #if neighbouring_node in avatarNodes or [last_node, neighbouring_node] in avatarEdges or [neighbouring_node, last_node] in avatarEdges:
        #    isAvatarAtNotChosen = True
    if neighbouring_node in avatarNodes or [last_node, neighbouring_node] in avatarEdges or [neighbouring_node, last_node] in avatarEdges:
        isAvatarAtNotChosen = True
    return isAvatarAtChosen, isAvatarAtNotChosen

def getParticipantDecision(last_node, current_node, neighbouring_node):
    decision = ''
    isAvatarAtChosen, isAvatarAtNotChosen = avatarInDecision(last_node, current_node, neighbouring_node)
    if isAvatarAtChosen and isAvatarAtNotChosen:
        decision = DecisionCategory(1).name
    elif isAvatarAtChosen and not isAvatarAtNotChosen:
        decision = DecisionCategory(2).name
    elif not isAvatarAtChosen and isAvatarAtNotChosen:
        decision = DecisionCategory(3).name  
    else:
        decision = DecisionCategory(4).name
    return str(decision)

def addDecisionToDB(dp_id, neighbouring_node, decision):
    values = str((dp_id, neighbouring_node, decision))
    sql_instruction = f"""INSERT INTO participant_decision (DatapointId,last_node_neighbour, decision)
    VALUES {values}"""
    cr.execute(sql_instruction)

def trial_in_db(trial):
    """check if the current trial is already in the database (participant_decision)

    Args:
        trial (int): current trialId

    Returns:
        bool: true if trial is in database
    """

    sql_instruction = """
    SELECT DISTINCT dataPoints_analysis.trialId FROM dataPoints_analysis
    INNER JOIN participant_decision ON dataPoints_analysis.DatapointId = participant_decision.DatapointId
    """
    cr.execute(sql_instruction)
    content = cr.fetchall()
    if (trial,) in content:
        return True
    else:
        return False

#def getVisits(currentNode, avatarNotChosenDir, noAvatarNotChosenDir):
#    visits_current_node = visits_node[currentNode]
#    visits_avat_notChosen = [visits_node[node] for node in avatarNotChosenDir]
#    visits_no_avat_notChosen = [visits_node[node] for node in noAvatarNotChosenDir]
#
#    return visits_current_node, visits_avat_notChosen, visits_no_avat_notChosen

#def adjustStrategyMatrix(matrix, isAvatarAtChosen, visits_currentNode, visits_avat_notChosen,visits_no_avat_notChosen):
#    if isAvatarAtChosen and visits_no_avat_notChosen != []:
#        for visits_noAvat in visits_no_avat_notChosen:
#            matrix[0][visits_currentNode][visits_noAvat] += 1
#    elif isAvatarAtChosen and visits_avat_notChosen != []:
#        for visits_Avat in visits_avat_notChosen:
#            matrix[0][visits_currentNode][visits_Avat] += 1
#        #matrix[1][visits_currentNode][visits_avat_notChosen] += 1    
#    elif not isAvatarAtChosen and visits_avat_notChosen != []:
#        for visits_Avat in visits_avat_notChosen:
#            matrix[0][visits_currentNode][visits_Avat] += 1
#        #matrix[2][visits_currentNode][visits_avat_notChosen] += 1 
#    return matrix

create_decision_table()

participants = getParticipants()
#max_node = getMaxNodeFromDB()
avatarNodes, avatarEdges = getAvatarPositions()
for participant in participants:
    sessions = getSessions(participant)
    for session in sessions:

        trials = getTrialNrs(participant, session)
        last_node = []
        for trial in trials:
            if not trial_in_db(trial):
                print("Participant: " + str(participant) + " | Trial: " + str(trial))
                data = getDatapoints(trial)
                for datapoint in data:
                    dp_id,timeStamp, node = datapoint
                    if last_node != []:
                        lastNode_neighbours = [neighbour for neighbour in getNodesNeighbours(last_node) if neighbour != node]
                        for neighbouring_node in lastNode_neighbours:
                            participant_decision = getParticipantDecision(last_node, node, neighbouring_node)
                            addDecisionToDB(dp_id, neighbouring_node, participant_decision)
                    last_node = node
                connection.commit()
connection.close()
print("All decisions added to DB")




