import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal


Direction = Literal["auto", "egyptian_to_chinese", "chinese_to_egyptian"]


@dataclass(frozen=True)
class DictionaryEntry:
    id: str
    egyptian: str
    transliteration: str
    zh_Hans: str
    pos: str
    note: str
    meanings: list[dict[str, str]] = field(default_factory=list)
    unicode: str = ""
    unicode_name: str = ""
    gardiner_code: str = ""
    category: str = ""


def get_chinese_value(item: dict[str, Any]) -> str:
    # 优先读取简体中文；兼容旧版繁体中文字段。
    value = item.get("zh_Hans")

    if value is None:
        value = item.get("zh_Hant")

    if value is None:
        value = "未释义"

    return str(value)


def load_dictionary(path: Path) -> list[DictionaryEntry]:
    # 读取 JSON 词典，并兼容 zh_Hans / zh_Hant 两种字段。
    with path.open("r", encoding="utf-8") as file:
        raw_data: dict[str, Any] = json.load(file)

    entries_raw = raw_data.get("entries", [])

    if not isinstance(entries_raw, list):
        raise ValueError("dictionary.json must contain an 'entries' list.")

    entries: list[DictionaryEntry] = []

    for item in entries_raw:
        if not isinstance(item, dict):
            raise ValueError("Every dictionary entry must be an object.")

        raw_meanings = item.get("meanings", [])
        meanings: list[dict[str, str]] = []

        if isinstance(raw_meanings, list):
            for meaning in raw_meanings:
                if isinstance(meaning, dict):
                    meanings.append({
                        "zh_Hans": get_chinese_value(meaning),
                        "context": str(meaning.get("context", "")),
                    })

        entry = DictionaryEntry(
            id=str(item["id"]),
            egyptian=str(item.get("egyptian", "")),
            transliteration=str(item.get("transliteration", "")),
            zh_Hans=get_chinese_value(item),
            pos=str(item.get("pos", "")),
            note=str(item.get("note", "")),
            meanings=meanings,
            unicode=str(item.get("unicode", "")),
            unicode_name=str(item.get("unicode_name", "")),
            gardiner_code=str(item.get("gardiner_code", "")),
            category=str(item.get("category", "")),
        )

        entries.append(entry)

    return entries


def is_egyptian_hieroglyph(char: str) -> bool:
    # Unicode Egyptian Hieroglyphs block.
    if not char:
        return False

    value = ord(char)
    return 0x13000 <= value <= 0x1342F


def has_egyptian_hieroglyph(text: str) -> bool:
    return any(is_egyptian_hieroglyph(char) for char in text)


def is_cjk_unified_ideograph(char: str) -> bool:
    if not char:
        return False

    value = ord(char)
    return (
        0x3400 <= value <= 0x4DBF
        or 0x4E00 <= value <= 0x9FFF
        or 0xF900 <= value <= 0xFAFF
        or 0x20000 <= value <= 0x2FA1F
    )


def has_chinese_char(text: str) -> bool:
    return any(is_cjk_unified_ideograph(char) for char in text)


def detect_translation_direction(text: str) -> Literal["egyptian_to_chinese", "chinese_to_egyptian"]:
    # Если есть хотя бы один египетский глиф — переводим в китайский.
    # Иначе считаем ввод китайским / обычным текстом и переводим в египетский.
    if has_egyptian_hieroglyph(text):
        return "egyptian_to_chinese"

    return "chinese_to_egyptian"


def build_egyptian_index(entries: list[DictionaryEntry]) -> dict[str, list[DictionaryEntry]]:
    # One Egyptian spelling can have several Chinese meanings.
    index: dict[str, list[DictionaryEntry]] = {}

    for entry in entries:
        if entry.egyptian:
            index.setdefault(entry.egyptian, []).append(entry)

    return index


def build_chinese_index(entries: list[DictionaryEntry]) -> dict[str, DictionaryEntry]:
    # Builds Simplified Chinese -> Egyptian index.
    # Supports main zh_Hans and meanings[].zh_Hans.
    index: dict[str, DictionaryEntry] = {}

    for entry in entries:
        candidates: list[str] = []

        if entry.zh_Hans and entry.zh_Hans != "未释义":
            candidates.append(entry.zh_Hans)

        for meaning in entry.meanings:
            value = meaning.get("zh_Hans", "").strip()
            if value and value != "未释义":
                candidates.append(value)

        for candidate in candidates:
            candidate = candidate.strip()

            if not candidate:
                continue

            # Full phrase has priority.
            index.setdefault(candidate, entry)

            # Split variants like "妈妈／母亲" or "妈妈/母亲".
            for separator in ("／", "/", "、", ",", "，"):
                if separator in candidate:
                    for part in candidate.split(separator):
                        part = part.strip()
                        if part:
                            index.setdefault(part, entry)

    return index


def is_punctuation(char: str) -> bool:
    return char in "，。！？；：（）,.!?;:()[]{}「」『』《》、"


def display_translation(entries: list[DictionaryEntry]) -> str:
    # Several entries can share one Egyptian spelling; show unique values.
    values: list[str] = []

    for entry in entries:
        if entry.zh_Hans and entry.zh_Hans != "未释义" and entry.zh_Hans not in values:
            values.append(entry.zh_Hans)

        for meaning in entry.meanings:
            value = meaning.get("zh_Hans", "").strip()
            if value and value != "未释义" and value not in values:
                values.append(value)

    if values:
        return "／".join(values)

    return "未释义"


def translate_egyptian_to_chinese(text: str, entries: list[DictionaryEntry]) -> str:
    index = build_egyptian_index(entries)
    keys = sorted(index.keys(), key=len, reverse=True)

    result: list[str] = []
    i = 0

    while i < len(text):
        current_char = text[i]

        if current_char.isspace():
            i += 1
            continue

        if is_punctuation(current_char):
            result.append(current_char)
            i += 1
            continue

        matched = False

        for key in keys:
            if text.startswith(key, i):
                result.append(display_translation(index[key]))
                i += len(key)
                matched = True
                break

        if not matched:
            result.append(f"[未知:{current_char}]")
            i += 1

    return "".join(result)


def translate_chinese_to_egyptian(text: str, entries: list[DictionaryEntry]) -> str:
    index = build_chinese_index(entries)
    keys = sorted(index.keys(), key=len, reverse=True)

    result: list[str] = []
    i = 0

    while i < len(text):
        current_char = text[i]

        if current_char.isspace():
            i += 1
            continue

        if is_punctuation(current_char):
            result.append(current_char)
            i += 1
            continue

        matched = False

        for key in keys:
            if text.startswith(key, i):
                result.append(index[key].egyptian)
                i += len(key)
                matched = True
                break

        if not matched:
            result.append(f"[未知:{current_char}]")
            i += 1

    return "".join(result)


def translate(text: str, entries: list[DictionaryEntry], direction: Direction = "auto") -> str:
    if not text.strip():
        return ""

    selected_direction = direction

    if selected_direction == "auto":
        selected_direction = detect_translation_direction(text)

    if selected_direction == "egyptian_to_chinese":
        return translate_egyptian_to_chinese(text, entries)

    if selected_direction == "chinese_to_egyptian":
        return translate_chinese_to_egyptian(text, entries)

    raise ValueError(f"Unknown translation direction: {direction}")


def inspect_codepoints(text: str) -> list[str]:
    result: list[str] = []

    for char in text:
        if char.isspace():
            continue

        codepoint = f"U+{ord(char):04X}"
        result.append(f"{char} = {codepoint}")

    return result
