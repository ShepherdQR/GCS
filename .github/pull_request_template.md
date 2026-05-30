### Task Card
- [ ] Task card exists at `docs/agentic/tasks/<slug>.md`
- [ ] Task card validates: `python tools/agentic_design/agentic_toolkit.py validate-task-card docs/agentic/tasks/<slug>.md`

### Scope
- [ ] Staged files match the task card scope
- [ ] No unrelated dirty files staged
- [ ] `git diff --cached --name-only` reviewed

### Validation
- [ ] `python tools/agentic_design/agentic_toolkit.py validate-docs` passes
- [ ] `python tools/agentic_design/agentic_toolkit.py validate-inventory` passes
- [ ] `python tools/agentic_design/agentic_toolkit.py validate-skills` passes
- [ ] `python tools/agentic_design/agentic_toolkit.py check-dependencies` passes
- [ ] Relevant C++ tests pass (if applicable)
- [ ] `python -m compileall -q python/gcs_viz` passes (if Python changed)

### Evidence
- [ ] Demo or command transcript attached (if user-facing change)
- [ ] Expected output files updated (if output format changed)
- [ ] New fixtures include metadata and expected status

### Related
- Closes #<issue>
- Ref: `docs/architecture/<relevant>.md`
