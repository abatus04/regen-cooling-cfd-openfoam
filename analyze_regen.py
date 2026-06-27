import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ─── Load data ────────────────────────────────────────────────────────────────
fluid_wall  = pd.read_csv('/home/shoyo/regenCooling/postProcessing/sampleDict/fluid/5/wallProfile_T_p_U.csv')
solid_wall  = pd.read_csv('/home/shoyo/regenCooling/postProcessing/sampleDict/innerWall/5/wallProfile_T_p.csv')
coolant_cl  = pd.read_csv('/home/shoyo/regenCooling/postProcessing/sampleDict/fluid/5/coolantCenterline_T_p_U.csv')
near_wall   = pd.read_csv('/home/shoyo/regenCooling/postProcessing/sampleDict/fluid/5/nearWallLine_T_p_U.csv')

y_fluid = fluid_wall['y'].values * 1000
T_fluid = fluid_wall['T'].values
y_solid = solid_wall['y'].values * 1000
T_solid = solid_wall['T'].values
x_cl    = coolant_cl['x'].values * 1000
T_cl    = coolant_cl['T'].values
p_cl    = coolant_cl['p'].values / 1000
x_nw    = near_wall['x'].values * 1000
T_nw    = near_wall['T'].values

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Regenerative Cooling Channel — CFD Results', fontsize=14, fontweight='bold')

# ─── Plot 1: Wall temperature profile ────────────────────────────────────────
axes[0,0].plot(T_fluid, y_fluid, 'b-', linewidth=2, label='Coolant (fluid)')
axes[0,0].plot(T_solid, y_solid, 'r-', linewidth=2, label='Copper wall (solid)')
axes[0,0].axhline(y=1.0, color='gray', linestyle='--', alpha=0.5)
axes[0,0].axhline(y=4.0, color='gray', linestyle='--', alpha=0.5)
axes[0,0].set_xlabel('Temperature (K)')
axes[0,0].set_ylabel('y position (mm)')
axes[0,0].set_title('Wall Temperature Profile (x=50mm)')
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3)
axes[0,0].text(350, 0.5, 'Outer Wall', fontsize=7, color='gray')
axes[0,0].text(350, 2.5, 'Coolant', fontsize=7, color='blue')
axes[0,0].text(350, 4.8, 'Inner Wall', fontsize=7, color='red')

# ─── Plot 2: Full wall stack ──────────────────────────────────────────────────
y_all   = np.concatenate([y_fluid, y_solid])
T_all   = np.concatenate([T_fluid, T_solid])
sort_idx = np.argsort(y_all)
axes[0,1].plot(T_all[sort_idx], y_all[sort_idx], 'r-', linewidth=2)
axes[0,1].axhline(y=1.0, color='gray', linestyle='--', alpha=0.5)
axes[0,1].axhline(y=4.0, color='gray', linestyle='--', alpha=0.5)
axes[0,1].axvspan(200, 450, alpha=0.1, color='blue', label='Coolant zone')
axes[0,1].axvspan(450, 1600, alpha=0.1, color='red', label='Copper zone')
axes[0,1].set_xlabel('Temperature (K)')
axes[0,1].set_ylabel('y position (mm)')
axes[0,1].set_title('Temperature Through Full Wall Stack')
axes[0,1].legend(fontsize=8)
axes[0,1].grid(True, alpha=0.3)
axes[0,1].text(750, 2.5, f'ΔT wall = {T_solid.max()-T_fluid.min():.0f} K',
               fontsize=10, ha='center',
               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

# ─── Plot 3: Near-wall coolant temperature along channel ──────────────────────
# smooth with rolling average to remove noise
T_nw_smooth = pd.Series(T_nw).rolling(window=10, center=True).mean().values
axes[1,0].plot(x_nw, T_nw, 'b-', alpha=0.3, linewidth=1, label='Raw')
axes[1,0].plot(x_nw, T_nw_smooth, 'b-', linewidth=2.5, label='Smoothed')
axes[1,0].set_xlabel('Axial position (mm)')
axes[1,0].set_ylabel('Temperature (K)')
axes[1,0].set_title('Near-Wall Coolant Temperature\nalong channel (y = 3.95mm)')
axes[1,0].legend()
axes[1,0].grid(True, alpha=0.3)
T_nw_valid = T_nw_smooth[~np.isnan(T_nw_smooth)]
axes[1,0].annotate(f'Max near-wall T = {np.nanmax(T_nw):.0f} K',
                   xy=(x_nw[np.argmax(T_nw)], np.nanmax(T_nw)),
                   xytext=(50, np.nanmax(T_nw)+100),
                   fontsize=9,
                   arrowprops=dict(arrowstyle='->', color='blue'))

# ─── Plot 4: Pressure drop ────────────────────────────────────────────────────
axes[1,1].plot(x_cl, p_cl, 'g-', linewidth=2)
axes[1,1].set_xlabel('Axial position (mm)')
axes[1,1].set_ylabel('Pressure (kPa)')
axes[1,1].set_title('Pressure Drop along Coolant Channel')
axes[1,1].grid(True, alpha=0.3)
dp = p_cl[0] - p_cl[-1]
axes[1,1].annotate(f'ΔP = {dp:.1f} kPa',
                   xy=(50, (p_cl[0]+p_cl[-1])/2),
                   fontsize=11, ha='center',
                   bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))

plt.tight_layout()
plt.savefig('/home/shoyo/regenCooling/results/regen_analysis.png', dpi=150, bbox_inches='tight')
plt.show()

# ─── Metrics ─────────────────────────────────────────────────────────────────
rho  = 998.0
mu   = 1e-3
Cp   = 4182.0
k    = 0.6
U_avg = coolant_cl['U_0'].mean()
D_h  = 2 * 0.002 * 0.003 / (0.002 + 0.003)
Re   = rho * U_avg * D_h / mu
Pr   = mu * Cp / k
Nu_DB = 0.023 * Re**0.8 * Pr**0.4

print("\n── Regenerative Cooling Results ─────────────────────")
print(f"Hot gas wall temperature:     {T_solid.max():.1f} K")
print(f"Peak near-wall coolant T:     {np.nanmax(T_nw):.1f} K")
print(f"Wall temperature drop (ΔT):   {T_solid.max()-T_fluid.min():.0f} K")
print(f"Pressure drop:                {dp:.1f} kPa")
print(f"Reynolds number:              {Re:.0f}")
print(f"Prandtl number:               {Pr:.2f}")
print(f"Nusselt (Dittus-Boelter):     {Nu_DB:.1f}")
print(f"Flow regime:                  {'Turbulent' if Re > 4000 else 'Laminar'}")
print(f"─────────────────────────────────────────────────────")
