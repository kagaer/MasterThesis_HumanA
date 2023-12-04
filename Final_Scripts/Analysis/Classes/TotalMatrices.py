from Matrixes import *
from AgentStrategyMatrix import *
from plotly.subplots import make_subplots
import plotly.graph_objects as go

class TotalMatrix():
    """Class for constructing a Strategy Matrices for all participants"""

    def __init__(self, cursor, weight = 0, savepath= 'E:/HumanA/Default/'):
        #nrMatrixes = 9
        self.cr = cursor
        self.weight = weight
        self.savepath = savepath
        self.totalMatrix = [[np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))],
                                  [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))],
                                  [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))],
                                  [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]]
        self.participants = TotalMatrix.getParticipants(self.cr)
        self.createAllMatrices(self.participants)

        #super().__init__(participantId, cursor, nrMatrixes, savepath)
        
        


    def getParticipants(cr):
        """get all participantIds from the database

        Returns:
            tuple: list of participants
        """

        sql_instruction = """
        SELECT DISTINCT participantId FROM trials WHERE validParticipant = 'VALID'
        """
        #;

        cr.execute(sql_instruction)
        participants = tuple(did[0] for did in cr.fetchall())
        return participants
    
    def createAllMatrices(self, participants):
        #self.totalMatrix = [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), 
        #                                 np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]
        for participant in participants:
            #print('Participant: ' + str(participant))
            curMatrix = AgentStrategyMatrix(participant, self.cr, savepath= self.savepath)
            for i  in range(len(self.totalMatrix)):
                for session in curMatrix.sessions:
                    if self.totalMatrix[i][session-1].shape[0] < curMatrix.matrix_total[i][session-1].shape[0]:
                        self.totalMatrix[i][session-1] = Matrix.resize_matrix(self.totalMatrix[i][session-1], curMatrix.matrix_total[i][session-1].shape[0] + 1)
                    elif self.totalMatrix[i][session-1].shape[1] < curMatrix.matrix_total[i][session-1].shape[1]:
                        self.totalMatrix[i][session-1] = Matrix.resize_matrix(self.totalMatrix[i][session-1], curMatrix.matrix_total[i][session-1].shape[1] + 1)
                    self.totalMatrix[i][session-1] = self.addUpMatrices(self.totalMatrix[i][session-1], curMatrix.matrix_total[i][session-1])
        print('Strategy Matrix completed')



    def addUpMatrices(self, matrix1, matrix2):
    # iterate through rows
        result = matrix1
        for i in range(len(matrix2)):  
        # iterate through columns
            for j in range(len(matrix2[0])):
                result[i][j] = matrix1[i][j] + matrix2[i][j]
    
        return result   
    

#    def plotAtChosen(self, matrix, sessions = (1,2,3,4,5), weights_adjusted = False):
#        if not weights_adjusted:
#            filename = "Total_Decision_Matrix_ActAtChosen_Agent_Total.png"
#            title = "All Participants"
#        else: 
#            filename = "Total_Weighted_Decision_Matrix_ActAtChosen_Agent_Total.png"
#            title = "All Participants"  + " Weight: " + str(self.weight)
# 
#        sum_actAvatAtChos = matrix[0][0].sum() + matrix[0][1].sum() + matrix[0][2].sum() +  matrix[0][3].sum() + matrix[0][4].sum()
#        sum_actAvatAtChosPasAvatAtNotChos = matrix[1][0].sum() + matrix[1][1].sum() + matrix[1][2].sum() +  matrix[1][3].sum() + matrix[1][4].sum()
#        sum_actAvatAtBoth = matrix[2][0].sum() + matrix[2][1].sum() + matrix[2][2].sum() +  matrix[2][3].sum() + matrix[2][4].sum()
#        
#        sum_pasAvatAtChos = matrix[3][0].sum() + matrix[3][1].sum() + matrix[3][2].sum() +  matrix[3][3].sum() + matrix[3][4].sum()
#        sum_pasAvatAtChosActAvatAtNotChos = matrix[4][0].sum() + matrix[4][1].sum() + matrix[4][2].sum() +  matrix[4][3].sum() + matrix[4][4].sum()
#        sum_pasAvatAtBoth = matrix[5][0].sum() + matrix[5][1].sum() + matrix[5][2].sum() +  matrix[5][3].sum() + matrix[5][4].sum()
#        
#        sum_actAtNotChosen = matrix[6][0].sum() + matrix[6][1].sum() + matrix[6][2].sum() +  matrix[6][3].sum() + matrix[6][4].sum()
#        sum_pasAtNotChosen = matrix[7][0].sum() + matrix[7][1].sum() + matrix[7][2].sum() +  matrix[7][3].sum() + matrix[7][4].sum()
#        sum_NoavatAtBoth = matrix[8][0].sum() + matrix[8][1].sum() + matrix[8][2].sum() +  matrix[8][3].sum() + matrix[8][4].sum() 
#        
#        sum_Total = (sum_actAvatAtChos + sum_actAvatAtChosPasAvatAtNotChos + sum_actAvatAtBoth + sum_pasAvatAtChos + 
#            sum_pasAvatAtChosActAvatAtNotChos + sum_pasAvatAtBoth + sum_actAtNotChosen + sum_pasAtNotChosen + sum_NoavatAtBoth)
##
#        perc_actAvatAtChos = round((sum_actAvatAtChos/sum_Total), 2)
#        perc_actAvatAtChosPasAvatAtNotChos = round((sum_actAvatAtChosPasAvatAtNotChos/sum_Total), 2)
#        perc_actAvatAtBoth = round((sum_actAvatAtBoth/sum_Total), 2)
#
#        diagonal_lines = [
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.733, 'y1': 1, 'x0': 0, 'x1': 0.168},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.733, 'y1': 1, 'x0': 0.208, 'x1': 0.376},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.733, 'y1': 1, 'x0': 0.417, 'x1': 0.584},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.733, 'y1': 1, 'x0': 0.624, 'x1': 0.792},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.733, 'y1': 1, 'x0': 0.832, 'x1': 1},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.368, 'y1': 0.635, 'x0': 0, 'x1': 0.168},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.368, 'y1': 0.635, 'x0': 0.208, 'x1': 0.376},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.368, 'y1': 0.635, 'x0': 0.417, 'x1': 0.584},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.368, 'y1': 0.635, 'x0': 0.624, 'x1': 0.792},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.368, 'y1': 0.635, 'x0': 0.832, 'x1': 1},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.0, 'y1': 0.267, 'x0': 0, 'x1': 0.168},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.0, 'y1': 0.267, 'x0': 0.208, 'x1': 0.376},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.0, 'y1': 0.267, 'x0': 0.417, 'x1': 0.584},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.0, 'y1': 0.267, 'x0': 0.624, 'x1': 0.792},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.0, 'y1': 0.267, 'x0': 0.832, 'x1': 1},
#            ]  
#
#        fig = make_subplots(
#            rows=3, 
#            cols=5, 
#            subplot_titles=("Act Agent at Chosen (" + str(perc_actAvatAtChos) + "): <br>" + "Session 1:" , "Session 2: ", "Session 3","Session 4", "Session 5",
#                            "Act Agent at Chosen, Pas Agent at not Chosen (" + str(perc_actAvatAtChosPasAvatAtNotChos) + "): <br>Session 1", "Session 2", "Session 3", "Session 4", "Session 5",
#                            "Act Agent at Both (" + str(perc_actAvatAtBoth) + "):<br>Session 1", "Session 2", "Session 3", "Session 4", "Session 5"), 
#            x_title="Number of previous visits not chosen nodes", 
#            y_title="Number of previous visits chosen node",
#            vertical_spacing = 0.1
#            )
#
#        fig.update_layout(margin=dict(t=200))
#        for i in range(3):
#            for session in sessions:
#                if len(matrix[i][session-1]) > 0:
#                    count_cons, count_expl, count_total = Matrix.getStrategyCounts(matrix[i][session-1])
#                    if count_cons > 0:
#                        perc_cons = round((count_cons/count_total), 2)
#                    else:
#                        perc_cons = 0.00
#                    if count_expl > 0:
#                        perc_expl = round((count_expl/count_total),2)
#                    else:
#                        perc_expl = 0.00
#
#                    matrix_text = np.array(np.array(matrix[i][session-1],dtype='int'),dtype='str')
#                    matrix_text[matrix_text == '0'] = ""
#                    colorscale = "Sunset"
#                    fig.add_trace(go.Heatmap(z=matrix[i][session-1], text=matrix_text, texttemplate="%{text}", textfont={"size":12}, colorscale = colorscale,), 
#                        row=i+1, col=session)
#                    fig.update_traces(showscale=False)
#                    fig.add_annotation(text = "Expl: " + str(count_expl) + " " + "(" + str(perc_expl) + ")"
#                            "<br>Cons: " + str(count_cons) + " " + "(" + str(perc_cons) + ")",
#                        showarrow=False,
#                        bordercolor='black',
#                        borderwidth=1,
#                        x = 0, y = 1,
#                        xanchor= 'left', yanchor='top',
#                        xref = 'x domain', yref = 'y domain',
#                        align="left",
#                        name="Strategy Counts", row=i+1, col = session)
#
#        fig.update_layout(
#                    title_text=title,
#                    boxmode='group',
#                    width=2000,
#                    height=1500,
#                    shapes=diagonal_lines,
#                    font=dict(
#                        size=18,
#                        )
#                )
#        fig.write_image((self.savepath + filename))

#    def plotPasAgentAtChosen(self, matrix, sessions = (1,2,3,4,5), weights_adjusted = False):
#        if not weights_adjusted:
#            filename = "Total_Decision_Matrix_PasAtChosen_Agent_Total.png"
#            title = "All Participants"
#        else: 
#            filename = "Total_Weighted_Decision_Matrix_PasAtChosen_Agent_Total.png"
#            title = "All Participants"  + " Weight: " + str(self.weight)
#
# 
#        sum_actAvatAtChos = matrix[0][0].sum() + matrix[0][1].sum() + matrix[0][2].sum() +  matrix[0][3].sum() + matrix[0][4].sum()
#        sum_actAvatAtChosPasAvatAtNotChos = matrix[1][0].sum() + matrix[1][1].sum() + matrix[1][2].sum() +  matrix[1][3].sum() + matrix[1][4].sum()
#        sum_actAvatAtBoth = matrix[2][0].sum() + matrix[2][1].sum() + matrix[2][2].sum() +  matrix[2][3].sum() + matrix[2][4].sum()
#        
#        sum_pasAvatAtChos = matrix[3][0].sum() + matrix[3][1].sum() + matrix[3][2].sum() +  matrix[3][3].sum() + matrix[3][4].sum()
#        sum_pasAvatAtChosActAvatAtNotChos = matrix[4][0].sum() + matrix[4][1].sum() + matrix[4][2].sum() +  matrix[4][3].sum() + matrix[4][4].sum()
#        sum_pasAvatAtBoth = matrix[5][0].sum() + matrix[5][1].sum() + matrix[5][2].sum() +  matrix[5][3].sum() + matrix[5][4].sum()
#        
#        sum_actAtNotChosen = matrix[6][0].sum() + matrix[6][1].sum() + matrix[6][2].sum() +  matrix[6][3].sum() + matrix[6][4].sum()
#        sum_pasAtNotChosen = matrix[7][0].sum() + matrix[7][1].sum() + matrix[7][2].sum() +  matrix[7][3].sum() + matrix[7][4].sum()
#        sum_NoavatAtBoth = matrix[8][0].sum() + matrix[8][1].sum() + matrix[8][2].sum() +  matrix[8][3].sum() + matrix[8][4].sum() 
#        
#        sum_Total = (sum_actAvatAtChos + sum_actAvatAtChosPasAvatAtNotChos + sum_actAvatAtBoth + sum_pasAvatAtChos + 
#            sum_pasAvatAtChosActAvatAtNotChos + sum_pasAvatAtBoth + sum_actAtNotChosen + sum_pasAtNotChosen + sum_NoavatAtBoth)
##
#        perc_pasAvatAtChos = round((sum_pasAvatAtChos/sum_Total), 2)
#        perc_pasAvatAtChosPasAvatAtNotChos = round((sum_pasAvatAtChosActAvatAtNotChos/sum_Total), 2)
#        perc_pasAvatAtBoth = round((sum_pasAvatAtBoth/sum_Total), 2)
#
#        diagonal_lines = [
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.733, 'y1': 1, 'x0': 0, 'x1': 0.168},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.733, 'y1': 1, 'x0': 0.208, 'x1': 0.376},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.733, 'y1': 1, 'x0': 0.417, 'x1': 0.584},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.733, 'y1': 1, 'x0': 0.624, 'x1': 0.792},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.733, 'y1': 1, 'x0': 0.832, 'x1': 1},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.368, 'y1': 0.635, 'x0': 0, 'x1': 0.168},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.368, 'y1': 0.635, 'x0': 0.208, 'x1': 0.376},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.368, 'y1': 0.635, 'x0': 0.417, 'x1': 0.584},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.368, 'y1': 0.635, 'x0': 0.624, 'x1': 0.792},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.368, 'y1': 0.635, 'x0': 0.832, 'x1': 1},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.0, 'y1': 0.267, 'x0': 0, 'x1': 0.168},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.0, 'y1': 0.267, 'x0': 0.208, 'x1': 0.376},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.0, 'y1': 0.267, 'x0': 0.417, 'x1': 0.584},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.0, 'y1': 0.267, 'x0': 0.624, 'x1': 0.792},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.0, 'y1': 0.267, 'x0': 0.832, 'x1': 1},
#            ]  
#
#        fig = make_subplots(
#            rows=3, 
#            cols=5, 
#            subplot_titles=("Pas Agent at Chosen (" + str(perc_pasAvatAtChos) + "): <br>" + "Session 1:" , "Session 2: ", "Session 3","Session 4", "Session 5",
#                            "Pas Agent at Chosen, Act Agent at not Chosen (" + str(perc_pasAvatAtChosPasAvatAtNotChos) + "): <br>Session 1", "Session 2", "Session 3", "Session 4", "Session 5",
#                            "Pas Agent at Both (" + str(perc_pasAvatAtBoth) + "):<br>Session 1", "Session 2", "Session 3", "Session 4", "Session 5"), 
#            x_title="Number of previous visits not chosen nodes", 
#            y_title="Number of previous visits chosen node",
#            vertical_spacing = 0.1
#            )
#
#        fig.update_layout(margin=dict(t=200))
#        for i in range(3, 6):
#            for session in sessions:
#                if len(matrix[i][session-1]) > 0:
#                    count_cons, count_expl, count_total = Matrix.getStrategyCounts(matrix[i][session-1])
#                    if count_cons > 0:
#                        perc_cons = round((count_cons/count_total), 2)
#                    else:
#                        perc_cons = 0.00
#                    if count_expl > 0:
#                        perc_expl = round((count_expl/count_total),2)
#                    else:
#                        perc_expl = 0.00
#
#                    matrix_text = np.array(np.array(matrix[i][session-1],dtype='int'),dtype='str')
#                    matrix_text[matrix_text == '0'] = ""
#                    colorscale = "Sunset"
#                    fig.add_trace(go.Heatmap(z=matrix[i][session-1], text=matrix_text, texttemplate="%{text}", textfont={"size":12}, colorscale = colorscale,), 
#                        row=i-2, col=session)
#                    fig.update_traces(showscale=False)
#                    fig.add_annotation(text = "Expl: " + str(count_expl) + " " + "(" + str(perc_expl) + ")"
#                            "<br>Cons: " + str(count_cons) + " " + "(" + str(perc_cons) + ")",
#                        showarrow=False,
#                        bordercolor='black',
#                        borderwidth=1,
#                        x = 0, y = 1,
#                        xanchor= 'left', yanchor='top',
#                        xref = 'x domain', yref = 'y domain',
#                        align="left",
#                        name="Strategy Counts", row=i-2, col = session)
#
#        fig.update_layout(
#                    title_text=title,
#                    boxmode='group',
#                    width=2000,
#                    height=1500,
#                    shapes=diagonal_lines,
#                    font=dict(
#                        size=18,
#                        )
#                )
#        fig.write_image((self.savepath + filename))
    def plotTotal(self, matrix, sessions = (1,2,3,4,5), weights_adjusted = False):
        #save_path = "E:/HumanA/Analysis/StrategyMatrices/"
        #if experiment == 1:
        #    save_path = save_path + "Exp1/Dec_Expl_Matrix/"
        #elif experiment == 2:
        #    save_path = save_path + "Exp2/Dec_Expl_Matrix/"


        if not weights_adjusted:
            filename = str(self.participantId) + "_Decision_Matrix_Avatars_Total.png"
            title = "Participant: " + str(self.participantId)
        else: 
            filename = str(self.participantId) + "_Weighted_Decision_Matrix_Avatars_Total.png"
            title = "Participant: " + str(self.participantId)  + " Weight: " + str(self.weight)
 

        #total_decisions = "Total Decisions Agent Seeking: " + str(count_seeking) + " | Total Decisions Agent Avoiding: " + str(count_avoiding)
        #title = "Participant: " + str(self.participantId)  + str(self.weight) #"<br>" #+ total_decisions

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
                    count_cons, count_expl, count_total = Matrix.getStrategyCounts(matrix[i][session-1])
                    perc_cons = round((count_cons/count_total), 2)
                    perc_expl = round((count_expl/count_total),2)

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
        fig.write_image((self.savepath + filename))
        
        
    def plotSession(self, matrix, sessions = (1,2,3,4,5), weights_adjusted = False):
        #save_path = "E:/HumanA/Analysis/StrategyMatrices/"
        #if experiment == 1:
        #    save_path = save_path + "Exp1/Dec_Expl_Matrix/"
        #elif experiment == 2:
        #    save_path = save_path + "Exp2/Dec_Expl_Matrix/"

        #if participant != None:
        if not weights_adjusted:
            filename = str(self.participantId) + "_Decision_Matrix_Avatars_Session" +  ".png"
            title = "Participant: " + str(self.participantId)
        else:
            filename = str(self.participantId) + "_Weighted_Decision_Matrix_Avatars_Session" +  ".png"
            title = "Participant: " + str(self.participantId) + " Weight: " + str(self.weight)
        #else:
        #    nr_participants = len(participants)
        #    filename = "AllParticipants_Decision_Matrix_Avatars_Session" + ".png"
        #    participant = 'All Participants (n = ' + str(nr_participants) + ")"


        #title = "Participant: " + str(self.participantId) + weights_adjusted 

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
        #session_decisions = []
        #for i in range(5):
            #decision_text_sessions = "Agent Seeking: " + str(count_seeking[i]) + " | Agent Avoiding: " + str(count_avoiding[i]) + "<br><br>"
            #session_decisions.append(decision_text_sessions)

        fig = make_subplots(
            rows=4, 
            cols=5, 
            subplot_titles=("Agent at Chosen Direction (" + str(perc_avatAtChos) + "): <br>" + "Session 1:" ,"Session 2: ", 
                "Session 3","Session 4", "Session 5",
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
                    count_cons, count_expl, count_total = Matrix.getStrategyCounts(matrix[i][session-1])
                    perc_cons = round((count_cons/count_total), 2)
                    perc_expl = round((count_expl/count_total),2)

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
        
#    def plotNoAgentAtChosen(self, matrix, sessions = (1,2,3,4,5), weights_adjusted = False):
#        if not weights_adjusted:
#            filename = "Total_Decision_Matrix_NoAtChosen_Agent_Total.png"
#            title = "All Participants"
#        else: 
#            filename = "Total_Weighted_Decision_Matrix_NoAtChosen_Agent_Total.png"
#            title = "All Participants"  + " Weight: " + str(self.weight)
#
#
#        sum_actAvatAtChos = matrix[0][0].sum() + matrix[0][1].sum() + matrix[0][2].sum() +  matrix[0][3].sum() + matrix[0][4].sum()
#        sum_actAvatAtChosPasAvatAtNotChos = matrix[1][0].sum() + matrix[1][1].sum() + matrix[1][2].sum() +  matrix[1][3].sum() + matrix[1][4].sum()
#        sum_actAvatAtBoth = matrix[2][0].sum() + matrix[2][1].sum() + matrix[2][2].sum() +  matrix[2][3].sum() + matrix[2][4].sum()
#        
#        sum_pasAvatAtChos = matrix[3][0].sum() + matrix[3][1].sum() + matrix[3][2].sum() +  matrix[3][3].sum() + matrix[3][4].sum()
#        sum_pasAvatAtChosActAvatAtNotChos = matrix[4][0].sum() + matrix[4][1].sum() + matrix[4][2].sum() +  matrix[4][3].sum() + matrix[4][4].sum()
#        sum_pasAvatAtBoth = matrix[5][0].sum() + matrix[5][1].sum() + matrix[5][2].sum() +  matrix[5][3].sum() + matrix[5][4].sum()
#        
#        sum_actAtNotChosen = matrix[6][0].sum() + matrix[6][1].sum() + matrix[6][2].sum() +  matrix[6][3].sum() + matrix[6][4].sum()
#        sum_pasAtNotChosen = matrix[7][0].sum() + matrix[7][1].sum() + matrix[7][2].sum() +  matrix[7][3].sum() + matrix[7][4].sum()
#        sum_NoavatAtBoth = matrix[8][0].sum() + matrix[8][1].sum() + matrix[8][2].sum() +  matrix[8][3].sum() + matrix[8][4].sum() 
#        
#        sum_Total = (sum_actAvatAtChos + sum_actAvatAtChosPasAvatAtNotChos + sum_actAvatAtBoth + sum_pasAvatAtChos + 
#            sum_pasAvatAtChosActAvatAtNotChos + sum_pasAvatAtBoth + sum_actAtNotChosen + sum_pasAtNotChosen + sum_NoavatAtBoth)
##
#        perc_NoAvatAtChosActAvatAtNotChos = round((sum_actAtNotChosen/sum_Total), 2)
#        perc_NoAvatAtChosPasAvatAtNotChos = round((sum_pasAtNotChosen/sum_Total), 2)
#        perc_NoAvatAtBoth = round((sum_NoavatAtBoth/sum_Total), 2)
#
#        diagonal_lines = [
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.733, 'y1': 1, 'x0': 0, 'x1': 0.168},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.733, 'y1': 1, 'x0': 0.208, 'x1': 0.376},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.733, 'y1': 1, 'x0': 0.417, 'x1': 0.584},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.733, 'y1': 1, 'x0': 0.624, 'x1': 0.792},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.733, 'y1': 1, 'x0': 0.832, 'x1': 1},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.368, 'y1': 0.635, 'x0': 0, 'x1': 0.168},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.368, 'y1': 0.635, 'x0': 0.208, 'x1': 0.376},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.368, 'y1': 0.635, 'x0': 0.417, 'x1': 0.584},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.368, 'y1': 0.635, 'x0': 0.624, 'x1': 0.792},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.368, 'y1': 0.635, 'x0': 0.832, 'x1': 1},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.0, 'y1': 0.267, 'x0': 0, 'x1': 0.168},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.0, 'y1': 0.267, 'x0': 0.208, 'x1': 0.376},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.0, 'y1': 0.267, 'x0': 0.417, 'x1': 0.584},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.0, 'y1': 0.267, 'x0': 0.624, 'x1': 0.792},
#            {'type': 'line', 'line': { 'color': 'red', 'width': 1 },'yref': 'paper', 'xref': 'paper', 'y0': 0.0, 'y1': 0.267, 'x0': 0.832, 'x1': 1},
#            ]  
#
#        fig = make_subplots(
#            rows=3, 
#            cols=5, 
#            subplot_titles=("No Agent at Chosen, Act Agent at not Chosen (" + str(perc_NoAvatAtChosActAvatAtNotChos) + "): <br>" + "Session 1:" , "Session 2: ", "Session 3","Session 4", "Session 5",
#                            "No Agent at Chosen, Pas Agent at not Chosen (" + str(perc_NoAvatAtChosPasAvatAtNotChos) + "): <br>Session 1", "Session 2", "Session 3", "Session 4", "Session 5",
#                            "No Agent at Both (" + str(perc_NoAvatAtBoth) + "):<br>Session 1", "Session 2", "Session 3", "Session 4", "Session 5"), 
#            x_title="Number of previous visits not chosen nodes", 
#            y_title="Number of previous visits chosen node",
#            vertical_spacing = 0.1
#            )
#
#        fig.update_layout(margin=dict(t=200))
#        for i in range(6, 9):
#            for session in sessions:
#                if len(matrix[i][session-1]) > 0:
#                    count_cons, count_expl, count_total = Matrix.getStrategyCounts(matrix[i][session-1])
#                    if count_cons > 0:
#                        perc_cons = round((count_cons/count_total), 2)
#                    else:
#                        perc_cons = 0.00
#                    if count_expl > 0:
#                        perc_expl = round((count_expl/count_total),2)
#                    else:
#                        perc_expl = 0.00
#
#                    matrix_text = np.array(np.array(matrix[i][session-1],dtype='int'),dtype='str')
#                    matrix_text[matrix_text == '0'] = ""
#                    colorscale = "Sunset"
#                    fig.add_trace(go.Heatmap(z=matrix[i][session-1], text=matrix_text, texttemplate="%{text}", textfont={"size":12}, colorscale = colorscale,), 
#                        row=i-5, col=session)
#                    fig.update_traces(showscale=False)
#                    fig.add_annotation(text = "Expl: " + str(count_expl) + " " + "(" + str(perc_expl) + ")"
#                            "<br>Cons: " + str(count_cons) + " " + "(" + str(perc_cons) + ")",
#                        showarrow=False,
#                        bordercolor='black',
#                        borderwidth=1,
#                        x = 0, y = 1,
#                        xanchor= 'left', yanchor='top',
#                        xref = 'x domain', yref = 'y domain',
#                        align="left",
#                        name="Strategy Counts", row=i-5, col = session)
#
#        fig.update_layout(
#                    title_text=title,
#                    boxmode='group',
#                    width=2000,
#                    height=1500,
#                    shapes=diagonal_lines,
#                    font=dict(
#                        size=18,
#                        )
#                )
#        fig.write_image((self.savepath + filename))


    #def plotMatrix(self):
    #    if self.weight == 0:
    #        self.plotAgentAtChosen(self.totalMatrix)
    #        print('ActAgent plotted')
    #        #self.plotPasAgentAtChosen(self.totalMatrix)
    #        #print('PasAgent plotted')
    #        self.plotNoAgentAtChosen(self.totalMatrix)
    #        print('NoAgent plotted')

    #    else:
    #        self.plotTotal(self.totalMatrix, True)
            
    def plotMatrix(self):
        if self.weight == 0:
            self.plotTotal(self.matrix_total,self.sessions)
            self.plotSession(self.matrix_perSession,self.sessions,)
        else:
            self.plotTotal(self.matrix_total,self.sessions, True)
            self.plotSession(self.matrix_perSession,self.sessions,True)




