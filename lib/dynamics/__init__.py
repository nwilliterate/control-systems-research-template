"""Rigid-body dynamics built on Pinocchio.

These modules import :mod:`pinocchio` lazily inside functions/constructors so the
rest of the toolbox (integrators, controllers, utils) stays usable on machines
where Pinocchio is not installed.
"""
