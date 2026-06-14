from datetime import date
from pathlib import Path
from typing import Any

import streamlit as st

from src import calendar as calendar_service

CALENDAR_DIRS = (Path("data"), Path("examples"))


def parse_date(value: str) -> date:
    return date.fromisoformat(value)


def message_text(entry: dict[str, Any]) -> str:
    return "\n\n".join(entry.get("messaggi", []))


def split_message_text(text: str) -> list[str]:
    return [message.strip() for message in text.split("\n\n") if message.strip()]


def first_pending_index(entries: list[dict[str, Any]]) -> int:
    return calendar_service.get_first_line_to_send(entries) or 0


def select_entry(index: int) -> None:
    st.session_state.selected_entry = index


def find_calendar_files() -> list[Path]:
    files = []
    for calendar_dir in CALENDAR_DIRS:
        if calendar_dir.exists():
            files.extend(calendar_dir.glob("*.jsonl"))
    return sorted(files)


def select_calendar_file(calendar_file: Path) -> None:
    st.session_state.calendar_file = str(calendar_file)
    st.session_state.pop("selected_entry", None)


def build_file_selector(calendar_files: list[Path]) -> None:
    if not calendar_files:
        st.error("Nessun file JSONL trovato.")
        st.stop()

    selected_file = st.selectbox(
        "Calendario",
        options=calendar_files,
        index=None,
        format_func=lambda path: str(path),
        placeholder="Seleziona un file JSONL",
    )

    if selected_file is not None:
        select_calendar_file(selected_file)
        st.rerun()


def build_form(calendar_file: Path, entries: list[dict[str, Any]], selected_index: int) -> None:
    entry = entries[selected_index]
    sent = entry.get("inviato", False)

    with st.container(horizontal=True):
        st.date_input("Dal", value=parse_date(entry["valido-da"]), disabled=True)
        st.date_input("Al", value=parse_date(entry["valido-a"]), disabled=True)

    text = st.text_area(
        "Testo",
        value=message_text(entry),
        height=320,
        disabled=sent,
        key=f"message_text_{selected_index}",
    )

    with st.container(horizontal=True):
        if sent:
            st.badge("Inviato", color="green")
        else:
            if st.button("Salva modifiche"):
                entries[selected_index] = {**entry, "messaggi": split_message_text(text)}
                if calendar_service.update_calendar(str(calendar_file), entries):
                    st.success("Modifiche salvate.")
                    st.rerun()
                else:
                    st.error("Errore durante il salvataggio.")

st.set_page_config(page_title="TabulaBot", layout="wide")

if "calendar_file" not in st.session_state:
    build_file_selector(find_calendar_files())
    st.stop()

calendar_file = Path(st.session_state.calendar_file)

if not calendar_file.exists():
    st.session_state.pop("calendar_file", None)
    st.error(f"File calendario non trovato: {calendar_file}")
    st.stop()

calendar_entries = calendar_service.load_json_calendar(str(calendar_file))
if not calendar_entries:
    st.warning("Calendario vuoto.")
    st.stop()

if "selected_entry" not in st.session_state:
    st.session_state.selected_entry = first_pending_index(calendar_entries)

st.session_state.selected_entry = min(
    st.session_state.selected_entry,
    len(calendar_entries) - 1,
)

with st.sidebar:
    for index, entry in enumerate(calendar_entries):
        label = f"{entry['valido-da']} - {entry['valido-a']}"
        icon = ":material/check_circle:" if entry.get("inviato", False) else ":material/circle:"
        button_type = "primary" if index == st.session_state.selected_entry else "secondary"
        st.button(
            label=label,
            icon=icon,
            type=button_type,
            on_click=select_entry,
            args=(index,),
            key=f"entry_{index}",
        )

build_form(calendar_file, calendar_entries, st.session_state.selected_entry)
