import numpy as np


def getParticipants(cr):
    """get all participantIds from the database

    Returns:
        tuple: list of participants
    """
    # select all participantIds and return them
    sql_instruction = """
    SELECT DISTINCT participantId FROM trials WHERE id IN (SELECT id FROM trials WHERE validSession = 'VALID' AND validParticipant = 'VALID')
    """
    #SELECT DISTINCT participantId FROM trials WHERE validParticipant = 'VALID';
    #"""
    cr.execute(sql_instruction)
    participants = tuple(did[0] for did in cr.fetchall())
    return participants

def getStrategyCounts(matrix):
    count_cons = 0
    count_expl = 0
    count_total = 0
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            if i > j:
                count_cons += matrix[i][j]
                count_total += matrix[i][j]
            elif i < j:
                count_expl += matrix[i][j]
                count_total += matrix[i][j]
    return round(count_cons,0), round(count_expl,0), count_total

def getSessions(participant, cr):
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

def getTrialNrs(participant, session, cr):
    """get all trialIds for the current participant, current session

    Args:
        participant (int): current participant

    Returns:
        tuple: all trialIds 
    """

    sql_instruction = f"""
    SELECT DISTINCT id 
    FROM trials
    WHERE participantId = {participant} AND sessionNr = {session} AND validSession = 'VALID' AND validParticipant = 'VALID'
    """
    
    cr.execute(sql_instruction)
    trialIdx = tuple(did[0] for did in cr.fetchall())
    return trialIdx

def getDatapoints(trials, cr):
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

def getDecisions(dp_id, cr):
    sql_instruction = f"""
    SELECT participant_decision.Id, participant_decision.last_node_neighbour, participant_decision.decision
    FROM participant_decision
    WHERE participant_decision.datapointId = {dp_id}
    ;
        """
    cr.execute(sql_instruction)
    decisions = cr.fetchall()
    return decisions

def getMaxNodeFromDB(cr):
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

def addUpMatrices(matrix1, matrix2):
# iterate through rows
    result = matrix1
    for i in range(len(matrix2)):  
    # iterate through columns
        for j in range(len(matrix2[0])):
            result[i][j] = matrix1[i][j] + matrix2[i][j]
    
    return result