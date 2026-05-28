#!/usr/bin/env python3
"""GCS 近期活动摘要 — recent git activity summary."""

import subprocess
import sys
from datetime import datetime, timezone


def run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True)
    return result.stdout.decode("utf-8", errors="replace").strip()


def main() -> None:
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    now_local = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
    days = sys.argv[1] if len(sys.argv) > 1 else "7"

    # Recent commits
    log = run(["git", "log", f"--since={days}.days", "--oneline"])
    count = len([l for l in log.split("\n") if l])

    # Changed files
    diff = run(["git", "diff", "--stat", f"@{{.{days}.days}}"])
    diff_count = len([l for l in diff.split("\n") if l.strip()])

    # Uncommitted
    status = run(["git", "status", "--short"])
    dirty = len([l for l in status.split("\n") if l.strip()])

    # Branch
    branch = run(["git", "branch", "--show-current"])

    print(f"# GCS 活动摘要 — {now_utc} / {now_local}")
    print(f"  分支: {branch}")
    print(f"  近 {days} 天: {count} 次提交, {diff_count} 个文件变更")
    if dirty:
        print(f"  未提交: {dirty} 个文件")
    print()
    if log:
        print("## 近期提交")
        for line in log.split("\n")[:20]:
            print(f"  {line}")
    if diff:
        print()
        print("## 变更统计")
        for line in diff.split("\n"):
            if line.strip():
                print(f"  {line}")
    if status:
        print()
        print("## 工作树状态")
        for line in status.split("\n"):
            if line.strip():
                print(f"  {line}")


if __name__ == "__main__":
    main()
