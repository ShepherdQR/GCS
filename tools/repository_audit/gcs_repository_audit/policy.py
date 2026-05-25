from __future__ import annotations

from .models import AuditFinding, RepositoryAuditSnapshot


def check_snapshot(snapshot: RepositoryAuditSnapshot) -> list[AuditFinding]:
    findings: list[AuditFinding] = []

    for metric in snapshot.files:
        if metric.artifact_class == "unknown":
            findings.append(
                AuditFinding(
                    id="unknown-artifact-class",
                    severity="warning",
                    confidence="high",
                    path=metric.path,
                    message="Tracked file does not match a known repository audit artifact class.",
                    recommendation="Classify the path or add an explicit exemption.",
                )
            )
        top = metric.path.split("/", 1)[0]
        if top in {"out", "outputs", "var"}:
            findings.append(
                AuditFinding(
                    id="tracked-build-output",
                    severity="error",
                    confidence="high",
                    path=metric.path,
                    message="Build or local output is tracked by git.",
                    recommendation="Remove the file from git or document a narrow exemption.",
                )
            )

    for module in snapshot.modules:
        if module.source_files > 0 and module.interface_files == 0:
            findings.append(
                AuditFinding(
                    id="module-missing-interface",
                    severity="error",
                    confidence="high",
                    path=module.source_dir,
                    message=f"Module {module.module_id} has source files but no C++ module interface.",
                    recommendation="Add a .cppm interface or correct module_inventory.json.",
                )
            )
        if module.source_files > 0 and module.implementation_files == 0:
            findings.append(
                AuditFinding(
                    id="module-missing-implementation",
                    severity="warning",
                    confidence="high",
                    path=module.source_dir,
                    message=f"Module {module.module_id} has source files but no C++ implementation file.",
                    recommendation="Add a .cpp implementation or record a module-specific exemption.",
                )
            )
        if module.contract_test and module.contract_test_files == 0:
            findings.append(
                AuditFinding(
                    id="module-missing-contract-test",
                    severity="error",
                    confidence="high",
                    path=module.contract_test,
                    message=f"Module {module.module_id} has no tracked contract test at the inventory path.",
                    recommendation="Add the contract test or correct module_inventory.json.",
                )
            )

    return findings
