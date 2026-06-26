# Robot Models (URDF)

URDF descriptions used by `lib/dynamics/robot_model.py` (loaded via Pinocchio).

## Included
- **`double_pendulum.urdf`** — planar 2-DOF double pendulum (revolute about Y).
  Each link: 1 m, 1 kg, thin-rod inertia. Used by `main.py` and `run_01`.

## Adding a robot
1. Drop the `.urdf` (and any mesh files it references) here.
2. Point `config/params.yaml -> robot.urdf` at it.
3. Ensure **every link has an `<inertial>`** block (mass + inertia) or Pinocchio
   will build a degenerate model.

## Ready-made models
Installing `example-robot-data` (see `environment.yml`) gives standard arms/legs
(Panda, UR5, Talos, …) loadable directly with Pinocchio's `RobotWrapper`.
