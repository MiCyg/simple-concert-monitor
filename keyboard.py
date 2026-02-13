from guizero import Box, PushButton

class NumericKeyboard:
    def __init__(self, parent, bg="#000000", height_ratio=0.5):
        self.parent = parent
        self.bg = bg
        self.active_entry = None

        # kontener u dołu ekranu
        screen_height = parent.tk.winfo_screenheight()
        screen_width = parent.tk.winfo_screenwidth()
        self.container = Box(
            parent,
            layout="grid",
            width=int(screen_width*0.6),  # 60% szerokości ekranu
            height=int(screen_height*height_ratio),
            align="bottom",
            visible=False
        )
        self.container.bg = self.bg

        # wrapper Box aby wyśrodkować poziomo
        self.inner_box = Box(
            self.container,
            layout="grid",
            width="fill",
            height="fill",
            grid=[0, 0]   # <- konieczne!
        )
        self.inner_box.bg = self.bg

        self._build_keys()

    def _build_keys(self):
        keys = [
            "7", "8", "9",
            "4", "5", "6",
            "1", "2", "3",
            "0", ".", "←"
        ]

        row = 0
        col = 0

        for key in keys:
            if key == "←":
                btn = PushButton(
                    self.inner_box,
                    text=key,
                    command=self.backspace,
                    grid=[col, row],
                    width=6,
                    height=2
                )
            else:
                btn = PushButton(
                    self.inner_box,
                    text=key,
                    command=lambda k=key: self.insert_value(k),
                    grid=[col, row],
                    width=6,
                    height=2
                )

            btn.bg = "#111111"
            btn.text_color = "#ffffff"
            btn.text_size = 22

            col += 1
            if col > 2:
                col = 0
                row += 1

        # dodatkowy rząd: Clear + Close
        clear_btn = PushButton(
            self.inner_box,
            text="Clear",
            command=self.clear_entry,
            grid=[0, row],
            width=6,
            height=2
        )

        close_btn = PushButton(
            self.inner_box,
            text="Close",
            command=self.hide,
            grid=[2, row],
            width=6,
            height=2
        )

        for btn in [clear_btn, close_btn]:
            btn.bg = "#555555"
            btn.text_color = "#ffffff"
            btn.text_size = 18

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
