import json
import subprocess
import sys

from src.message import assembly_message, get_dates_line
from src.calendar import get_first_line_to_send, update_calendar


def test_get_dates_line_same_month():
    assert get_dates_line("2026-06-07", "2026-06-13") == "_Dal 7 al 13 Giugno_"


def test_assembly_message():
    message = assembly_message(
        header="*Aggiornamenti*",
        dates_line="_Dal 7 al 13 Giugno_",
        footer="---\nContatti: info@example.org",
        days=["*Lunedi*\n9:30 - Stand-up", "*Venerdi*\n17:30 - Report"],
    )

    assert message == (
        "*Aggiornamenti*\n"
        "_Dal 7 al 13 Giugno_\n\n"
        "*Lunedi*\n"
        "9:30 - Stand-up\n\n"
        "*Venerdi*\n"
        "17:30 - Report\n\n"
        "---\n"
        "Contatti: info@example.org"
    )


def test_assembly_message_without_header_and_footer():
    message = assembly_message(
        header=None,
        dates_line="_Dal 7 al 13 Giugno_",
        footer=None,
        days=["*Lunedi*\n9:30 - Stand-up"],
    )

    assert message == (
        "_Dal 7 al 13 Giugno_\n\n"
        "*Lunedi*\n"
        "9:30 - Stand-up\n\n"
    )


def test_get_first_line_to_send_returns_first_pending_entry(tmp_path):
    calendar_file = tmp_path / "calendar.jsonl"
    sent_entry = {
        "inviato": True,
        "valido-da": "2026-06-01",
        "valido-a": "2026-06-06",
        "messaggi": ["gia inviato"],
    }
    pending_entry = {
        "inviato": False,
        "valido-da": "2026-06-07",
        "valido-a": "2026-06-13",
        "messaggi": ["da inviare"],
    }
    calendar_file.write_text(
        json.dumps(sent_entry) + "\n" + json.dumps(pending_entry) + "\n",
        encoding="utf-8",
    )

    to_send = get_first_line_to_send(str(calendar_file))

    assert to_send["json"] == pending_entry
    assert to_send["string"] == json.dumps(pending_entry)


def test_update_calendar_marks_entry_as_sent(tmp_path):
    calendar_file = tmp_path / "calendar.jsonl"
    pending_entry = {
        "inviato": False,
        "valido-da": "2026-06-07",
        "valido-a": "2026-06-13",
        "messaggi": ["da inviare"],
    }
    calendar_file.write_text(json.dumps(pending_entry) + "\n", encoding="utf-8")
    to_send = get_first_line_to_send(str(calendar_file))

    assert update_calendar(
        str(calendar_file),
        to_send,
        "123",
    )

    updated_entry = json.loads(calendar_file.read_text(encoding="utf-8"))
    assert updated_entry["inviato"] is True
    assert updated_entry["message_id"] == "123"


def test_dry_run_without_more_does_not_require_config_file():
    result = subprocess.run(
        [sys.executable, "tabula.py", "--dry-run", "examples/calendario.jsonl"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "DRY RUN: messaggio non inviato; calendario non aggiornato." in result.stdout


def test_dry_run_with_more_uses_config_file():
    result = subprocess.run(
        [
            sys.executable,
            "tabula.py",
            "--dry-run",
            "--more",
            "examples/tabula.yaml",
            "examples/calendario.jsonl",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "*Aggiornamenti settimanali*" in result.stdout
    assert "Per contatti: info@example.org" in result.stdout
