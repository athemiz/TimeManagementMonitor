import tkinter as tk

class ToolTip:
    def __init__(self, parent, text): self.parent, self.text, self.tooltip = parent, text, None
    def show(self, x, y):
        if not self.tooltip:
            self.tooltip = tk.Toplevel(self.parent); self.tooltip.attributes('-alpha', 0.8, '-topmost', True); self.tooltip.overrideredirect(True)
            tk.Label(self.tooltip, text=self.text, background="#ffffe0", relief="solid", borderwidth=1).pack()
            self.tooltip.geometry(f"+{x}+{y}")

    def hide(self):
        if self.tooltip is not None:
            self.tooltip.destroy()
            self.tooltip = None