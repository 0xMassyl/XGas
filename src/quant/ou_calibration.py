# pour simuler le temps, j par j donc discrétisation du temps obligatoire par Euler-Maruyama
#P_{t+1} = P_t + theta*(mu - P_t)* Delta_t + sigma * sqrt{Delta_t}*epsilon


# edit : dans le premier code, mu était une constante (45.0). Mais le marché du gaz ne fonctionne pas avec une moyenne fixe. 
# Les traders regardent la Forward Curve : une série de prix fixés pour le futur (ex: Janvier est à 75€, Juillet à 30€, Décembre à 80€).
# Si on reliait ces points par des segments de droite (interpolation linéaire), on aurait des "cassures" nettes à chaque point. 
# Ce n'est pas réaliste : le prix ne change pas de trajectoire brutalement le 1er du mois.
# L'interpolation cubique crée une courbe "élastique" et lisse qui passe par tes points de données.
# Cela donne à ton processus d'Ornstein-Uhlenbeck une cible mouvante mais fluide.

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

def model_xgas_advance(p0, theta, sigma, days, scenarios):
    """
    MEME CHOSE QUE ORNSTEIN UHLENBECK MAIS DU COUP MU_t varie de manière continue sans cassure donc interpolation cubique nécessaire
    """

    piliers_jours = [0, 90, 180, 270, 365]
    piliers_prix  = [80, 40, 25, 60, 80]
    # Création de la courbe lisse (Cubic Spline)
    # bc_type='periodic' assure que le début et la fin de l'année se raccordent bien
    cs = CubicSpline(piliers_jours, piliers_prix, bc_type='periodic')
    
    t_axis = np.arange(days)
    mu_t = cs(t_axis) # Notre cible mu(t) pour chaque jour

    
    dt = 1/365
    prix = np.zeros((days, scenarios))
    prix[0] = p0
    
    
    for t in range(1,days):
        prev_p=prix[t-1]
        # ICI : mu n'est plus fixe, on prend la valeur de la courbe lisse au temps t
        mu=mu_t[t]
        #force de rappel
        drift= theta * (mu - prev_p) * dt
        # Volatilité
        choc = sigma * np.sqrt(dt) * np.random.normal(0, 1, scenarios)
        prix[t]=np.maximum(prev_p+drift+choc,0.1)
        
    return prix, mu_t, piliers_jours, piliers_prix

PRIX_DEPART = 75.
VITESSE_RAPPEL = 6.0  # Force de l'élastique
VOLATILITE = 25.0 
HORIZON = 365
SIMULATIONS = 40

# --- PARAMÈTRES ---
PRIX_DEPART = 75.0 
VITESSE_RAPPEL = 6.0 
VOLATILITE = 25.0 
HORIZON = 365
SIMULATIONS = 40

# Exécution
trajectoires, cible_lisse, x_points, y_points = model_xgas_advance(
    PRIX_DEPART, VITESSE_RAPPEL, VOLATILITE, HORIZON, SIMULATIONS
)

# --- VISUALISATION ---
plt.figure(figsize=(12, 6))
plt.style.use('dark_background')
plt.plot(trajectoires, color='cyan', alpha=0.1)
plt.plot(cible_lisse, color='red', linewidth=2, label="Cible Mu(t) (Boucle Périodique)")
plt.scatter(x_points, y_points, color='yellow', zorder=5, label="Points de Marché")
plt.title("XGas : Modèle Stochastique avec Cible Périodique Lisse")
plt.ylabel("Prix Gaz (€/MWh)")
plt.xlabel("Jours")
plt.legend()
plt.grid(alpha=0.2)
plt.show()



# Ce que tu viens de construire :

# La Cible (Rouge) : C'est le "modèle de consommation/prix idéal". 
# Elle ne bouge pas, elle représente l'attente du marché. 
# L'interpolation cubique a permis de transformer 5 points isolés en une route continue.

# L'Aléatoire (Cyan) : Ce sont les 40 réalités possibles. 
# Elles essaient de suivre la route rouge, mais elles sont poussées par la volatilité.

# Le Lien : C'est le paramètre theta (Vitesse de rappel).
# Si je mets theta = 100, les lignes bleues seront presque confondues avec la ligne rouge. 
# Si je mets theta = 0.5, elles ignoreront presque la saisonnalité.

# Vers le jour 180 (l'été), le prix est très bas. 
# C'est le moment idéal pour injecter (remplir le stockage). 
# Vers le jour 365, il est haut, c'est le moment de soutirer (vendre).

# Mais, physiquement, si je décide d'injecter au jour 180, je ne peux pas remplir le réservoir de 1 million de m3 en une seconde. 
# il y a une vitesse d'injection... donc nécessité de prendre ceci en compte. 

# SAUF QUE : La contrainte physique 
# Je ne peux pas injecter tout le gaz le jour le moins cher de l'année. 
# Si le réservoir fait 100 GWh et que le compresseur ne peut injecter que 1 GWh par jour, 
# il faut 100 jours pour le remplir....... donc nécessité de prédiction.... 



