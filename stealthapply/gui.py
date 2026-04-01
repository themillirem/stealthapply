"""
StealthApply GUI — built with tkinter + ttk (dark Catppuccin-inspired theme).
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from pathlib import Path
from typing import Optional
from datetime import datetime

from .config import (
    APP_TITLE, APP_WIDTH, APP_HEIGHT,
    BG_DARK, BG_PANEL, BG_CARD,
    FG_TEXT, FG_MUTED,
    ACCENT_BLUE, ACCENT_GREEN, ACCENT_RED, ACCENT_YELLOW, ACCENT_MAUVE,
    OLLAMA_BASE_URL, OLLAMA_DEFAULT_MODEL,
)
from .job_scraper import JobListing, get_all_jobs
from .resume_parser import parse_resume, get_resume_preview
from .llm_client import OllamaClient
from .submitter import Submitter, SubmissionReceipt


class StealthApplyApp:
    """Main application window."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(True, True)
        self.root.minsize(800, 550)

        # State
        self.resume_path: Optional[str] = None
        self.resume_text: Optional[str] = None
        self.jobs: list[JobListing] = get_all_jobs()
        self.job_vars: list[tk.BooleanVar] = []
        self.last_receipt: Optional[SubmissionReceipt] = None
        self.ollama_url: str = OLLAMA_BASE_URL
        self.ollama_model: str = OLLAMA_DEFAULT_MODEL
        self.is_running: bool = False

        self._setup_styles()
        self._build_ui()

    # ------------------------------------------------------------------
    # Styles
    # ------------------------------------------------------------------

    def _setup_styles(self) -> None:
        """Configure ttk styles for the dark theme."""
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(".", background=BG_DARK, foreground=FG_TEXT, font=("Helvetica", 11))

        style.configure("TFrame", background=BG_DARK)
        style.configure("Panel.TFrame", background=BG_PANEL)
        style.configure("Card.TFrame", background=BG_CARD)

        style.configure("TLabel", background=BG_DARK, foreground=FG_TEXT)
        style.configure("Panel.TLabel", background=BG_PANEL, foreground=FG_TEXT)
        style.configure("Muted.TLabel", background=BG_DARK, foreground=FG_MUTED, font=("Helvetica", 9))
        style.configure("Title.TLabel", background=BG_DARK, foreground=ACCENT_MAUVE, font=("Helvetica", 18, "bold"))
        style.configure("Subtitle.TLabel", background=BG_PANEL, foreground=FG_MUTED, font=("Helvetica", 10))
        style.configure("Success.TLabel", background=BG_DARK, foreground=ACCENT_GREEN)
        style.configure("Error.TLabel", background=BG_DARK, foreground=ACCENT_RED)

        style.configure(
            "TButton",
            background=BG_CARD,
            foreground=FG_TEXT,
            borderwidth=0,
            focusthickness=0,
            padding=(12, 6),
            font=("Helvetica", 11),
        )
        style.map("TButton", background=[("active", ACCENT_BLUE), ("pressed", ACCENT_BLUE)])

        style.configure(
            "Accent.TButton",
            background=ACCENT_BLUE,
            foreground=BG_DARK,
            font=("Helvetica", 11, "bold"),
            padding=(14, 8),
        )
        style.map("Accent.TButton", background=[("active", ACCENT_MAUVE), ("disabled", FG_MUTED)])

        style.configure(
            "Execute.TButton",
            background=ACCENT_GREEN,
            foreground=BG_DARK,
            font=("Helvetica", 13, "bold"),
            padding=(16, 10),
        )
        style.map("Execute.TButton", background=[("active", "#79d3a0"), ("disabled", FG_MUTED)])

        style.configure(
            "Danger.TButton",
            background=ACCENT_RED,
            foreground=BG_DARK,
            font=("Helvetica", 11),
            padding=(12, 6),
        )
        style.map("Danger.TButton", background=[("active", "#e06c75")])

        style.configure("TCheckbutton", background=BG_PANEL, foreground=FG_TEXT)
        style.map("TCheckbutton", background=[("active", BG_PANEL)])

        style.configure(
            "Horizontal.TProgressbar",
            troughcolor=BG_CARD,
            background=ACCENT_BLUE,
            thickness=8,
        )

        style.configure(
            "TScrollbar",
            background=BG_CARD,
            troughcolor=BG_DARK,
            borderwidth=0,
        )

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Build the full application UI."""
        # Header bar
        self._build_header()

        # Main content area (left panel + right panel)
        main = ttk.Frame(self.root, style="TFrame")
        main.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=2)
        main.rowconfigure(0, weight=1)

        self._build_left_panel(main)
        self._build_right_panel(main)

        # Bottom bar
        self._build_bottom_bar()

    def _build_header(self) -> None:
        """Top header with title and settings."""
        header = ttk.Frame(self.root, style="Panel.TFrame")
        header.pack(fill=tk.X, padx=0, pady=0)

        inner = ttk.Frame(header, style="Panel.TFrame")
        inner.pack(fill=tk.X, padx=16, pady=10)

        ttk.Label(inner, text="🎯  StealthApply", style="Title.TLabel").pack(side=tk.LEFT)
        ttk.Label(
            inner,
            text="Privacy-first resume submission for SolidWorks Engineers",
            style="Subtitle.TLabel",
        ).pack(side=tk.LEFT, padx=(12, 0), pady=(6, 0))

        ttk.Button(inner, text="⚙ Settings", command=self._open_settings).pack(side=tk.RIGHT)

    def _build_left_panel(self, parent: ttk.Frame) -> None:
        """Left panel: resume upload + status."""
        left = ttk.Frame(parent, style="Panel.TFrame")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=0)
        left.rowconfigure(2, weight=1)
        left.columnconfigure(0, weight=1)

        # --- Resume Section ---
        resume_header = ttk.Frame(left, style="Panel.TFrame")
        resume_header.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 4))
        ttk.Label(resume_header, text="📄  Resume", style="Panel.TLabel",
                  font=("Helvetica", 13, "bold")).pack(side=tk.LEFT)

        resume_frame = ttk.Frame(left, style="Card.TFrame")
        resume_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))
        resume_frame.columnconfigure(0, weight=1)

        self.resume_label = tk.Label(
            resume_frame,
            text="No resume loaded",
            bg=BG_CARD,
            fg=FG_MUTED,
            font=("Helvetica", 10),
            anchor="w",
            wraplength=220,
        )
        self.resume_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 4))

        btn_frame = ttk.Frame(resume_frame, style="Card.TFrame")
        btn_frame.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))

        ttk.Button(btn_frame, text="📂  Upload Resume", style="Accent.TButton",
                   command=self._upload_resume).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(btn_frame, text="✕ Clear", style="Danger.TButton",
                   command=self._clear_resume).pack(side=tk.LEFT)

        # Resume preview
        self.resume_preview = scrolledtext.ScrolledText(
            left,
            wrap=tk.WORD,
            bg=BG_CARD,
            fg=FG_MUTED,
            insertbackground=FG_TEXT,
            font=("Courier", 9),
            relief=tk.FLAT,
            state=tk.DISABLED,
            height=8,
        )
        self.resume_preview.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 8))

        # --- LLM Status ---
        llm_frame = ttk.Frame(left, style="Card.TFrame")
        llm_frame.grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 12))
        llm_frame.columnconfigure(1, weight=1)

        ttk.Label(llm_frame, text="🤖  LLM Status", background=BG_CARD,
                  foreground=FG_MUTED, font=("Helvetica", 9)).grid(
            row=0, column=0, sticky="w", padx=10, pady=(8, 2))

        self.llm_status_label = tk.Label(
            llm_frame, text="Checking...", bg=BG_CARD,
            fg=ACCENT_YELLOW, font=("Helvetica", 9)
        )
        self.llm_status_label.grid(row=0, column=1, sticky="w", padx=4, pady=(8, 2))

        tk.Label(llm_frame, text="Model:", bg=BG_CARD, fg=FG_MUTED,
                 font=("Helvetica", 9)).grid(row=1, column=0, sticky="w", padx=10, pady=(0, 8))
        self.llm_model_label = tk.Label(
            llm_frame, text=self.ollama_model, bg=BG_CARD,
            fg=ACCENT_BLUE, font=("Helvetica", 9)
        )
        self.llm_model_label.grid(row=1, column=1, sticky="w", padx=4, pady=(0, 8))

        # Check LLM status in background
        self.root.after(500, self._check_llm_status)

    def _build_right_panel(self, parent: ttk.Frame) -> None:
        """Right panel: job list with checkboxes."""
        right = ttk.Frame(parent, style="Panel.TFrame")
        right.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        # Header row
        header_row = ttk.Frame(right, style="Panel.TFrame")
        header_row.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))

        ttk.Label(header_row, text="💼  Target Companies", style="Panel.TLabel",
                  font=("Helvetica", 13, "bold")).pack(side=tk.LEFT)

        self.selected_count_label = tk.Label(
            header_row, text="0 selected",
            bg=BG_PANEL, fg=FG_MUTED, font=("Helvetica", 9)
        )
        self.selected_count_label.pack(side=tk.LEFT, padx=(10, 0))

        ttk.Button(header_row, text="✓ All", command=self._select_all).pack(side=tk.RIGHT, padx=(4, 0))
        ttk.Button(header_row, text="✗ None", command=self._deselect_all).pack(side=tk.RIGHT, padx=(4, 0))

        # Scrollable checkbox list
        list_container = ttk.Frame(right, style="Panel.TFrame")
        list_container.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 8))
        list_container.rowconfigure(0, weight=1)
        list_container.columnconfigure(0, weight=1)

        canvas = tk.Canvas(list_container, bg=BG_PANEL, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
        self.job_frame = ttk.Frame(canvas, style="Panel.TFrame")

        self.job_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.job_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Bind mousewheel
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        # Populate job checkboxes
        self._populate_jobs()

    def _populate_jobs(self) -> None:
        """Populate the job list with checkboxes."""
        self.job_vars.clear()

        for widget in self.job_frame.winfo_children():
            widget.destroy()

        for i, job in enumerate(self.jobs):
            var = tk.BooleanVar(value=False)
            self.job_vars.append(var)

            row_bg = BG_PANEL if i % 2 == 0 else BG_CARD

            row = tk.Frame(self.job_frame, bg=row_bg)
            row.pack(fill=tk.X, padx=4, pady=1)

            cb = tk.Checkbutton(
                row,
                text="",
                variable=var,
                bg=row_bg,
                fg=FG_TEXT,
                selectcolor=BG_CARD,
                activebackground=row_bg,
                command=self._update_selected_count,
            )
            cb.pack(side=tk.LEFT, padx=(8, 0))

            company_label = tk.Label(
                row, text=job.company,
                bg=row_bg, fg=ACCENT_BLUE,
                font=("Helvetica", 11, "bold"),
                width=22, anchor="w",
            )
            company_label.pack(side=tk.LEFT, padx=(0, 8))

            title_label = tk.Label(
                row, text=job.title,
                bg=row_bg, fg=FG_TEXT,
                font=("Helvetica", 10),
                anchor="w",
            )
            title_label.pack(side=tk.LEFT)

            loc_label = tk.Label(
                row, text=f"  📍{job.location}",
                bg=row_bg, fg=FG_MUTED,
                font=("Helvetica", 9),
                anchor="e",
            )
            loc_label.pack(side=tk.RIGHT, padx=(0, 8))

    def _build_bottom_bar(self) -> None:
        """Bottom bar: progress, execute button, actions."""
        bar = ttk.Frame(self.root, style="Panel.TFrame")
        bar.pack(fill=tk.X, padx=0, pady=0, side=tk.BOTTOM)

        inner = ttk.Frame(bar, style="Panel.TFrame")
        inner.pack(fill=tk.X, padx=16, pady=10)
        inner.columnconfigure(1, weight=1)

        # Execute button
        self.execute_btn = ttk.Button(
            inner, text="🚀  Execute Submissions",
            style="Execute.TButton",
            command=self._execute_submissions,
        )
        self.execute_btn.grid(row=0, column=0, padx=(0, 16))

        # Progress area
        progress_frame = ttk.Frame(inner, style="Panel.TFrame")
        progress_frame.grid(row=0, column=1, sticky="ew")
        progress_frame.columnconfigure(0, weight=1)

        self.progress_label = tk.Label(
            progress_frame, text="Ready",
            bg=BG_PANEL, fg=FG_MUTED, font=("Helvetica", 10), anchor="w"
        )
        self.progress_label.pack(fill=tk.X)

        self.progress_bar = ttk.Progressbar(
            progress_frame, style="Horizontal.TProgressbar",
            mode="determinate", maximum=100
        )
        self.progress_bar.pack(fill=tk.X, pady=(4, 0))

        # Receipt button (hidden until receipt exists)
        self.receipt_btn = ttk.Button(
            inner, text="📋 View Receipt",
            command=self._show_receipt,
            state=tk.DISABLED,
        )
        self.receipt_btn.grid(row=0, column=2, padx=(16, 0))

        ttk.Button(inner, text="🗑 Clear All", style="Danger.TButton",
                   command=self._clear_all).grid(row=0, column=3, padx=(8, 0))

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _upload_resume(self) -> None:
        """Open file dialog to upload a resume."""
        file_path = filedialog.askopenfilename(
            title="Select Resume",
            filetypes=[
                ("Resume files", "*.pdf *.docx"),
                ("PDF files", "*.pdf"),
                ("Word documents", "*.docx"),
                ("All files", "*.*"),
            ],
        )
        if not file_path:
            return

        try:
            self.resume_text = parse_resume(file_path)
            self.resume_path = file_path
            filename = Path(file_path).name
            self.resume_label.config(text=f"✅  {filename}", fg=ACCENT_GREEN)

            # Show preview
            preview = get_resume_preview(self.resume_text, 800)
            self.resume_preview.config(state=tk.NORMAL)
            self.resume_preview.delete("1.0", tk.END)
            self.resume_preview.insert(tk.END, preview)
            self.resume_preview.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("Resume Error", f"Failed to load resume:\n\n{e}")
            self.resume_label.config(text="❌  Failed to load resume", fg=ACCENT_RED)

    def _clear_resume(self) -> None:
        """Clear the loaded resume."""
        self.resume_path = None
        self.resume_text = None
        self.resume_label.config(text="No resume loaded", fg=FG_MUTED)
        self.resume_preview.config(state=tk.NORMAL)
        self.resume_preview.delete("1.0", tk.END)
        self.resume_preview.config(state=tk.DISABLED)

    def _select_all(self) -> None:
        """Select all job checkboxes."""
        for var in self.job_vars:
            var.set(True)
        self._update_selected_count()

    def _deselect_all(self) -> None:
        """Deselect all job checkboxes."""
        for var in self.job_vars:
            var.set(False)
        self._update_selected_count()

    def _update_selected_count(self) -> None:
        """Update the selected job count label."""
        count = sum(1 for v in self.job_vars if v.get())
        self.selected_count_label.config(
            text=f"{count} selected",
            fg=ACCENT_BLUE if count > 0 else FG_MUTED,
        )

    def _execute_submissions(self) -> None:
        """Start the submission process in a background thread."""
        if self.is_running:
            return

        if not self.resume_text:
            messagebox.showwarning("No Resume", "Please upload a resume before submitting.")
            return

        selected_jobs = [
            job for job, var in zip(self.jobs, self.job_vars) if var.get()
        ]

        if not selected_jobs:
            messagebox.showwarning("No Jobs Selected", "Please select at least one company to apply to.")
            return

        confirm = messagebox.askyesno(
            "Confirm Submission",
            f"Submit your resume to {len(selected_jobs)} company/companies?\n\n"
            "This will use your local LLM to generate tailored cover notes.",
        )
        if not confirm:
            return

        self.is_running = True
        self.execute_btn.config(state=tk.DISABLED)
        self.last_receipt = None
        self.receipt_btn.config(state=tk.DISABLED)
        self.progress_bar["value"] = 0

        thread = threading.Thread(
            target=self._run_submissions,
            args=(selected_jobs,),
            daemon=True,
        )
        thread.start()

    def _run_submissions(self, jobs: list[JobListing]) -> None:
        """Background thread: run all submissions."""
        llm = OllamaClient(base_url=self.ollama_url, model=self.ollama_model)
        submitter = Submitter(llm_client=llm)

        def progress(current: int, total: int, message: str) -> None:
            pct = int((current / total) * 100) if total > 0 else 0
            self.root.after(0, lambda: self._update_progress(pct, message))

        receipt = submitter.submit_all(
            jobs=jobs,
            resume_text=self.resume_text,
            progress_callback=progress,
        )

        self.last_receipt = receipt
        self.root.after(0, self._submission_complete)

    def _update_progress(self, pct: int, message: str) -> None:
        """Update progress bar and label (called from main thread)."""
        self.progress_bar["value"] = pct
        self.progress_label.config(text=message, fg=FG_TEXT)

    def _submission_complete(self) -> None:
        """Called when submission thread finishes."""
        self.is_running = False
        self.execute_btn.config(state=tk.NORMAL)
        self.receipt_btn.config(state=tk.NORMAL)

        summary = self.last_receipt.summary()
        self.progress_label.config(
            text=f"✅  Done! {summary['success']} submitted, {summary['errors']} errors",
            fg=ACCENT_GREEN,
        )
        self.progress_bar["value"] = 100

        messagebox.showinfo(
            "Submissions Complete",
            f"✅  {summary['success']} applications submitted\n"
            f"❌  {summary['errors']} errors\n\n"
            "Click 'View Receipt' for the full transaction log.",
        )

    def _show_receipt(self) -> None:
        """Show the transaction receipt in a new window."""
        if not self.last_receipt:
            return

        win = tk.Toplevel(self.root)
        win.title("Transaction Receipt")
        win.geometry("700x500")
        win.configure(bg=BG_DARK)
        win.grab_set()

        ttk.Label(win, text="📋  Transaction Receipt",
                  font=("Helvetica", 14, "bold"),
                  foreground=ACCENT_MAUVE, background=BG_DARK).pack(pady=(12, 4))

        text = scrolledtext.ScrolledText(
            win, bg=BG_CARD, fg=FG_TEXT,
            font=("Courier", 10), relief=tk.FLAT,
            state=tk.NORMAL,
        )
        text.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
        text.insert(tk.END, self.last_receipt.as_text())
        text.config(state=tk.DISABLED)

        btn_frame = ttk.Frame(win)
        btn_frame.pack(pady=(0, 12))

        ttk.Button(
            btn_frame, text="💾  Save Receipt",
            style="Accent.TButton",
            command=lambda: self._save_receipt(win),
        ).pack(side=tk.LEFT, padx=6)

        ttk.Button(btn_frame, text="Close", command=win.destroy).pack(side=tk.LEFT, padx=6)

    def _save_receipt(self, parent_win: tk.Toplevel) -> None:
        """Save the receipt to a file chosen by the user."""
        if not self.last_receipt:
            return

        default_name = f"stealthapply_receipt_{self.last_receipt.run_id}.txt"
        file_path = filedialog.asksaveasfilename(
            parent=parent_win,
            title="Save Receipt",
            defaultextension=".txt",
            initialfile=default_name,
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.last_receipt.as_text())
            messagebox.showinfo("Saved", f"Receipt saved to:\n{file_path}", parent=parent_win)
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save receipt:\n{e}", parent=parent_win)

    def _clear_all(self) -> None:
        """Clear all in-memory state."""
        if self.is_running:
            messagebox.showwarning("Running", "Please wait for the current submission to complete.")
            return

        confirm = messagebox.askyesno("Clear All", "Clear all loaded data and selections?")
        if not confirm:
            return

        self._clear_resume()
        self._deselect_all()
        self.last_receipt = None
        self.receipt_btn.config(state=tk.DISABLED)
        self.progress_bar["value"] = 0
        self.progress_label.config(text="Ready", fg=FG_MUTED)

    def _check_llm_status(self) -> None:
        """Check Ollama availability and update the status label."""
        def check():
            client = OllamaClient(base_url=self.ollama_url, model=self.ollama_model)
            available = client.is_available()
            self.root.after(0, lambda: self._set_llm_status(available))

        threading.Thread(target=check, daemon=True).start()

    def _set_llm_status(self, available: bool) -> None:
        """Update LLM status label."""
        if available:
            self.llm_status_label.config(text="● Online", fg=ACCENT_GREEN)
        else:
            self.llm_status_label.config(text="● Offline (will skip cover notes)", fg=ACCENT_YELLOW)

    def _open_settings(self) -> None:
        """Open the settings dialog."""
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.geometry("420x240")
        win.configure(bg=BG_DARK)
        win.grab_set()
        win.resizable(False, False)

        ttk.Label(win, text="⚙  Settings", font=("Helvetica", 14, "bold"),
                  foreground=ACCENT_MAUVE, background=BG_DARK).pack(pady=(12, 8))

        frame = ttk.Frame(win, style="Card.TFrame")
        frame.pack(fill=tk.X, padx=20, pady=4)
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Ollama URL:", background=BG_CARD).grid(
            row=0, column=0, sticky="w", padx=10, pady=(10, 4))
        url_var = tk.StringVar(value=self.ollama_url)
        url_entry = ttk.Entry(frame, textvariable=url_var, width=30)
        url_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=(10, 4))

        ttk.Label(frame, text="Model:", background=BG_CARD).grid(
            row=1, column=0, sticky="w", padx=10, pady=(4, 10))
        model_var = tk.StringVar(value=self.ollama_model)
        model_entry = ttk.Entry(frame, textvariable=model_var, width=30)
        model_entry.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(4, 10))

        def save():
            self.ollama_url = url_var.get().strip()
            self.ollama_model = model_var.get().strip()
            self.llm_model_label.config(text=self.ollama_model)
            self.llm_status_label.config(text="Checking...", fg=ACCENT_YELLOW)
            self._check_llm_status()
            win.destroy()

        btn_frame = ttk.Frame(win)
        btn_frame.pack(pady=12)
        ttk.Button(btn_frame, text="Save", style="Accent.TButton", command=save).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text="Cancel", command=win.destroy).pack(side=tk.LEFT, padx=6)
