"""
StealthApply — entry point.
Run with: python -m stealthapply.main
"""

import tkinter as tk
from .gui import StealthApplyApp


def main() -> None:
    """Launch the StealthApply application."""
    root = tk.Tk()
    app = StealthApplyApp(root)

    # Center on screen
    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)
    root.geometry(f"{w}x{h}+{x}+{y}")

    root.mainloop()


if __name__ == "__main__":
    main()
