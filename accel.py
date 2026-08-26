import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# ==========================================
# 1. PARAMÈTRES PHYSIQUES
# ==========================================
J = 0.002               # Inertie de l'axe du turbo (kg.m^2)
k_comp = 1.2e-8         # Coefficient de traînée du compresseur
tau_exh_max = 5.0       # Couple max des gaz d'échappement (Nm)
tau_elec_max = 8.0      # Couple max du moteur électrique (Nm)

target_rpm = 69000      # Limite de vitesse du turbo
target_omega = target_rpm * (2 * np.pi / 60) # Conversion en rad/s

# ==========================================
# 2. MODÈLES PHYSIQUES (Résolution ODE pour les RPM)
# ==========================================
def standard_turbo(t, state):
    """Simule le turbo classique avec le rebond de la wastegate"""
    omega = state[0]
    if t > 0.5:
        # Les gaz d'échappement montent lentement (Lag)
        t_exh = tau_exh_max * (1 - np.exp(-(t - 0.5) / 1.5))
    else:
        t_exh = 0.0
        
    # Rebond mécanique (Hystérésis) si on dépasse 69k
    if omega > target_omega:
        t_exh = t_exh * 0.3 
        
    t_comp = k_comp * (omega ** 2)
    return [(t_exh - t_comp) / J]

def hybrid_turbo(t, state):
    """Simule l'e-Turbo avec précision numérique (MGU-H)"""
    omega = state[0]
    if t > 0.5:
        t_exh = tau_exh_max * (1 - np.exp(-(t - 0.5) / 1.5))
    else:
        t_exh = 0.0
    
    t_comp = k_comp * (omega ** 2)
    
    # Logique de contrôle électrique
    if t > 0.5 and omega < target_omega:
        t_elec = tau_elec_max # Boost électrique instantané
    elif omega >= target_omega:
        t_elec = t_comp - t_exh # Régulation parfaite (Freinage/Générateur)
    else:
        t_elec = 0.0
        
    return [(t_exh + t_elec - t_comp) / J]

# --- Exécution de la simulation sur 10 secondes ---
t_span = (0, 10)
t_eval = np.linspace(0, 10, 1000)

# max_step=0.01 est crucial pour capter le rebond mécanique
sol_standard = solve_ivp(standard_turbo, t_span, [0], t_eval=t_eval, max_step=0.01)
sol_hybrid = solve_ivp(hybrid_turbo, t_span, [0], t_eval=t_eval, max_step=0.01)

rpm_standard = sol_standard.y[0] * (60 / (2 * np.pi))
rpm_hybrid = sol_hybrid.y[0] * (60 / (2 * np.pi))


# ==========================================
# 3. MODÈLE DE CONSOMMATION D'ESSENCE (Inspiré du croquis)
# ==========================================    
fuel_standard = np.zeros_like(t_eval)
fuel_electric = np.zeros_like(t_eval)

for i, t in enumerate(t_eval):
    if t > 0.5: # Début de l'accélération
        # Standard : Monte haut (pour combattre le lag)
        fuel_standard[i] = 10 * (1 - np.exp(-(t - 0.5) / 2.0))
        # Si le turbo classique oscille, l'injection oscille aussi
        if rpm_standard[i] >= target_rpm * 0.98:
            fuel_standard[i] += 0.3 * np.sin(15 * t)
            
        # Hybride : Monte doucement à un niveau plus bas
        fuel_electric[i] = 6.5 * (1 - np.exp(-(t - 0.5) / 2.5))


# ==========================================
# 4. GÉNÉRATION DES DEUX GRAPHIQUES SUPERPOSÉS
# ==========================================
plt.style.use('default')
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# Graphique 1 : Vitesse du Turbo (Performance)
ax1.plot(t_eval, rpm_standard, color='red', linewidth=2, label='Turbo Classique (Wastegate)')
ax1.plot(t_eval, rpm_hybrid, color='green', linewidth=2, label='e-Turbo Assisté')
ax1.axhline(y=target_rpm, color='orange', linestyle='--', label='Cible (69 000 RPM)')
ax1.axvline(x=0.5, color='gray', linestyle='--')
ax1.set_title("Dynamique du Turbo : Suppression du Lag et de l'Oscillation", fontsize=12, fontweight='bold')
ax1.set_ylabel("Vitesse (RPM)")
ax1.set_ylim(0, 85000)
ax1.grid(True, alpha=0.3)
ax1.legend(loc='lower right')

# Graphique 2 : Consommation d'essence (Sobriété)
ax2.plot(t_eval, fuel_standard, color='red', linewidth=2.5, label='Sans Aide (Gaspillage)')
ax2.plot(t_eval, fuel_electric, color='green', linewidth=2.5, label='Aide Électrique (Optimisé)')
ax2.axvline(x=0.5, color='gray', linestyle='--')
ax2.set_title("Débit de Carburant (Comparaison de Sobriété)", fontsize=12, fontweight='bold')
ax2.set_xlabel("Temps (secondes)", fontsize=11)
ax2.set_ylabel("Débit d'essence injecté", fontsize=11)
ax2.set_ylim(0, 12)
ax2.grid(True, alpha=0.3)
ax2.legend(loc='lower right')

# Affichage propre
plt.tight_layout()
plt.show()
