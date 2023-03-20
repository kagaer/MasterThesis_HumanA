import sqlite3
from pathlib import Path
from typing import List, Tuple, Union
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import enum
from MultipleUseFunctions import * 
from Plotting import *
#from StrategyMatrix_Avatars_Expl import *

savepath = "E:/HumanA/Analysis/StrategyMatrices/"
# path to databases
print("For which experiment would you like to analyize the data?")
experiment = int(input())
if experiment == 1:
    db_path = Path('E:/HumanA/Data/Database/HumanA_Exp1.db')
    savepath = savepath + "Exp1/Dec_Expl_Matrix/Weights_Adjusted/"

elif experiment == 2:
    db_path = Path('E:/HumanA/Data/Database/HumanA_Exp2.db')
    savepath = savepath + "Exp2/Dec_Expl_Matrix/Weights_Adjusted/"

# check if path exists
if not db_path or not db_path.exists():
    db_path = ':memory:'

# connect to database
connection=sqlite3.connect(db_path)
cr=connection.cursor()


class TrialValidity(enum.Enum):
    Valid = 1
    MissingTrial = 2
    MissingSession = 3
    Undefined = 4

#weight = 2

class TrialValidity(enum.Enum):
    Valid = 1
    MissingTrial = 2
    MissingSession = 3
    Undefined = 4


def getVisits(node):
    """get the number of visits of a node for the current session and overall

    Args:
        node (int): node for which you want to get the number of visits

    Returns:
        visits_participant_total(int): total nr of visits for current participant
        visits_participant_currentSes (int) : session nr of visits for current participant
        visits_total (int) : total nr of visits over all participants
        visits_currentSes (int) : session nr of visits over all participants 
    """
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

def adjustVisits(node):
    visits_node_participant_total[node] += 1
    visits_node_participant_currentSes[node] += 1


def resizeStrategyMatrixes():
    global max_visits_total_participant
    global max_visits_session_participant
    global max_visits_total
    global max_visits_sessions
    global strategy_matrix_current_total
    global strategy_matrix_current_Session
    global strategy_matrix_total
    global strategy_matrix_perSession


    if max_visits_total_participant < max(visits_node_participant_total)+1 + weight or (len(strategy_matrix_current_total[0]) == 0 
        or len(strategy_matrix_current_total[1]) == 0 or len(strategy_matrix_current_total[2]) == 0 or len(strategy_matrix_current_total[3]) == 0 ):
        max_visits_total_participant = max(visits_node_participant_total)+1 + weight
        for i in range(len(strategy_matrix_current_total)):
            strategy_matrix_current_total[i] = resize_matrix(strategy_matrix_current_total[i], max_visits_total_participant+1)

    if max_visits_session_participant < max(visits_node_participant_currentSes)+1 + weight or (len(strategy_matrix_current_Session[0]) == 0 
        or len(strategy_matrix_current_Session[1]) == 0 or len(strategy_matrix_current_Session[2]) == 0 or len(strategy_matrix_current_Session[3]) == 0 ):
        max_visits_session_participant = max(visits_node_participant_currentSes)+1 + weight
        for i in range(len(strategy_matrix_current_Session)):
            strategy_matrix_current_Session[i] = resize_matrix(strategy_matrix_current_Session[i], max_visits_session_participant+1)

    if max_visits_total <= max_visits_total_participant + weight or (len(strategy_matrix_total[0][session-1]) <= max_visits_total or 
        len(strategy_matrix_total[1][session-1]) <= max_visits_total or len(strategy_matrix_total[2][session-1]) <= max_visits_total or len(strategy_matrix_total[3][session-1]) <= max_visits_total):
        if max_visits_total <= max_visits_total_participant + weight:
            max_visits_total = max_visits_total_participant+ 1 +  weight
        
        for i in range(len(strategy_matrix_total)):
            strategy_matrix_total[i][session-1]  = resize_matrix(strategy_matrix_total[i][session-1] , max_visits_total+1)

    if max_visits_sessions <= max_visits_session_participant or (len(strategy_matrix_perSession[0][session-1]) <= max_visits_sessions or
        len(strategy_matrix_perSession[1][session-1]) <= max_visits_sessions or len(strategy_matrix_perSession[2][session-1]) <= max_visits_sessions or len(strategy_matrix_perSession[3][session-1]) <= max_visits_sessions):
        if max_visits_sessions <= max_visits_session_participant + weight:
            max_visits_sessions = max_visits_session_participant+1 + weight
        for i in range(len(strategy_matrix_perSession)):
            strategy_matrix_perSession[i][session-1]  = resize_matrix(strategy_matrix_perSession[i][session-1] , max_visits_sessions+1)

def addVisitToStrategyMatrix(node,decisions, weight):
    visits_cur_node_part_total,visits_cur_node_part_ses, _,_= getVisits(node)


    for _,neighbour,decision in decisions:
        visits_neighbour_part_total,visits_neighbour_part_ses, _,_= getVisits(neighbour)
        if decision == 'AvatarAtChosen':
            strategy_matrix_current_total[0][visits_cur_node_part_total][visits_neighbour_part_total+weight] += 1
            strategy_matrix_current_Session[0][visits_cur_node_part_ses][visits_neighbour_part_ses+weight] += 1

        elif decision == 'AvatarAtNotChosen':
            strategy_matrix_current_total[1][visits_cur_node_part_total+weight][visits_neighbour_part_total] += 1
            strategy_matrix_current_Session[1][visits_cur_node_part_ses+weight][visits_neighbour_part_ses] += 1
        elif decision == 'AvatarAtBoth':
            strategy_matrix_current_total[2][visits_cur_node_part_total][visits_neighbour_part_total] += 1
            strategy_matrix_current_Session[2][visits_cur_node_part_ses][visits_neighbour_part_ses] += 1
        else: 
            strategy_matrix_current_total[3][visits_cur_node_part_total][visits_neighbour_part_total] += 1
            strategy_matrix_current_Session[3][visits_cur_node_part_ses][visits_neighbour_part_ses] += 1

#def calc_plot_matrices(weight):
weight = 1
weights_adjusted = ' Weight: ' + str(weight)
participants = getParticipants(cr) 
max_node = getMaxNodeFromDB(cr)
count_dec_seeking_total, count_dec_avoiding_total = getCountDecisionsTotal()
count_dec_seeking_total_ses, count_dec_avoiding_total_ses = getCountDecisionsSessionTotal()
strategy_matrix_total = [[np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))],
                        [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))],
                        [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))],
                        [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]]


strategy_matrix_perSession = [[np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))],
                        [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))],
                        [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))],
                        [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]]

max_visits_total = 0 + weight
max_visits_sessions = 0 + weight
visits_node_total = [0]*(max_node + 1)
visits_node_perSession = [0]*(max_node + 1)

for participant in participants:
    visits_node_participant_total = [0]*(max_node + 1)

    strategy_matrix_participant_total = [[np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))],
                                        [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))],
                                        [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))],
                                        [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]]

    strategy_matrix_participant_perSession = [[np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))],
                                        [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))],
                                        [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))],
                                        [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]]

    sessions = getSessions(participant, cr)
    last_session = 0

    last_node = []
    max_visits_total_participant = 0 + weight

    count_dec_seeking_part = 0
    count_dec_avoiding_part = 0
    count_dec_seeking_ses = 5*[0]
    count_dec_avoiding_ses = 5*[0]

    for session in sessions:
        print("Participant: " + str(participant) + " | Session: " + str(session))
        visits_node_participant_currentSes = [0]*(max_node + 1)

        strategy_matrix_current_total = [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]
        strategy_matrix_current_Session = [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]

        max_visits_session_participant = 0 + weight
        trials = getTrialNrs(participant, session, cr)

        if len(trials) < 3:
            print("Missing trials for this session")
            continue

        data = getDatapoints(trials, cr)
        dp_ids_total = tuple([datapoint[1] for datapoint in data])
        count_dec_seeking,count_dec_avoiding = getCountDecisions(dp_ids_total)
        count_dec_seeking_ses[session-1] = count_dec_seeking
        count_dec_avoiding_ses[session-1] = count_dec_avoiding

        count_dec_seeking_part += count_dec_seeking
        count_dec_avoiding_part += count_dec_avoiding

        for datapoint in data:
            trial_id, dp_id,timeStamp, node = datapoint
            if last_node != []:
                decisions = getDecisions(dp_id, cr)


                resizeStrategyMatrixes()
                addVisitToStrategyMatrix(node,decisions, weight)
                adjustVisits(node)

            last_node = node
        
        strategy_matrix_participant_total[0][session-1] = strategy_matrix_current_total[0] 
        strategy_matrix_participant_total[1][session-1] = strategy_matrix_current_total[1] 
        strategy_matrix_participant_total[2][session-1] = strategy_matrix_current_total[2]
        strategy_matrix_participant_total[3][session-1] = strategy_matrix_current_total[3] 

        strategy_matrix_participant_perSession[0][session-1] = strategy_matrix_current_Session[0]
        strategy_matrix_participant_perSession[1][session-1]  = strategy_matrix_current_Session[1]
        strategy_matrix_participant_perSession[2][session-1]  = strategy_matrix_current_Session[2]
        strategy_matrix_participant_perSession[3][session-1]  = strategy_matrix_current_Session[3]


        strategy_matrix_total[0][session-1] = addUpMatrices(strategy_matrix_total[0][session-1], strategy_matrix_current_total[0]) 
        strategy_matrix_total[1][session-1] = addUpMatrices(strategy_matrix_total[1][session-1], strategy_matrix_current_total[1]) 
        strategy_matrix_total[2][session-1] = addUpMatrices(strategy_matrix_total[2][session-1], strategy_matrix_current_total[2]) 
        strategy_matrix_total[3][session-1] = addUpMatrices(strategy_matrix_total[3][session-1], strategy_matrix_current_total[3]) 

        strategy_matrix_perSession[0][session-1] = addUpMatrices(strategy_matrix_perSession[0][session-1], strategy_matrix_current_Session[0]) 
        strategy_matrix_perSession[1][session-1] = addUpMatrices(strategy_matrix_perSession[1][session-1], strategy_matrix_current_Session[1]) 
        strategy_matrix_perSession[2][session-1] = addUpMatrices(strategy_matrix_perSession[2][session-1], strategy_matrix_current_Session[2]) 
        strategy_matrix_perSession[3][session-1] = addUpMatrices(strategy_matrix_perSession[3][session-1], strategy_matrix_current_Session[3]) 

        last_session = session
        print("All visits counted")
    #print()
    plotTotal(strategy_matrix_participant_total,count_dec_seeking_part,count_dec_avoiding_part,participant,sessions, weights_adjusted = weights_adjusted,
              save_path = savepath)
    plotSession(strategy_matrix_participant_perSession,count_dec_seeking_ses,count_dec_avoiding_ses,participant,sessions, weights_adjusted = weights_adjusted,
              save_path = savepath)

plotTotal(strategy_matrix_total,count_dec_seeking_total,count_dec_avoiding_total,participants = participants, weights_adjusted = weights_adjusted,
              save_path = savepath)
plotSession(strategy_matrix_perSession,count_dec_seeking_total_ses,count_dec_avoiding_total_ses,participants = participants, weights_adjusted = weights_adjusted,
              save_path = savepath)

print("All done")
connection.close()

#weight = 2
#calc_plot_matrices(weight)