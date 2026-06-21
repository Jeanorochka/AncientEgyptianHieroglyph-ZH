from pathlib import Path

from dict import (
    inspect_codepoints,
    load_dictionary,
    translate,
)


BASE_DIR = Path(__file__).resolve().parent
DICTIONARY_PATH = BASE_DIR / "dictionary.json"


def main() -> None:
    # 載入詞典資料。
    entries = load_dictionary(DICTIONARY_PATH)

    print("古埃及文字 ↔ 繁體中文")
    print("1 = Auto")
    print("2 = Egyptian → 中文")
    print("3 = 中文 → Egyptian")
    print("4 = Unicode")
    print("0 = Exit")

    while True:
        mode = input("\nMode: ").strip()

        if mode == "0":
            break

        text = input("Text: ").strip()

        if mode == "1":
            print(translate(text, entries, "auto"))
        elif mode == "2":
            print(translate(text, entries, "egyptian_to_chinese"))
        elif mode == "3":
            print(translate(text, entries, "chinese_to_egyptian"))
        elif mode == "4":
            for item in inspect_codepoints(text):
                print(item)
        else:
            print("Unknown mode.")


if __name__ == "__main__":
    main()
