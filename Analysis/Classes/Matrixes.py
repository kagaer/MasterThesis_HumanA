import numpy as np
#from plotly.subplots import make_subplots
#import plotly.graph_objects as go

class Matrix():
    """Class for constructing a Strategy for a single participant"""

    def __init__(self, participantId,   cursor, nrMatrixes = 1, savepath = 'E:/HumanA/Default/'):
        self.participantId = participantId
        self.cr = cursor
        self.sessions = Matrix.getSessions(self)
        self.maxNode = Matrix.getMaxNodeFromDB(self)
        self.savepath = savepath
        self.visits_node_total = [0]*(self.maxNode + 1)
        self.visits_over_sessions = []
        #self.visits_node_currentSes = [0]*(self.maxNode + 1)
        self.max_visits_total_participant = 0
        if nrMatrixes == 1:
            self.matrix_total= [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]
            self.matrix_perSession = [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]
        else:
            self.matrix_total= []
            self.matrix_perSession = []
            for i in range(nrMatrixes):
                self.matrix_total.append([np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))])
                self.matrix_perSession.append([np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))])
        #if nrMatrixes == 1:
        #    self.matrix_total = [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]
        #    self.matrix_perSession = [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]
        #elif nrMatrixes > 1:
        #    self.matrix_total = np.tile([np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))] , [nrMatrixes, 5])
        #    self.matrix_perSession = np.tile([np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))] , [nrMatrixes, 5])

# region GETTER
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

    def getMaxNodeFromDB(self):
        """get the max node from the database

        Returns:
            max_node (int): max node
        """

        sql_instruction = f"""
        SELECT MAX(nodeNr) FROM graph_coordinates
        """

        self.cr.execute(sql_instruction)
        max_node = self.cr.fetchone()
        #maxNode = tuple(did[0] for did in cr.fetchall())
        return max_node[0]
    
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
# endregion GETTER

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