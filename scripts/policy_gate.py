"""Policy gate: one place that decides whether an image may be deployed.

The three scanners only report. This script reads their results, applies the rules below,
prints a table (also written to the GitHub step summary) and exits 1 if any rule is broken.
"""
import json
import os
import sys

# The rules. Change them here, in one place, for every scanner.
BLOCK_SNYK_SEVERITIES = {"critical", "high"}


def sonar_rule():
    passed = os.environ.get("SONAR_OUTCOME") == "success"
    return "SonarQube", "Quality gate passed", passed, "passed" if passed else "quality gate FAILED"


def snyk_rule():
    try:
        with open("snyk.json", encoding="utf-8") as f:
            report = json.load(f)
    except (OSError, ValueError):
        return "Snyk", "No high or critical dependency issues", False, "no report produced"
    vulns = report.get("vulnerabilities", [])
    # Snyk lists one entry per path to a vulnerable package, so count each issue once
    blocking = {v["id"] for v in vulns if v.get("severity") in BLOCK_SNYK_SEVERITIES}
    return "Snyk", "No high or critical dependency issues", not blocking, f"{len(blocking)} high/critical"


def inspector_rule():
    flag = os.environ.get("INSPECTOR_EXCEEDED", "")
    rule = "No fixable high or critical CVEs in the image"
    if flag not in ("0", "1"):
        return "Amazon Inspector", rule, False, "scan did not run"
    passed = flag == "0"
    return "Amazon Inspector", rule, passed, "clean" if passed else "threshold exceeded"


def main():
    results = [sonar_rule(), snyk_rule(), inspector_rule()]
    rows = ["| Scanner | Rule | Result |", "|---|---|---|"]
    for name, rule, passed, detail in results:
        rows.append(f"| {name} | {rule} | {'PASS' if passed else 'FAIL'}: {detail} |")
    allowed = all(r[2] for r in results)
    verdict = "**Policy gate PASSED: image approved for deploy**" if allowed else "**Policy gate FAILED: deploy blocked**"
    table = "\n".join(rows + ["", verdict])

    print(table)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write("## Policy gate\n\n" + table + "\n")
    sys.exit(0 if allowed else 1)


if __name__ == "__main__":
    main()
