# Task Cards

Persist task cards here when work is non-trivial, high-risk, multi-step, or
likely to need later review. Use `../task-card-template.md` or:

```bat
python tools\agentic_design\agentic_toolkit.py new-task-card --slug <slug> --scope <scope> --risk <risk> --owner <skill> --request "<request>" --write
```

The generated file is a skeleton. Fill the scope, acceptance gates, evidence,
and residual risks before running `validate-task-card`.
