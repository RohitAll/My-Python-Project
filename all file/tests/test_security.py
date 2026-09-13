"""
Unit Tests for Security Risk Classification System
"""

from security.permissions import security_checker, RiskLevel


def test_risk_level_evaluations():
    risk, _ = security_checker.evaluate_action("get_cpu_usage", {})
    assert risk == RiskLevel.LOW

    risk, msg = security_checker.evaluate_action("delete_file", {"filepath": "important.doc"})
    assert risk == RiskLevel.DANGEROUS
    assert "important.doc" in msg

    risk, msg = security_checker.evaluate_action("run_command", {"command": "rm -rf /"})
    assert risk == RiskLevel.DANGEROUS
