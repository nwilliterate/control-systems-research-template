"""Experiment 04 — Symbolic derivation and numerical cross-check for the pendulum.

Uses sympy to derive the linearised state-space (A, B) of a simple pendulum about
the DOWNWARD equilibrium (theta=0, the stable rest position), then cross-checks the
result against lib.systems.linearize.linearize_plant applied to a NumPy Plant
subclass of the same pendulum. Confirms that symbolic and numerical Jacobians agree
to machine precision.

State: x = [theta, theta_dot]  (theta = 0 is the downward equilibrium)
Input: u = torque [N·m]
EOM:   theta'' = -(g/L) sin(theta) - (b/(m L^2)) theta_dot + u/(m L^2)

Run in Spyder cell-by-cell or
    python -m experiments.run_04_symbolic_pendulum
from the project root. Requires sympy.
"""

# %% Imports
import numpy as np
import sympy as sp

from lib.systems.plant import Plant
from lib.systems.linearize import linearize_plant

# %% Symbolic derivation
# ---- symbols ---------------------------------------------------------------
theta, theta_dot = sp.symbols("theta theta_dot", real=True)
u_sym = sp.Symbol("u", real=True)
g_sym, L_sym, m_sym, b_sym = sp.symbols("g L m b", positive=True)

# State vector x = [theta, theta_dot]; f maps x -> xdot
f1 = theta_dot                                                        # d(theta)/dt
f2 = -(g_sym / L_sym) * sp.sin(theta) \
     - (b_sym / (m_sym * L_sym**2)) * theta_dot \
     + u_sym / (m_sym * L_sym**2)                                    # d(theta_dot)/dt

f_vec = sp.Matrix([f1, f2])
x_vec = sp.Matrix([theta, theta_dot])

# ---- Jacobians -------------------------------------------------------------
A_sym = f_vec.jacobian(x_vec)
B_sym = f_vec.jacobian(sp.Matrix([u_sym]))

print("Symbolic A(x, u) =")
sp.pprint(A_sym)
print("\nSymbolic B =")
sp.pprint(B_sym)

# ---- Evaluate at downward equilibrium: theta=0, theta_dot=0, u=0 ----------
# At theta=0: sin(theta)=0, cos(theta)=1
eq = {theta: 0, theta_dot: 0, u_sym: 0}

A_sym_eq = A_sym.subs(eq)
B_sym_eq = B_sym.subs(eq)

print("\nAt downward equilibrium (theta=0, theta_dot=0, u=0):")
print("A_sym ="); sp.pprint(A_sym_eq)
print("B_sym ="); sp.pprint(B_sym_eq)

# ---- Substitute numeric parameters -----------------------------------------
m_val, L_val, g_val, b_val = 1.0, 1.0, 9.81, 0.1

param_subs = {m_sym: m_val, L_sym: L_val, g_sym: g_val, b_sym: b_val}

A_num_sym = np.array(A_sym_eq.subs(param_subs).tolist(), dtype=float)
B_num_sym = np.array(B_sym_eq.subs(param_subs).tolist(), dtype=float)

print(f"\nNumeric (from sympy) with m={m_val}, L={L_val}, g={g_val}, b={b_val}:")
print(f"  A =\n{A_num_sym}")
print(f"  B =\n{B_num_sym}")

# %% Define pendulum as a Plant subclass (inline — single-use study)
class SimplePendulum(Plant):
    """Simple pendulum  theta'' = -(g/L) sin(theta) - (b/(mL^2)) theta_dot + u/(mL^2).

    State  x = [theta [rad], theta_dot [rad/s]].
    Input  u = applied torque [N·m].

    Parameters
    ----------
    m : bob mass [kg].
    L : rod length [m].
    g : gravitational acceleration [m/s^2].
    b : viscous damping coefficient [N·m·s/rad].
    """

    def __init__(self, m: float = 1.0, L: float = 1.0,
                 g: float = 9.81, b: float = 0.1) -> None:
        self.m = float(m)
        self.L = float(L)
        self.g = float(g)
        self.b = float(b)
        self.nx = 2
        self.nu = 1

    def dynamics(self, x: np.ndarray, u: np.ndarray, t: float = 0.0) -> np.ndarray:
        """State derivative [theta_dot, theta_ddot] for state [theta, theta_dot].

        Parameters
        ----------
        x : (2,) [theta [rad], theta_dot [rad/s]].
        u : (1,) applied torque [N·m].
        t : float, time [s] (unused — autonomous).

        Returns
        -------
        xdot : (2,) [theta_dot, theta_ddot].
        """
        x = np.asarray(x, dtype=float)
        u_scalar = float(np.asarray(u, dtype=float).ravel()[0])
        th, th_d = x[0], x[1]
        th_dd = (-(self.g / self.L) * np.sin(th)
                 - (self.b / (self.m * self.L**2)) * th_d
                 + u_scalar / (self.m * self.L**2))
        return np.array([th_d, th_dd])

# %% Numerical linearisation via linearize_plant
pendulum = SimplePendulum(m=m_val, L=L_val, g=g_val, b=b_val)

x0_eq = np.array([0.0, 0.0])   # downward equilibrium
u0_eq = np.array([0.0])         # zero torque at equilibrium

A_num_fd, B_num_fd = linearize_plant(pendulum, x0_eq, u0_eq)

print("\nNumerical (from linearize_plant finite-diff):")
print(f"  A =\n{A_num_fd}")
print(f"  B =\n{B_num_fd}")

# %% Cross-check: sympy vs finite-difference
match_A = np.allclose(A_num_sym, A_num_fd, atol=1e-8)
match_B = np.allclose(B_num_sym, B_num_fd, atol=1e-8)

print(f"\nA matches (np.allclose): {match_A}")
print(f"B matches (np.allclose): {match_B}")
print(f"Max |A_sym - A_fd| = {np.max(np.abs(A_num_sym - A_num_fd)):.2e}")
print(f"Max |B_sym - B_fd| = {np.max(np.abs(B_num_sym - B_num_fd)):.2e}")

if match_A and match_B:
    print("\nSYMBOLIC and NUMERICAL linearisations AGREE.")
else:
    raise RuntimeError("Linearisation mismatch — check derivation!")

print("run_04 complete.")
