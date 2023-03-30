from Matrixes import *
from plotly.subplots import make_subplots
import plotly.graph_objects as go

class AgentStrategyMatrix(Matrix):
    """Class for constructing a Strategy for a single participant"""

    def __init__(self, participantId, cursor, savepath= 'E:/HumanA/Default/'):
        super().__init__(participantId, cursor, savepath)

        self.matrix_total = [[np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))],
                        [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))],
                        [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))],
                        [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]]
        self.matrix_perSession = [[np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))],
                        [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))],
                        [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))],
                        [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]]
        #self.max_visits_session_participant = 
        self.createMatrix()

    # region GETTER
    #def getCountDecisions(self, dp_ids):
    #    sql_instruction = f"""SELECT COUNT(decision) FROM participant_decision WHERE datapointId IN {dp_ids} AND decision = 'AvatarAtChosen'"""
    #    self.cr.execute(sql_instruction)
    #    count_Avatar_Seeking = self.cr.fetchone()
#
    #    sql_instruction = f"""SELECT COUNT(decision) FROM participant_decision WHERE datapointId IN {dp_ids} AND decision = 'AvatarAtNotChosen'"""
    #    self.cr.execute(sql_instruction)
    #    count_Avatar_Avoiding = self.cr.fetchone()
    #    return count_Avatar_Seeking[0], count_Avatar_Avoiding[0]
#
    #def getCountDecisionsTotal(self):
    #    sql_instruction = f"""SELECT COUNT(decision) FROM participant_decision WHERE decision = 'AvatarAtChosen'"""
    #    self.cr.execute(sql_instruction)
    #    count_Avatar_Seeking = self.cr.fetchone()
#
    #    sql_instruction = f"""SELECT COUNT(decision) FROM participant_decision WHERE decision = 'AvatarAtNotChosen'"""
    #    self.cr.execute(sql_instruction)
    #    count_Avatar_Avoiding = self.cr.fetchone()
    #    return count_Avatar_Seeking[0], count_Avatar_Avoiding[0]
#
    #def getCountDecisionsSessionTotal(self):
    #    sql_instruction = f"""SELECT COUNT(participant_decision.decision) FROM trials
    #        LEFT JOIN datapoints_analysis ON trials.id = datapoints_analysis.trialId
    #            LEFT JOIN participant_decision ON datapoints_analysis.datapointId = participant_decision.datapointId
    #            WHERE decision = 'AvatarAtChosen'
    #            GROUP BY trials.sessionNr"""
    #    self.cr.execute(sql_instruction)
    #    count_Avatar_Seeking = tuple(did[0] for did in self.cr.fetchall())
#
    #    sql_instruction = f"""SELECT COUNT(participant_decision.decision) FROM trials
    #        LEFT JOIN datapoints_analysis ON trials.id = datapoints_analysis.trialId
    #            LEFT JOIN participant_decision ON datapoints_analysis.datapointId = participant_decision.datapointId
    #            WHERE decision = 'AvatarAtNotChosen'
    #            GROUP BY trials.sessionNr"""
    #    self.cr.execute(sql_instruction)
    #    count_Avatar_Avoiding = [did[0] for did in self.cr.fetchall()]
    #    return count_Avatar_Seeking, count_Avatar_Avoiding

    def getDecisions(self, dp_id):
        sql_instruction = f"""
        SELECT participant_decision.Id, participant_decision.last_node_neighbour, participant_decision.decision
        FROM participant_decision
        WHERE participant_decision.datapointId = {dp_id}
        ;
            """
        self.cr.execute(sql_instruction)
        decisions = self.cr.fetchall()
        return decisions
    
    def getVisits(self, node):
        """get the number of visits of a node for the current session and overall

        Args:
            node (int): node for which you want to get the number of visits

        Returns:
            visits_participant_total(int): total nr of visits for current participant
            visits_participant_currentSes (int) : session nr of visits for current participant
            visits_total (int) : total nr of visits over all participants
            visits_currentSes (int) : session nr of visits over all participants 
        """
        visits_participant_total = self.visits_node_total[node]
        visits_participant_currentSes = self.visits_node_currentSes[node]

        #visits_total = self.visits_node_total[node]
        #visits_currentSes = self.visits_node_perSession[node]

        return visits_participant_total,visits_participant_currentSes #,visits_total,visits_currentSes
    # endregion GETTER

    # region ADJUST MATRIX
    def addVisitToStrategyMatrix(self, node,decisions):
        visits_cur_node_part_total,visits_cur_node_part_ses = self.getVisits(node)


        for _,neighbour,decision in decisions:
            visits_neighbour_part_total,visits_neighbour_part_ses = self.getVisits(neighbour)
            if decision == 'AvatarAtChosen':
                self.matrix_current_total[0][visits_cur_node_part_total][visits_neighbour_part_total] += 1
                self.matrix_current_Session[0][visits_cur_node_part_ses][visits_neighbour_part_ses] += 1

            elif decision == 'AvatarAtNotChosen':
                self.matrix_current_total[1][visits_cur_node_part_total][visits_neighbour_part_total] += 1
                self.matrix_current_Session[1][visits_cur_node_part_ses][visits_neighbour_part_ses] += 1
            elif decision == 'AvatarAtBoth':
                self.matrix_current_total[2][visits_cur_node_part_total][visits_neighbour_part_total] += 1
                self.matrix_current_Session[2][visits_cur_node_part_ses][visits_neighbour_part_ses] += 1
            else: 
                self.matrix_current_total[3][visits_cur_node_part_total][visits_neighbour_part_total] += 1
                self.matrix_current_Session[3][visits_cur_node_part_ses][visits_neighbour_part_ses] += 1


    def adjustVisits(self, node):
        self.visits_node_total[node] += 1
        self.visits_node_currentSes[node] += 1


    def resizeStrategyMatrixes(self, session):
        #global max_visits_total_participant
        #global max_visits_session_participant
        #global max_visits_total
        #global max_visits_sessions
        #global self.matrix_current_total
        #global self.matrix_current_Session
        #global strategy_matrix_total
        #global strategy_matrix_perSession


        if self.max_visits_total_participant < max(self.visits_node_total)+1 or (len(self.matrix_current_total[0]) == 0 
            or len(self.matrix_current_total[1]) == 0 or len(self.matrix_current_total[2]) == 0 or len(self.matrix_current_total[3]) == 0 ):
            max_visits_total_participant = max(self.visits_node_total)+1
            for i in range(len(self.matrix_current_total)):
                self.matrix_current_total[i] = Matrix.resize_matrix(self.matrix_current_total[i], max_visits_total_participant+1)

        if self.max_visits_session_participant < max(self.visits_node_currentSes)+1 or (len(self.matrix_current_Session[0]) == 0 
            or len(self.matrix_current_Session[1]) == 0 or len(self.matrix_current_Session[2]) == 0 or len(self.matrix_current_Session[3]) == 0 ):
            max_visits_session_participant = max(self.visits_node_currentSes)+1
            for i in range(len(self.matrix_current_Session)):
                self.matrix_current_Session[i] = Matrix.resize_matrix(self.matrix_current_Session[i], max_visits_session_participant+1)

        #if max_visits_total <= self.max_visits_total_participant or (len(self.matrix_total[0][session-1]) <= max_visits_total or 
        #    len(strategy_matrix_total[1][session-1]) <= max_visits_total or len(strategy_matrix_total[2][session-1]) <= max_visits_total or len(strategy_matrix_total[3][session-1]) <= max_visits_total):
        #    if max_visits_total <= max_visits_total_participant:
        #        max_visits_total = max_visits_total_participant+1
##
        #    for i in range(len(strategy_matrix_total)):
        #        strategy_matrix_total[i][session-1]  = resize_matrix(strategy_matrix_total[i][session-1] , max_visits_total+1)
#
        #if max_visits_sessions <= max_visits_session_participant or (len(strategy_matrix_perSession[0][session-1]) <= max_visits_sessions or
        #    len(strategy_matrix_perSession[1][session-1]) <= max_visits_sessions or len(strategy_matrix_perSession[2][session-1]) <= max_visits_sessions or len(strategy_matrix_perSession[3][session-1]) <= max_visits_sessions):
        #    if max_visits_sessions <= max_visits_session_participant:
        #        max_visits_sessions = max_visits_session_participant+1
        #    for i in range(len(strategy_matrix_perSession)):
        #        strategy_matrix_perSession[i][session-1]  = resize_matrix(strategy_matrix_perSession[i][session-1] , max_visits_sessions+1)
    # endregion ADJUST MATRIX
    def createMatrix(self):

       

        last_node = []
        #max_visits_total_participant = 0

        #count_dec_seeking_part = 0
        #count_dec_avoiding_part = 0
        #count_dec_seeking_ses = 5*[0]
        #count_dec_avoiding_ses = 5*[0]

        for session in self.sessions:
            #print("Participant: " + str(self.) + " | Session: " + str(session))
            self.visits_node_currentSes = [0]*(self.maxNode + 1)

            self.matrix_current_total = [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]
            self.matrix_current_Session = [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]

            self.max_visits_session_participant = 0
            trials = self.getTrialNrs(session)

            data = self.getDatapoints(trials)
            dp_ids_total = tuple([datapoint[1] for datapoint in data])
            #count_dec_seeking,count_dec_avoiding = getCountDecisions(dp_ids_total)
            #count_dec_seeking_ses[session-1] = count_dec_seeking
            #count_dec_avoiding_ses[session-1] = count_dec_avoiding
#
            #count_dec_seeking_part += count_dec_seeking
            #count_dec_avoiding_part += count_dec_avoiding


            for datapoint in data:
                trial_id, dp_id,timeStamp, node = datapoint
                if last_node != []:
                    decisions = self.getDecisions(dp_id)


                    self.resizeStrategyMatrixes(session)
                    self.addVisitToStrategyMatrix(node,decisions)
                    self.adjustVisits(node)

                last_node = node

            self.matrix_total[0][session-1] = self.matrix_current_total[0] 
            self.matrix_total[1][session-1] = self.matrix_current_total[1] 
            self.matrix_total[2][session-1] = self.matrix_current_total[2]
            self.matrix_total[3][session-1] = self.matrix_current_total[3] 

            self.matrix_perSession[0][session-1] = self.matrix_current_Session[0]
            self.matrix_perSession[1][session-1] = self.matrix_current_Session[1]
            self.matrix_perSession[2][session-1] = self.matrix_current_Session[2]
            self.matrix_perSession[3][session-1] = self.matrix_current_Session[3]


            #strategy_matrix_total[0][session-1] = addUpMatrices(strategy_matrix_total[0][session-1], self.matrix_current_total[0]) 
            #strategy_matrix_total[1][session-1] = addUpMatrices(strategy_matrix_total[1][session-1], self.matrix_current_total[1]) 
            #strategy_matrix_total[2][session-1] = addUpMatrices(strategy_matrix_total[2][session-1], self.matrix_current_total[2]) 
            #strategy_matrix_total[3][session-1] = addUpMatrices(strategy_matrix_total[3][session-1], self.matrix_current_total[3]) 
#
            #strategy_matrix_perSession[0][session-1] = addUpMatrices(strategy_matrix_perSession[0][session-1], self.matrix_current_Session[0]) 
            #strategy_matrix_perSession[1][session-1] = addUpMatrices(strategy_matrix_perSession[1][session-1], self.matrix_current_Session[1]) 
            #strategy_matrix_perSession[2][session-1] = addUpMatrices(strategy_matrix_perSession[2][session-1], self.matrix_current_Session[2]) 
            #strategy_matrix_perSession[3][session-1] = addUpMatrices(strategy_matrix_perSession[3][session-1], self.matrix_current_Session[3]) 


            #last_session = session
            #print("All visits counted")

    def plotTotal(self, matrix, sessions = (1,2,3,4,5), weights_adjusted = ''):
        #save_path = "E:/HumanA/Analysis/StrategyMatrices/"
        #if experiment == 1:
        #    save_path = save_path + "Exp1/Dec_Expl_Matrix/"
        #elif experiment == 2:
        #    save_path = save_path + "Exp2/Dec_Expl_Matrix/"


        #if participant != None:
        filename = str(self.participantId) + "_Decision_Matrix_Avatars_Total" +  ".png"
        ##else:
        #    nr_participants = len(participants)
        #    filename = "AllParticipants_Decision_Matrix_Avatars_Total" + ".png"
        #    participant = 'All Participants (n = ' + str(nr_participants) + ")" 

        #total_decisions = "Total Decisions Agent Seeking: " + str(count_seeking) + " | Total Decisions Agent Avoiding: " + str(count_avoiding)
        title = "Participant: " + str(self.participantId)  + weights_adjusted #"<br>" #+ total_decisions

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


    def plotSession(self, matrix, sessions = (1,2,3,4,5), weights_adjusted = ''):
        #save_path = "E:/HumanA/Analysis/StrategyMatrices/"
        #if experiment == 1:
        #    save_path = save_path + "Exp1/Dec_Expl_Matrix/"
        #elif experiment == 2:
        #    save_path = save_path + "Exp2/Dec_Expl_Matrix/"

        #if participant != None:
        filename = str(self.participantId) + "_Decision_Matrix_Avatars_Session" +  ".png"
        #else:
        #    nr_participants = len(participants)
        #    filename = "AllParticipants_Decision_Matrix_Avatars_Session" + ".png"
        #    participant = 'All Participants (n = ' + str(nr_participants) + ")"


        title = "Participant: " + str(self.participantId) + weights_adjusted 

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
        fig.write_image((self.savepath + filename))

    def plotMatrix(self):
        self.plotTotal(self.matrix_total,self.sessions)
        self.plotSession(self.matrix_perSession,self.sessions,)