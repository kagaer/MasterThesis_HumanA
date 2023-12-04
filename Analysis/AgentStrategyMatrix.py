import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go

class StrategyMatrix():
    """Class for constructing a Strategy for a single participant"""

    def __init__(self, participantId, cursor, savepath = 'E:/HumanA/Default/'):
        self.participantId = participantId
        self.savepath = savepath
        self.cr = cursor
        self.visits_node_total = [0]*(158 + 1)
        self.visits_node_currentSes = [0]*(158 + 1)
        self.matrix_total = [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]
        self.matrix_perSession = [np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0)), np.zeros((0,0))]
        self.max_visits_total_participant = 0