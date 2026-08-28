"""Navigation shell and scrollable task pages for the desktop application."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, Optional

from ui_theme import COLORS


class ScrollablePage(ttk.Frame):
    def __init__(self, master, title: str, subtitle: str):
        super().__init__(master, style="Workspace.TFrame")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        header = ttk.Frame(self, style="Workspace.TFrame", padding=(30, 24, 30, 16))
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        ttk.Label(header, text=title, style="PageTitle.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(header, text=subtitle, style="PageSubtitle.TLabel").grid(
            row=1, column=0, sticky="w", pady=(5, 0)
        )

        body_host = ttk.Frame(self, style="Workspace.TFrame")
        body_host.grid(row=1, column=0, sticky="nsew")
        body_host.grid_rowconfigure(0, weight=1)
        body_host.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            body_host,
            bg=COLORS["background"],
            highlightthickness=0,
            borderwidth=0,
        )
        scrollbar = ttk.Scrollbar(
            body_host, orient="vertical", command=self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.content = ttk.Frame(
            self.canvas,
            style="Workspace.TFrame",
            padding=(30, 4, 30, 76),
        )
        self.content.grid_columnconfigure(0, weight=1)
        self._window_id = self.canvas.create_window(
            (0, 0), window=self.content, anchor="nw"
        )

        self.content.bind("<Configure>", self._sync_scroll_region)
        self.canvas.bind("<Configure>", self._sync_content_width)
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

    def _sync_scroll_region(self, _event=None) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _sync_content_width(self, event) -> None:
        self.canvas.itemconfigure(self._window_id, width=event.width)

    def _bind_mousewheel(self, _event=None) -> None:
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, _event=None) -> None:
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event) -> None:
        self.canvas.yview_scroll(int(-event.delta / 120), "units")

    def reset_scroll(self) -> None:
        self.canvas.yview_moveto(0)


class WorkspaceShell(ttk.Frame):
    def __init__(
        self,
        master,
        app_name: str,
        version: str,
        stop_command: Callable[[], None],
    ):
        super().__init__(master, style="Workspace.TFrame")
        self.pack(fill="both", expand=True)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = ttk.Frame(
            self, style="Sidebar.TFrame", width=250, padding=(16, 14)
        )
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)

        brand = ttk.Frame(self.sidebar, style="Sidebar.TFrame")
        brand.grid(row=0, column=0, sticky="ew", padx=6, pady=(2, 13))
        ttk.Label(brand, text="N", style="BrandMark.TLabel").grid(
            row=0, column=0, rowspan=2, padx=(0, 11)
        )
        ttk.Label(brand, text=app_name, style="BrandTitle.TLabel").grid(
            row=0, column=1, sticky="sw"
        )
        ttk.Label(brand, text=version, style="BrandMeta.TLabel").grid(
            row=1, column=1, sticky="nw"
        )

        self.page_host = ttk.Frame(self, style="Workspace.TFrame")
        self.page_host.grid(row=0, column=1, sticky="nsew")
        self.page_host.grid_rowconfigure(0, weight=1)
        self.page_host.grid_columnconfigure(0, weight=1)

        self.status_bar = ttk.Frame(
            self, style="StatusBar.TFrame", padding=(20, 9)
        )
        self.status_bar.place(relx=0, rely=1, anchor="sw", relwidth=1)
        self.status_bar.lift()
        self.status_bar.grid_columnconfigure(1, weight=1)
        self._status_dot = ttk.Label(
            self.status_bar, text="●", style="StatusDotIdle.TLabel"
        )
        self._status_dot.grid(row=0, column=0, padx=(0, 8))
        self.status_label = ttk.Label(
            self.status_bar, text="空闲 · 可以启动任务", style="StatusText.TLabel"
        )
        self.status_label.grid(row=0, column=1, sticky="w")
        self.stop_button = ttk.Button(
            self.status_bar,
            text="停止当前任务",
            command=stop_command,
            style="Stop.TButton",
            state="disabled",
        )
        self.stop_button.grid(row=0, column=2)

        self._nav_row = 1
        self._pages: Dict[str, ScrollablePage] = {}
        self._buttons: Dict[str, ttk.Button] = {}
        self._active_key: Optional[str] = None

    def add_section(self, title: str) -> None:
        ttk.Label(self.sidebar, text=title.upper(), style="NavSection.TLabel").grid(
            row=self._nav_row,
            column=0,
            sticky="w",
            padx=12,
            pady=(4, 3),
        )
        self._nav_row += 1

    def add_page(
        self,
        key: str,
        nav_text: str,
        title: str,
        subtitle: str,
    ) -> ttk.Frame:
        page = ScrollablePage(self.page_host, title, subtitle)
        page.grid(row=0, column=0, sticky="nsew")
        page.grid_remove()

        button = ttk.Button(
            self.sidebar,
            text=nav_text,
            command=lambda page_key=key: self.show(page_key),
            style="Nav.TButton",
        )
        button.grid(row=self._nav_row, column=0, sticky="ew", pady=2)
        self._nav_row += 1
        self._pages[key] = page
        self._buttons[key] = button
        return page.content

    def show(self, key: str) -> None:
        if key not in self._pages:
            return
        if self._active_key:
            self._pages[self._active_key].grid_remove()
            self._buttons[self._active_key].configure(style="Nav.TButton")
        self._active_key = key
        self._pages[key].grid()
        self._pages[key].tkraise()
        self._pages[key].reset_scroll()
        self._buttons[key].configure(style="NavActive.TButton")

    def set_task_status(self, active_name: Optional[str]) -> None:
        if active_name:
            self._status_dot.configure(style="StatusDotBusy.TLabel")
            self.status_label.configure(text=f"运行中 · {active_name}")
            self.stop_button.configure(state="normal")
        else:
            self._status_dot.configure(style="StatusDotIdle.TLabel")
            self.status_label.configure(text="空闲 · 可以启动任务")
            self.stop_button.configure(state="disabled")
