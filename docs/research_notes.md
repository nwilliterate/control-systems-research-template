# Research Notes

A running lab notebook. One section per study; newest on top.

## Conventions
- **Units:** SI throughout — positions [rad]/[m], velocities [rad/s], torques [N·m].
- **State convention:** `x = [q, v]` (positions stacked above velocities).
- **Frames:** world-frame gravity set in `config/params.yaml`.

## AI-assistance log
Record here which modules were drafted with AI help, for venue disclosure later.
- 2026-06-26: Initial template (lib toolbox, controllers, integrators) scaffolded with AI assistance.

## Studies
### run_01 — free response of the double pendulum
- **Goal:** sanity-check the dynamics + RK4 loop with zero input.
- **Setup:** `models/double_pendulum.urdf`, initial `q=[0.5, 0]`, `dt=1e-3`.
- **Result:** _(fill in after running; figure at `results/figures/run_01/free_response.png`)_
- **Notes:** _(observations, next steps)_

<!-- Template for a new entry:
### run_NN — <short title>
- **Goal:**
- **Setup:**
- **Result:**
- **Notes:**
-->
