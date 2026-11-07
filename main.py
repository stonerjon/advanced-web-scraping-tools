from typing import Any, Dict, List


def build_report(findings: Dict[str, Any]) -> Dict[str, Any]:
    issues = findings.get("issues", [])
    assets = findings.get("assets", [])
    high = sum(1 for item in issues if item.get("severity") == "high")
    medium = sum(1 for item in issues if item.get("severity") == "medium")
    low = sum(1 for item in issues if item.get("severity") == "low")

    return {
        "summary": {
            "assets": len(assets),
            "issues": len(issues),
            "high": high,
            "medium": medium,
            "low": low,
        },
        "issues": issues,
        "assets": assets,
    }
