from advanced_scraper.cli.app import build_parser, main


def test_cli_lists_workflow_commands():
    parser = build_parser()
    actions = [action for action in parser._actions if getattr(action, "choices", None)]
    commands = actions[0].choices
    assert {"recon", "api-scan", "fingerprint", "vuln", "fuzz", "assess", "doctor", "report", "history"} <= set(commands)


def test_active_scan_requires_authorization(tmp_path, capsys):
    exit_code = main(["--db", str(tmp_path / "scans.sqlite3"), "fingerprint", "https://example.org"])
    assert exit_code == 2
    assert "Authorization required" in capsys.readouterr().err


def test_doctor_is_offline_by_default(tmp_path):
    exit_code = main(["--db", str(tmp_path / "doctor.sqlite3"), "doctor"])
    assert exit_code == 0
