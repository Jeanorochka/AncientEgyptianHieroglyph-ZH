from pathlib import Path
import tkinter as tk

from dict import (
    Direction,
    load_dictionary,
    translate,
)


BASE_DIR = Path(__file__).resolve().parent
DICTIONARY_PATH = BASE_DIR / "dictionary.json"


class TranslatorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("古埃及文字 ↔ 繁體中文")
        self.root.geometry("920x520")
        self.root.minsize(760, 420)

        self.entries = load_dictionary(DICTIONARY_PATH)
        self.direction_var = tk.StringVar(value="auto")
        self._updating = False

        self.build_ui()
        self.bind_events()

    def build_ui(self) -> None:
        # 極簡介面：左輸入，右輸出。
        self.root.configure(bg="#111111")

        top = tk.Frame(self.root, bg="#111111")
        top.pack(fill="x", padx=12, pady=(12, 8))

        for text, value in (
            ("Auto", "auto"),
            ("Egyptian → 中文", "egyptian_to_chinese"),
            ("中文 → Egyptian", "chinese_to_egyptian"),
        ):
            button = tk.Radiobutton(
                top,
                text=text,
                value=value,
                variable=self.direction_var,
                command=self.update_output,
                bg="#111111",
                fg="#EAEAEA",
                selectcolor="#222222",
                activebackground="#111111",
                activeforeground="#FFFFFF",
            )
            button.pack(side="left", padx=(0, 12))

        body = tk.Frame(self.root, bg="#111111")
        body.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        self.input_box = tk.Text(
            body,
            wrap="word",
            undo=True,
            bg="#181818",
            fg="#F2F2F2",
            insertbackground="#F2F2F2",
            selectbackground="#333333",
            relief="flat",
            padx=14,
            pady=12,
            font=("Segoe UI", 16),
        )
        self.input_box.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self.output_box = tk.Text(
            body,
            wrap="word",
            bg="#181818",
            fg="#F2F2F2",
            insertbackground="#F2F2F2",
            selectbackground="#333333",
            relief="flat",
            padx=14,
            pady=12,
            font=("Segoe UI", 16),
        )
        self.output_box.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        self.output_box.configure(state="disabled")

    def bind_events(self) -> None:
        self.input_box.bind("<KeyRelease>", lambda _event: self.update_output())
        self.input_box.bind("<<Paste>>", lambda _event: self.root.after(1, self.update_output))
        self.input_box.bind("<<Cut>>", lambda _event: self.root.after(1, self.update_output))

    def update_output(self) -> None:
        if self._updating:
            return

        self._updating = True

        try:
            source_text = self.input_box.get("1.0", "end-1c")
            direction = self.direction_var.get()

            result = translate(
                source_text,
                self.entries,
                direction=direction,  # type: ignore[arg-type]
            )

            self.output_box.configure(state="normal")
            self.output_box.delete("1.0", "end")
            self.output_box.insert("1.0", result)
            self.output_box.configure(state="disabled")
        finally:
            self._updating = False


def main() -> None:
    root = tk.Tk()
    TranslatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
