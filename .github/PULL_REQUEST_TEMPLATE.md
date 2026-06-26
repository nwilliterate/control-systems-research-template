## Summary
What does this PR change and why?

## Type
- [ ] Bug fix
- [ ] New feature (controller / dynamics / integrator / util)
- [ ] Docs
- [ ] Refactor / cleanup

## Checklist
- [ ] `pytest -q` passes locally (Pinocchio tests skip if it isn't installed)
- [ ] New pure-numpy routines have a test
- [ ] Pinocchio-dependent code stays import-guarded (pure-numpy import path intact)
- [ ] Reusable logic lives in `lib/`; `main.py` stays concise
- [ ] Parameters added to `config/params.yaml` (not hard-coded)
- [ ] Docstrings state units and array shapes
- [ ] Relevant docs (`README.md`, `docs/`) updated
