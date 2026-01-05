import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from dataclasses import dataclass 
from typing import Tuple
from EIA_connector import EIAClient

@dataclass
class CalibrationResult:
        """
        Structure de données pour stocker les paramètres calibrés du modèle Ornstein-Uhlenbeck.
        """
        current_price : float # P0 (starting price)
        theta: float # Mean-reversion speed 
        mu : float # Long-term mean
        sigma : float # Vol
        dt : float = 1/252 # market open days
    
    
class OUCalibrator:
    """
    Calibre le modèle OU sur les données officielles de l'EIA (Henry Hub).
    """
        
        
