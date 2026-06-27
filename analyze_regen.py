import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ─── Load data ────────────────────────────────────────────────────────────────
fluid_wall    = pd.read_csv('/home/shoyo/regenCooling/postProcessing/sampleDict/fluid/0.5/wallProfile_T_p_U.csv')
solid_wall    = pd.read_csv('/home/shoyo/regenCooling/postProcessing/sampleDict/innerWall/0.5/wallProfile_T_p.csv')
coolant_cl    = pd.read_csv('/home/shoyo/regenCooling/postProcessing/sampleDict/fluid/0.5/coolantCenterline_T_p_U.csv')

# ─── Plot 1: Temperature profile through wall thickness ───────────────────────
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle('Regenerative Cooling Channel — CFD Results', fontsize=13, fontweight='bold')

# Combine fluid and solid wall profiles
y_fluid = fluid_wall['y'].values * 1000       # mm
T_fluid = fluid_wall['T'].values

y_solid = solid_wall['y'].values * 1000       # mm
T_solid = solid_wall['T'].values

axes[0].plot(T_fluid, y_fluid, 'b-', linewidth=2, label='Coolant (fluid)')
axes[0].plot(T_solid, y_solid, 'r-', linewidth=2, label='Copper wall (solid)')
axes[0].axhline(y=1.0, color='gray', linestyle='--', alpha=0.5, label='Fluid-solid interface')
axes[0].axhline(y=4.0, color='gray', linestyle='--', alpha=0.5)
axes[0].set_xlabel('Temperature (K)')
axes[0].set_ylabel('y position (mm)')
axes[0].set_title('Wall Temperature Profile\n(cross-section at x=50mm)')
axes[0].legend(fontsize=8)
axes[0].grid(True, alpha=0.3)

# Annotate regions
axes[0].text(310, 0.5, 'Outer\nWall', fontsize=7, ha='center', color='gray')
axes[0].text(310, 2.5, 'Coolant\nChannel', fontsize=7, ha='center', color='blue')
axes[0].text(310, 4.8, 'Inner\nWall', fontsize=7, ha='center', color='red')

# ─── Plot 2: Coolant temperature rise along channel ───────────────────────────
x_cl = coolant_cl['x'].values * 1000         # mm
T_cl = coolant_cl['T'].values
p_cl = coolant_cl['p'].values / 1000         # kPa
U_cl = coolant_cl['U_0'].values              # axial velocity

axes[1].plot(x_cl, T_cl, 'b-', linewidth=2)
axes[1].set_xlabel('Axial position (mm)')
axes[1].set_ylabel('Temperature (K)')
axes[1].set_title('Coolant Temperature Rise\nalong channel centerline')
axes[1].grid(True, alpha=0.3)

# Annotate inlet/outlet
T_rise = T_cl[-1] - T_cl[0]
axes[1].annotate(f'ΔT = {T_rise:.1f} K',
                xy=(50, (T_cl[0]+T_cl[-1])/2),
                fontsize=10, color='blue',
                ha='center',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))

# ─── Plot 3: Pressure drop along channel ─────────────────────────────────────
axes[2].plot(x_cl, p_cl, 'g-', linewidth=2)
axes[2].set_xlabel('Axial position (mm)')
axes[2].set_ylabel('Pressure (kPa)')
axes[2].set_title('Pressure Drop\nalong coolant channel')
axes[2].grid(True, alpha=0.3)

dp = p_cl[0] - p_cl[-1]
axes[2].annotate(f'ΔP = {dp:.1f} kPa',
                xy=(50, (p_cl[0]+p_cl[-1])/2),
                fontsize=10, color='green',
                ha='center',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))

plt.tight_layout()
plt.savefig('/home/shoyo/regenCooling/results/regen_analysis.png', dpi=150, bbox_inches='tight')
plt.show()

# ─── Engineering metrics ──────────────────────────────────────────────────────
print("\n── Regenerative Cooling Results ─────────────────────")
print(f"Hot gas wall temperature:     {T_solid.max():.1f} K")
print(f"Coolant inlet temperature:    {T_cl[0]:.1f} K")
print(f"Coolant outlet temperature:   {T_cl[-1]:.1f} K")
print(f"Coolant temperature rise:     {T_rise:.1f} K")
print(f"Pressure drop:                {dp:.1f} kPa")
print(f"Peak wall temp (inner wall):  {T_solid.max():.1f} K")
print(f"Min wall temp (fluid side):   {T_fluid.min():.1f} K")

# Dittus-Boelter validation
rho   = 998.0    # kg/m3 water
mu    = 1e-3     # Pa.s
Cp    = 4182.0   # J/kg.K
k     = 0.6      # W/m.K water
U_avg = np.mean(U_cl)
D_h   = 2 * 0.002 * 0.003 / (0.002 + 0.003)  # hydraulic diameter of 2x3mm channel

Re = rho * U_avg * D_h / mu
Pr = mu * Cp / k
Nu_DB = 0.023 * Re**0.8 * Pr**0.4   # Dittus-Boelter

print(f"\n── Validation vs Dittus-Boelter ────────────────────")
print(f"Reynolds number:              {Re:.0f}")
print(f"Prandtl number:               {Pr:.2f}")
print(f"Nusselt (Dittus-Boelter):     {Nu_DB:.1f}")
print(f"Flow regime:                  {'Turbulent' if Re > 4000 else 'Laminar'}")
print(f"────────────────────────────────────────────────────")
