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
    zh_Hant: str
    pos: str
    note: str
    meanings: list[dict[str, str]] = field(default_factory=list)
    unicode: str = ""
    unicode_name: str = ""
    gardiner_code: str = ""
    category: str = ""


def load_dictionary(path: Path) -> list[DictionaryEntry]:
    # 讀取 JSON 詞典檔案，並轉成型別安全的資料結構。
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
                        "zh_Hant": str(meaning.get("zh_Hant", "")),
                        "context": str(meaning.get("context", "")),
                    })

        entry = DictionaryEntry(
            id=str(item["id"]),
            egyptian=str(item["egyptian"]),
            transliteration=str(item.get("transliteration", "")),
            zh_Hant=str(item.get("zh_Hant", "未釋義")),
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
    # 判斷字元是否屬於 Unicode 古埃及文字區段。
    if not char:
        return False

    value = ord(char)
    return 0x13000 <= value <= 0x1342F


def has_egyptian_hieroglyph(text: str) -> bool:
    # 判斷文字中是否含有至少一個古埃及文字。
    return any(is_egyptian_hieroglyph(char) for char in text)


def is_cjk_unified_ideograph(char: str) -> bool:
    # 判斷是否為常見中日韓漢字區段。
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
    # 判斷文字中是否含有漢字。
    return any(is_cjk_unified_ideograph(char) for char in text)


def detect_translation_direction(text: str) -> Literal["egyptian_to_chinese", "chinese_to_egyptian"]:
    # 自動判斷翻譯方向：有古埃及字就優先視為古埃及文，否則視為中文。
    if has_egyptian_hieroglyph(text):
        return "egyptian_to_chinese"

    return "chinese_to_egyptian"


def build_egyptian_index(entries: list[DictionaryEntry]) -> dict[str, DictionaryEntry]:
    # 建立「古埃及文字 → 詞條」索引，方便快速查找。
    index: dict[str, DictionaryEntry] = {}

    for entry in entries:
        if entry.egyptian:
            index[entry.egyptian] = entry

    return index


def build_chinese_index(entries: list[DictionaryEntry]) -> dict[str, DictionaryEntry]:
    # 建立「繁體中文 → 詞條」索引，用於反向翻譯。
    index: dict[str, DictionaryEntry] = {}

    for entry in entries:
        candidates: list[str] = []

        if entry.zh_Hant and entry.zh_Hant != "未釋義":
            candidates.append(entry.zh_Hant)

        for meaning in entry.meanings:
            zh = meaning.get("zh_Hant", "").strip()
            if zh and zh != "未釋義":
                candidates.append(zh)

        for candidate in candidates:
            for part in candidate.split("／"):
                part = part.strip()
                if part and part not in index:
                    index[part] = entry

            if candidate and candidate not in index:
                index[candidate] = entry

    return index


def is_punctuation(char: str) -> bool:
    # 判斷是否為常見標點符號。
    return char in "，。！？；：（）,.!?;:()[]{}「」『』《》"


def display_translation(entry: DictionaryEntry) -> str:
    # 優先顯示主翻譯；如果有多義，用「／」保留多個可能值。
    values: list[str] = []

    if entry.zh_Hant and entry.zh_Hant != "未釋義":
        values.append(entry.zh_Hant)

    for meaning in entry.meanings:
        value = meaning.get("zh_Hant", "").strip()
        if value and value != "未釋義" and value not in values:
            values.append(value)

    if values:
        return "／".join(values)

    return "未釋義"


def translate_egyptian_to_chinese(text: str, entries: list[DictionaryEntry]) -> str:
    # 使用最長匹配法，從古埃及 Unicode 符號翻譯成繁體中文。
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
    # 使用最長匹配法，從繁體中文翻譯成古埃及 Unicode 符號。
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
    # 統一翻譯入口：支援自動方向，也支援手動指定方向。
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
    # 檢查輸入字元的 Unicode 編碼，確認是否真的是古埃及文字。
    result: list[str] = []

    for char in text:
        if char.isspace():
            continue

        codepoint = f"U+{ord(char):04X}"
        result.append(f"{char} = {codepoint}")

    return result
