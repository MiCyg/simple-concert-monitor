from guizero import Box, PushButton

class NumericKeyboard:
    def __init__(self, parent, bg="#000000", additional_commands=True):
        self.parent = parent
        self.bg = bg
        self.active_entry = None
        self.additional_commands = additional_commands

        # Kontener klawiatury w parent, layout auto
        self.container = Box(
            parent,
            layout="auto",
            width="fill",
            height="fill",
            align="bottom",
            visible=False
        )
        self.container.bg = self.bg

        # inner_box z layout="grid"
        self.inner_box = Box(
            self.container,
            layout="grid",
            width="fill",
            height="fill"
        )
        self.inner_box.bg = self.bg

        self._build_keys()

    def _build_keys(self):
        keys = [
            ["1", "2", "3"],
            ["4", "5", "6"],
            ["7", "8", "9"],
            ["0", ".", "←"]
        ]

            
        total_cols = len(keys[0])
        total_rows = len(keys)
        if self.additional_commands:
            total_rows += 1  # +1 dla Clear/Close

        # Tworzenie przycisków numerycznych
        for r, row_keys in enumerate(keys):
            for c, key in enumerate(row_keys):
                btn = PushButton(
                    self.inner_box,
                    text=key,
                    command=(self.backspace if key == "←" else lambda k=key: self.insert_value(k)),
                    grid=[c, r],
                    width="fill",
                    height="fill",
                    padx=20,
                    pady=5
                )
                btn.bg = "#111111"
                btn.text_color = "#ffffff"
                btn.text_size = 22

        if self.additional_commands:
            # Ostatni rząd: Clear i Close w lewo/prawo oraz pusty środkowy przycisk
            clear_btn = PushButton(
                self.inner_box,
                text="Clear",
                command=self.clear_entry,
                grid=[0, total_rows - 1],
                width="fill",
                height="fill"
            )
            dummy_btn = Box(self.inner_box, grid=[1, total_rows - 1], width="fill", height="fill")  # pusty środek
            close_btn = PushButton(
                self.inner_box,
                text="Close",
                command=self.hide,
                grid=[2, total_rows - 1],
                width="fill",
                height="fill"
            )

            for btn in [clear_btn, close_btn]:
                btn.bg = "#555555"
                btn.text_color = "#ffffff"
                btn.text_size = 18

        # Rozciąganie wszystkich wierszy i kolumn równomiernie
        for r in range(total_rows):
            self.inner_box.tk.rowconfigure(r, weight=1)
        for c in range(total_cols):
            self.inner_box.tk.columnconfigure(c, weight=1)

    # -------------------------
    # Public API
    # -------------------------
    def attach(self, textbox):
        textbox.when_clicked = lambda: self.set_active(textbox)

    def set_active(self, textbox):
        self.active_entry = textbox
        self.show()

    def show(self):
        self.container.show()

    def hide(self):
        self.container.hide()
        self.active_entry = None

    # -------------------------
    # Key actions
    # -------------------------
    def insert_value(self, value):
        if self.active_entry:
            self.active_entry.value += str(value)

    def backspace(self):
        if self.active_entry:
            self.active_entry.value = self.active_entry.value[:-1]

    def clear_entry(self):
        if self.active_entry:
            self.active_entry.value = ""
