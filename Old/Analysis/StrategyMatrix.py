import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go

class StrategyMatrix():
    """Class for constructing a Strategy for a single participant"""

    def __init__(self, participantId, cursor, savepath = 'E:/HumanA/Default/'):
        self.participantId = participantId
        self.getSessions = StrategyMatrix.getSessions()
        self.savepath = savepath
        self.cr = cursor
        self.visits_node_total = [0]*(158 + 1)
        self.visits_node_currentSes = [0]*(158 + 1)
        self.matrix_total = [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]
        self.matrix_perSession = [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]
        self.max_visits_total_participant = 0

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

# region ADJUST MATRIX
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
# endregion ADJUST MATRIX

# region PLOTTING FUNCTIONS 
    def plotAndSafeStratMatrix(self, matrix_total,matrix_sessions, participant = None, sessions = (1,2,3,4,5)):

        filename = "Strategy_Matrix_Expl_" + str(participant) + ".png"

        #filename = "Strategy_Matrix_" + str(participant) + ".png"
        title = "Participant: " + str(participant)


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
                count_cons, count_expl, count_total = StrategyMatrix.getStrategyCounts(matrix_total[session-1])
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
                        xref = 'x domain', yref = 'y domain', 
                        align="left",
                        name="Strategy Counts", row=1, col = session)
            if len(matrix_sessions[session-1]) > 0:

                count_cons, count_expl, count_total = StrategyMatrix.getStrategyCounts(matrix_sessions[session-1])
                perc_cons = round((count_cons/count_total), 2)
                perc_expl = round((count_expl/count_total),2)
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
                fig.add_annotation(text = "Expl: " + str(count_expl) + " " + "(" + str(perc_expl) + ")"
                            "<br>Cons: " + str(count_cons) + " " + "(" + str(perc_cons) + ")",
                        showarrow=False,
                        bordercolor='black',
                        borderwidth=1,
                        x = 0, y = 1,
                        xanchor= 'left', yanchor='top',
                        xref = 'x domain', yref = 'y domain', 
                        align="left",
                        name="Strategy Counts", row=2, col = session)

        fig.write_image((self.savepath + filename))

# endregion PLOTTING FUNCTIONS 

# region CREATE MATRIX

    def createMatrix(self):
        sessions = StrategyMatrix.getSessions(self)
        last_node = []
        for session in sessions:
            matrix_current_total = np.zeros((0,0))
            matrix_current_session = np.zeros((0,0))

            self.visits_node_currentSes = [0]*(158 + 1)
            max_visits_session_participant = 0
            trials = StrategyMatrix.getTrialNrs(self, session)
            #if len(trials) < 3:
            #    print("Missing trials for this session")
            #    continue
            data = StrategyMatrix.getDatapoints(self, trials)

            #last_trial_id = None
            for datapoint in data:
                _, _,_, node = datapoint

                if self.max_visits_total_participant < (max(self.visits_node_total)+1) or len(matrix_current_total) == 0:
                    self.max_visits_total_participant = (max(self.visits_node_total) +1)
                    matrix_current_total = StrategyMatrix.resize_matrix(matrix_current_total, self.max_visits_total_participant+1)

                if max_visits_session_participant < (max(self.visits_node_currentSes)+1):
                    max_visits_session_participant = (max(self.visits_node_currentSes)+1)
                    matrix_current_session = StrategyMatrix.resize_matrix(matrix_current_session, max_visits_session_participant+1)

                #if max_visits_total <= max_visits_total_participant or len(self.matrix_total[session-1]) <= max_visits_total:
                #    if max_visits_total <= max_visits_total_participant:
                #        max_visits_total = max_visits_total_participant+1
                #    self.matrix_total[session-1]  = StrategyMatrix.resize_matrix(self.matrix_total[session-1] , max_visits_total+1)
#
                #if max_visits_sessions <= max_visits_session_participant or len(self.matrix_total_sessions[session-1]) <= max_visits_sessions:
                #    if max_visits_sessions <= max_visits_session_participant:
                #        max_visits_sessions = max_visits_session_participant+1
                #    self.matrix_total_sessions[session-1]  = StrategyMatrix.resize_matrix(self.matrix_total_sessions[session-1] , max_visits_sessions+1)



                if last_node != []:
                    # get visits of neighbouring nodes (of the last element)
                    lastNode_neighbours = [neighbour for neighbour in StrategyMatrix.getNodesNeighbours(self, last_node) if node != neighbour]
                    visits_current_node_total, visits_neighbours_total = StrategyMatrix.getTotalVisitsNodes(self, node, lastNode_neighbours)
                    visits_current_node_session, visits_neighbours_session = StrategyMatrix.getSessionVisitsNodes(self, node, lastNode_neighbours)
                    # adjust strategy matrix
                    for visit in visits_neighbours_total:
                        matrix_current_total[visits_current_node_total][visit] += 1

                    for visit in visits_neighbours_session:
                        matrix_current_session[visits_current_node_session][visit] += 1

                    # add visit to the visits count of the current node
                    self.visits_node_total[node] += 1
                    self.visits_node_currentSes[node] += 1
                    # adjust strategy matrix in size if necessary

                #last_trial_id = trial_id
                #pre_last_node = last_node
                last_node = node
            self.matrix_total[session-1] = matrix_current_total
            self.matrix_perSession[session-1] = matrix_current_session

            #self.matrix_total[session-1] =  StrategyMatrix.addUpMatrices(self.matrix_total[session-1], strategy_matrix_current_total)
            #self.matrix_total_sessions[session-1] = StrategyMatrix.addUpMatrices(self.matrix_total_sessions[session-1], strategy_matrix_current_sess)

            #last_session = session

    def plotMatrix(self):
        sessions = StrategyMatrix.getSessions(self)
        StrategyMatrix.plotAndSafeStratMatrix(self, self.matrix_total, self.matrix_perSession, self.participantId, sessions)
        

# endregion CREATE MATRIX