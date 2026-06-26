"""Build the plant selected by ``config.plant.type``.

Keeps ``main.py`` short: the script asks for a plant, this maps the YAML choice to a
concrete :class:`~lib.systems.plant.Plant`. The robot branch is the only one that
needs Pinocchio, and it is imported lazily so the state-space examples build on any
machine.
"""

from __future__ import annotations

from lib.systems.examples import double_integrator, mass_spring_damper, CartPole
from lib.systems.plant import Plant


def build_plant(cfg) -> Plant:
    """Return the plant chosen by ``cfg.plant.type``.

    Supported types: ``robot`` (Pinocchio URDF), ``double_integrator``,
    ``mass_spring_damper``, ``cart_pole``.
    """
    ptype = cfg.plant.type

    if ptype == "robot":
        # Lazy: only the robot path needs Pinocchio.
        from lib.dynamics.robot_model import RobotModel
        from lib.dynamics.robot_plant import RobotPlant
        from lib.utils.config import project_root

        robot = RobotModel(project_root() / cfg.robot.urdf, gravity=cfg.robot.gravity)
        return RobotPlant(robot)

    if ptype == "double_integrator":
        return double_integrator()

    if ptype == "mass_spring_damper":
        p = cfg.plant.mass_spring_damper
        return mass_spring_damper(m=p.m, k=p.k, c=p.c)

    if ptype == "cart_pole":
        p = cfg.plant.cart_pole
        return CartPole(m_cart=p.m_cart, m_pole=p.m_pole,
                        length=p.length, gravity=p.gravity)

    raise ValueError(
        f"unknown plant.type {ptype!r} "
        "(use robot | double_integrator | mass_spring_damper | cart_pole)"
    )
