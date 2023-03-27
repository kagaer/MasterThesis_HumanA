import numpy as np

class StrategyMatrix():
    """Class for constructing a Strategy for a single participant"""

    def __init__(self, participantId, cursor, savepath = 'E:/HumanA/Default'):
        self.participantId = participantId
        self.savepath = savepath
        self.cr = cursor
        self.visits_node_total = [0]*(158 + 1)
        self.visits_node_currentSes = [0]*(158 + 1)

    def getSessions(self):
        """get all sessionNrs for the current participant from the database
    
        Returns:
            tuple: list of participants
        """
        # select all participantIds and return them
        sql_instruction = f"""
        SELECT DISTINCT sessionNr FROM trials WHERE participantId = {self.participantId} AND validSession = 'VALID'
        ORDER BY sessionNr;
        """
        self.cr.execute(sql_instruction)
        sessions = tuple(did[0] for did in self.cr.fetchall())
        return sessions
    
    def getTrialNrs(self, session):
        """get all trialIds for the current participant, current session
    
        Args:
            participant (int): current participant
    
        Returns:
            tuple: all trialIds 
        """
    
        sql_instruction = f"""
        SELECT DISTINCT id 
        FROM trials
        WHERE participantId = {self.participantId} AND sessionNr = {session}
        """
        
        self.cr.execute(sql_instruction)
        trialIdx = tuple(did[0] for did in self.cr.fetchall())
        return trialIdx

    def getDatapoints(self, trials):
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
        """

        self.cr.execute(sql_instruction)
        data = self.cr.fetchall()
        return data

    #def getMaxNodeFromDB(self):
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
    #    self.cr.execute(sql_instruction)
    #    max_node = self.cr.fetchone()
    #    return max_node[0]
    
    def getNodesNeighbours(self, node):
        """get the neighbouring nodes of a node from the database

        Args:
            node (int): node for which the neighbours are selected

        Returns:
            neighbours (list(int)) : list of all the neighbours found
        """

        sql_instruction = f"""SELECT * FROM node_neighbours WHERE FirstNode = {node} or SecondNode = {node}"""
        self.cr.execute(sql_instruction)
        nodes_and_neighbours = self.cr.fetchall()
        neighbours = []
        for node_and_neighbour in nodes_and_neighbours:
            if node_and_neighbour[0] == node:
                neighbours.append(node_and_neighbour[1])
            elif node_and_neighbour[1] == node:
                neighbours.append(node_and_neighbour[0])
        return neighbours
    
    def getTotalVisitsNodes(self, chosenNode, neighbouringNodes):
        visits_chosenNode = self.visits_node_total[chosenNode]
        visits_neighbouringNodes = [self.visits_node_total[node] for node in neighbouringNodes]

        return visits_chosenNode, visits_neighbouringNodes

    def getSessionVisitsNodes(self, chosenNode, neighbouringNodes):
        visits_chosenNode = self.visits_node_currentSes[chosenNode]
        visits_neighbouringNodes = [self.visits_node_currentSes[node] for node in neighbouringNodes]

        return visits_chosenNode, visits_neighbouringNodes
    
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



#participant_s_Mat = StrategyMatrix(1245)
