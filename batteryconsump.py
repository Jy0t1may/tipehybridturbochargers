import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Paramètres
J = 0.002
k_comp = 1.2e-8
tau_exh_max = 5.0
tau_elec_max = 8.0
target_rpm = 69000
target_omega = target_rpm * (2 * np.pi / 60)

# Variables globales pour traquer la puissance de la batterie
time_history = []
power_history = []

def hybrid_turbo_with_power(t, state):
    omega = state[0]
    
    if t > 0.5:
        t_exh = tau_exh_max * (1 - np.exp(-(t - 0.5) / 0.8))
    else:
        t_exh = 0.0
        
    t_comp = k_comp * (omega ** 2)
    
    # LA LOGIQUE MGU-H (Le Cut-off et la Récupération)
    if t > 0.5 and omega < target_omega:
        t_elec = tau_elec_max # 1. MODE MOTEUR : On vide la batterie pour tuer le lag
    elif omega >= target_omega:
        # 2. CUT-OFF & MODE GÉNÉRATEUR : On freine le turbo pour le bloquer à 69k
        t_elec = t_comp - t_exh # Devient négatif (freinage magnétique)
    else:
        t_elec = 0.0
        
    # Calcul de la puissance électrique (P = C * w). 
    # Divisé par 1000 pour avoir des Kilowatts (kW)
    power_kw = (t_elec * omega) / 1000 
    
    # Enregistrement pour le graphique
    time_history.append(t)
    power_history.append(power_kw)
    
    return [(t_exh + t_elec - t_comp) / J]

# --- Simulation ---
t_span = (0, 5)
t_eval = np.linspace(0, 5, 1000)
sol_hybrid = solve_ivp(hybrid_turbo_with_power, t_span, [0], t_eval=t_eval, max_step=0.01)

# Traitement des données de puissance (nettoyage des doublons du solveur)
# On interpole pour que ça corresponde exactement à t_eval
from scipy.interpolate import interp1d
power_interp = interp1d(time_history, power_history, fill_value="extrapolate")
power_kw_array = power_interp(t_eval)

# --- Graphique de la Batterie ---
plt.style.use('default')
plt.figure(figsize=(10, 4))

# Zone rouge (Dépense) et Zone verte (Recharge)
plt.plot(t_eval, power_kw_array, color='blue', linewidth=2, label="Flux d'énergie de la Batterie")
plt.axhline(y=0, color='black', linestyle='-')
plt.fill_between(t_eval, 0, power_kw_array, where=(power_kw_array > 0), facecolor='red', alpha=0.3, label="Moteur (Décharge Batterie)")
plt.fill_between(t_eval, 0, power_kw_array, where=(power_kw_array < 0), facecolor='green', alpha=0.3, label="Générateur (Recharge Batterie)")

plt.axvline(x=0.5, color='gray', linestyle='--')
plt.title("Gestion de la Batterie : Cut-off et Récupération d'énergie", fontsize=12)
plt.ylabel("Puissance (kW)")
plt.xlabel("Temps (secondes)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()