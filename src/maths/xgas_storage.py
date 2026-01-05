# Étape 5 : La Physique du Stockage (Contraintes)
# 1. Réflexion (Le Concept)Un stockage de gaz n'est pas un compte en banque infini. 

# C'est une cavité géologique avec des contraintes d'ingénierie strictes :Volume (Space) : 
# Tu as un volume Max (V_{max}) et Min (V_{min}).
# Débit (Rate) :Tu as une vitesse d'injection (R_{in}) et de soutirage (R_{out}). 
# Tu ne peux pas remplir la cuve en une heure.
# Coût Marginal : Activer les compresseurs pour injecter coûte de l'argent (électricité/gaz).
# 
# 2. Implication (La Logique de Décision)
# À chaque jour t, étant donné un niveau de stock S_t, l'ensemble des actions possibles a est limité par la physique.
# Si S_t = V_{max}, l'action "Acheter" est interdite.L'inventaire de demain sera : 
# S_{t+1} = S_t + a (où a est positif si on injecte, négatif si on soutire).

#DONC :IL FAUT MODELISER L'ACTIF PHYSIQUEMENT PAR DES VARIABLES PHYSIQUES 

from dataclasses import dataclass
import numpy as np

@dataclass
class StorageParams:
    """Paramètres techniques d'une cavité de stockage."""
    capacity: float       # Volume total (MWh)
    inject_rate: float # Vitesse max de remplissage (MWh/jour)
    wd_rate: float # Vitesse max de vidage (MWh/jour)
    inject_cost: float # Coût variable pour injecter (€/MWh)
    wd_cost: float # Coût variable pour soutirer (€/MWh)
    min_inventory: float = 0.0 # Volume gaz coussin (optionnel sait-on jamais)
    
    
class GasStorage:
    def __init__(self, params: StorageParams):
        self.params = params
        
        
    def get_possible_actions(self, current_inventory: float) -> tuple: # type: ignore
        """
        Calcule les bornes physiques pour la décision d'aujourd'hui.
        Returns: (min_action, max_action)
        - Action > 0 : Injection (Achat)
        - Action < 0 : Soutirage (Vente)
        """
        # Combien de place il reste pour injecter ?
        space_left = self.params.capacity-current_inventory
        # On ne peut pas injecter plus que le débit max OU la place restante
        max_inj = min(self.params.inject_rate, space_left)
        # Combien de gaz peut-(on) soutirer?
        gas_available=current_inventory -  self.params.min_inventory
        # On ne peut pas retirer plus que le débit max OU le gaz dispo
        max_wd=min(self.params.wd_rate, gas_available)
        # Les bornes : on peut soutirer (-max_wd) jusqu'à injecter (+max_inj)
        return (-max_wd, max_inj)
    
    
    
    
    def calculate_CF(self, action:float, price : float) ->float:
        """
        Calcule l'argent gagné ou perdu par l'action d'injecter ou d'éjecter.
        """
        if action > 0: 
            # INJECTION : On achète du gaz + on paie le coût d'injection
            # Cashflow Négatif (Sortie d'argent)
            cost = price * action + (self.params.inject_cost * action)
            return -cost
        elif action < 0:
            # SOUTIRAGE : On vend du gaz - on paie le coût de soutirage
            # Cashflow Positif (Entrée d'argent)
            # Note: action est négative, donc abs(action) pour le volume
            volume=abs(action)
            profit = price * volume - (self.params.wd_cost * volume ) 
            return profit
        else:
            return 0.0
        
        
      
    # --- TEST DE LOGIQUE ---
if __name__ == "__main__":
        params = StorageParams(
            capacity=100_000,   # 100 GWh
            inject_rate=2000, # 50 jours pour remplir
            wd_rate=4000, # 25 jours pour vider (souvent plus rapide)
            inject_cost=1.5,
            wd_cost=0.5
            )
        storage =GasStorage(params)
        
        #cas 1:  Stockage à moitié plein

        inv = 50_000
        min_act, max_act = storage.get_possible_actions(inv)
        print(f"Niveau {inv}: Je peux vendre {abs(min_act)} ou acheter {max_act}")
        
        # Cas 2 : Stockage plein à craquer
        inv = 100_000
        min_act, max_act = storage.get_possible_actions(inv)
        print(f"Niveau {inv}: Je peux vendre {abs(min_act)} ou acheter {max_act}")
    
        # Test Cashflow : Vente de 1000 MWh à 50€
        cf = storage.calculate_CF(-1000, 50.0)
        print(f"Vente 1000 MWh @ 50€ (Coût 0.5) -> Cashflow: {cf} €")
        
        
#OUTPUTS : 

# Niveau 50000: Je peux vendre 4000 ou acheter 2000
# Niveau 100000: Je peux vendre 4000 ou acheter 0
# Vente 1000 MWh @ 50€ (Coût 0.5) -> Cashflow: 49500.0 €

#CONCLUSION : OK !!

# MAINTENANT : jour 150. Le stockage est à moitié plein. Le prix est moyen.
# comment savoir quelle décision prendre ?

# POUR CELA : LSMC :Least Squares MC method avec du backward induction:

# je ne sais pas ce que vaudra mon stock de gas de main ? si mieux de vendre ajd ou mieux de vendre demain car hausse du prix.

# stratégie : au lieu de partir du 01/01 au 31/12. Partir d'un prix au 31/12 défini et avancer dans l'autre sens jusqu'au JOUR 0 = PROG DYNAMIQUE