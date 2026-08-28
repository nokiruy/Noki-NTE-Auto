"""Noki NTE Auto 的统一 Tkinter 视觉主题。

主程序的任务逻辑历史较长，混用了 ttk 与原生 tk 控件。这个模块集中处理颜色、
字体和控件状态，让界面可以逐步重构，而不必碰任务执行代码。
"""

from __future__ import annotations

import tkinter as tk
from tkinter import font, ttk


COLORS = {
    "background": "#EEF2F7",
    "surface": "#FFFFFF",
    "surface_alt": "#EAF0F7",
    "surface_hover": "#E2EAF4",
    "text": "#172033",
    "muted": "#667085",
    "subtle": "#98A2B3",
    "border": "#D8E1EC",
    "accent": "#2563EB",
    "accent_hover": "#1D4ED8",
    "accent_soft": "#DBEAFE",
    "cyan": "#0891B2",
    "success": "#15803D",
    "success_soft": "#DCFCE7",
    "warning": "#B45309",
    "danger": "#DC2626",
    "danger_hover": "#B91C1C",
    "danger_soft": "#FEE2E2",
    "sidebar": "#121A2A",
    "sidebar_hover": "#1C2940",
    "sidebar_active": "#253858",
    "sidebar_text": "#DDE7F5",
    "sidebar_muted": "#7F91AA",
    "status": "#0E1624",
}

FONT_FAMILY = "Microsoft YaHei UI"


def apply_modern_theme(root: tk.Misc, style: ttk.Style | None = None) -> ttk.Style:
    """应用轻量、清晰的现代浅色主题。"""
    style = style or ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    root.configure(background=COLORS["background"])
    root.option_add("*Font", (FONT_FAMILY, 10))
    root.option_add("*tearOff", False)
    root.option_add("*TCombobox*Listbox.font", (FONT_FAMILY, 10))
    root.option_add("*TCombobox*Listbox.background", COLORS["surface"])
    root.option_add("*TCombobox*Listbox.foreground", COLORS["text"])
    root.option_add("*TCombobox*Listbox.selectBackground", COLORS["accent"])
    root.option_add("*TCombobox*Listbox.selectForeground", "#FFFFFF")

    style.configure(".", font=(FONT_FAMILY, 10))
    style.configure("App.TFrame", background=COLORS["background"])
    style.configure("Workspace.TFrame", background=COLORS["background"])
    style.configure("TFrame", background=COLORS["surface"])
    style.configure("Card.TFrame", background=COLORS["surface"])
    style.configure("Sidebar.TFrame", background=COLORS["sidebar"])
    style.configure("StatusBar.TFrame", background=COLORS["status"])
    style.configure(
        "Header.TFrame",
        background=COLORS["surface"],
        relief="solid",
        borderwidth=1,
    )

    style.configure(
        "TLabel",
        background=COLORS["surface"],
        foreground=COLORS["text"],
    )
    style.configure(
        "Card.TLabel",
        background=COLORS["surface"],
        foreground=COLORS["text"],
    )
    style.configure(
        "HeaderTitle.TLabel",
        background=COLORS["surface"],
        foreground=COLORS["text"],
        font=(FONT_FAMILY, 17, "bold"),
    )
    style.configure(
        "HeaderSubtitle.TLabel",
        background=COLORS["surface"],
        foreground=COLORS["muted"],
        font=(FONT_FAMILY, 9),
    )
    style.configure(
        "PageTitle.TLabel",
        background=COLORS["background"],
        foreground=COLORS["text"],
        font=(FONT_FAMILY, 24, "bold"),
    )
    style.configure(
        "PageSubtitle.TLabel",
        background=COLORS["background"],
        foreground=COLORS["muted"],
        font=(FONT_FAMILY, 10),
    )
    style.configure(
        "BrandMark.TLabel",
        background=COLORS["accent"],
        foreground="#FFFFFF",
        font=(FONT_FAMILY, 16, "bold"),
        padding=(10, 7),
    )
    style.configure(
        "BrandTitle.TLabel",
        background=COLORS["sidebar"],
        foreground="#FFFFFF",
        font=(FONT_FAMILY, 11, "bold"),
    )
    style.configure(
        "BrandMeta.TLabel",
        background=COLORS["sidebar"],
        foreground=COLORS["sidebar_muted"],
        font=(FONT_FAMILY, 8),
    )
    style.configure(
        "NavSection.TLabel",
        background=COLORS["sidebar"],
        foreground=COLORS["sidebar_muted"],
        font=(FONT_FAMILY, 8, "bold"),
    )
    style.configure(
        "StatusText.TLabel",
        background=COLORS["status"],
        foreground=COLORS["sidebar_text"],
        font=(FONT_FAMILY, 9),
    )
    style.configure(
        "StatusDotIdle.TLabel",
        background=COLORS["status"],
        foreground="#4DD6A1",
        font=(FONT_FAMILY, 10, "bold"),
    )
    style.configure(
        "StatusDotBusy.TLabel",
        background=COLORS["status"],
        foreground="#FFB454",
        font=(FONT_FAMILY, 10, "bold"),
    )
    style.configure(
        "Section.TLabel",
        background=COLORS["background"],
        foreground=COLORS["text"],
        font=(FONT_FAMILY, 13, "bold"),
    )
    style.configure(
        "CardSection.TLabel",
        background=COLORS["surface"],
        foreground=COLORS["text"],
        font=(FONT_FAMILY, 12, "bold"),
    )
    style.configure(
        "Muted.TLabel",
        background=COLORS["background"],
        foreground=COLORS["muted"],
        font=(FONT_FAMILY, 9),
    )
    style.configure(
        "CardMuted.TLabel",
        background=COLORS["surface"],
        foreground=COLORS["muted"],
        font=(FONT_FAMILY, 9),
    )
    style.configure(
        "Badge.TLabel",
        background=COLORS["accent_soft"],
        foreground=COLORS["accent"],
        font=(FONT_FAMILY, 9, "bold"),
        padding=(10, 5),
    )
    style.configure(
        "SuccessBadge.TLabel",
        background=COLORS["success_soft"],
        foreground=COLORS["success"],
        font=(FONT_FAMILY, 9, "bold"),
        padding=(10, 5),
    )
    style.configure(
        "Danger.TLabel",
        background=COLORS["background"],
        foreground=COLORS["danger"],
        font=(FONT_FAMILY, 10, "bold"),
    )

    style.configure(
        "TLabelframe",
        background=COLORS["surface"],
        bordercolor=COLORS["border"],
        lightcolor=COLORS["border"],
        darkcolor=COLORS["border"],
        relief="solid",
        borderwidth=1,
        padding=(12, 10),
    )
    style.configure(
        "TLabelframe.Label",
        background=COLORS["surface"],
        foreground=COLORS["text"],
        font=(FONT_FAMILY, 10, "bold"),
        padding=(2, 0),
    )

    style.configure(
        "TButton",
        background=COLORS["surface"],
        foreground=COLORS["text"],
        bordercolor=COLORS["border"],
        lightcolor=COLORS["border"],
        darkcolor=COLORS["border"],
        relief="flat",
        borderwidth=1,
        focusthickness=0,
        focuscolor=COLORS["surface"],
        padding=(12, 8),
        font=(FONT_FAMILY, 10, "bold"),
    )
    style.map(
        "TButton",
        background=[
            ("disabled", COLORS["surface_alt"]),
            ("pressed", COLORS["surface_hover"]),
            ("active", COLORS["surface_alt"]),
        ],
        foreground=[
            ("disabled", COLORS["subtle"]),
            ("active", COLORS["accent"]),
        ],
        bordercolor=[("active", COLORS["accent"])],
    )
    style.configure(
        "Primary.TButton",
        background=COLORS["accent"],
        foreground="#FFFFFF",
        bordercolor=COLORS["accent"],
        lightcolor=COLORS["accent"],
        darkcolor=COLORS["accent"],
        padding=(14, 9),
    )
    style.map(
        "Primary.TButton",
        background=[
            ("disabled", "#AFC6F8"),
            ("pressed", COLORS["accent_hover"]),
            ("active", COLORS["accent_hover"]),
        ],
        foreground=[("disabled", "#EFF6FF"), ("active", "#FFFFFF")],
        bordercolor=[("active", COLORS["accent_hover"])],
    )
    style.configure(
        "Danger.TButton",
        background=COLORS["danger_soft"],
        foreground=COLORS["danger"],
        bordercolor="#FECACA",
        lightcolor="#FECACA",
        darkcolor="#FECACA",
        padding=(14, 9),
    )
    style.map(
        "Danger.TButton",
        background=[
            ("pressed", "#FECACA"),
            ("active", "#FECACA"),
        ],
        foreground=[("active", COLORS["danger_hover"])],
    )
    style.configure(
        "Task.TButton",
        background=COLORS["surface"],
        foreground=COLORS["text"],
        bordercolor=COLORS["border"],
        lightcolor=COLORS["border"],
        darkcolor=COLORS["border"],
        anchor="w",
        padding=(14, 11),
    )
    style.map(
        "Task.TButton",
        background=[("pressed", COLORS["accent_soft"]), ("active", COLORS["accent_soft"])],
        foreground=[("active", COLORS["accent"])],
        bordercolor=[("active", "#93B4F8")],
    )
    style.configure(
        "Icon.TButton",
        background=COLORS["surface_alt"],
        foreground=COLORS["muted"],
        bordercolor=COLORS["border"],
        padding=(7, 5),
        font=(FONT_FAMILY, 9, "bold"),
    )
    style.map(
        "Icon.TButton",
        background=[("pressed", COLORS["accent_soft"]), ("active", COLORS["accent_soft"])],
        foreground=[("active", COLORS["accent"])],
    )
    style.configure(
        "Nav.TButton",
        background=COLORS["sidebar"],
        foreground=COLORS["sidebar_text"],
        bordercolor=COLORS["sidebar"],
        lightcolor=COLORS["sidebar"],
        darkcolor=COLORS["sidebar"],
        relief="flat",
        borderwidth=0,
        anchor="w",
        padding=(13, 5),
        font=(FONT_FAMILY, 10),
    )
    style.map(
        "Nav.TButton",
        background=[("pressed", COLORS["sidebar_hover"]), ("active", COLORS["sidebar_hover"])],
        foreground=[("active", "#FFFFFF")],
        bordercolor=[("active", COLORS["sidebar_hover"])],
    )
    style.configure(
        "NavActive.TButton",
        background=COLORS["sidebar_active"],
        foreground="#FFFFFF",
        bordercolor=COLORS["sidebar_active"],
        lightcolor=COLORS["sidebar_active"],
        darkcolor=COLORS["sidebar_active"],
        relief="flat",
        borderwidth=0,
        anchor="w",
        padding=(13, 5),
        font=(FONT_FAMILY, 10, "bold"),
    )
    style.map(
        "NavActive.TButton",
        background=[("active", COLORS["sidebar_active"])],
        foreground=[("active", "#FFFFFF")],
        bordercolor=[("active", COLORS["sidebar_active"])],
    )
    style.configure(
        "Stop.TButton",
        background="#7B2937",
        foreground="#FFFFFF",
        bordercolor="#7B2937",
        lightcolor="#7B2937",
        darkcolor="#7B2937",
        relief="flat",
        borderwidth=0,
        padding=(13, 6),
        font=(FONT_FAMILY, 9, "bold"),
    )
    style.map(
        "Stop.TButton",
        background=[("active", "#9C3445"), ("disabled", "#293343")],
        foreground=[("disabled", "#78869A")],
        bordercolor=[("disabled", "#293343")],
    )

    style.configure(
        "TNotebook",
        background=COLORS["background"],
        borderwidth=0,
        tabmargins=(0, 0, 12, 0),
    )
    style.configure(
        "TNotebook.Tab",
        background=COLORS["surface_alt"],
        foreground=COLORS["muted"],
        borderwidth=0,
        padding=(18, 13),
        font=(FONT_FAMILY, 10, "bold"),
        anchor="center",
    )
    style.map(
        "TNotebook.Tab",
        background=[
            ("selected", COLORS["surface"]),
            ("active", COLORS["surface_hover"]),
        ],
        foreground=[
            ("selected", COLORS["accent"]),
            ("active", COLORS["text"]),
        ],
        expand=[("selected", (0, 0, 0, 0))],
    )

    for widget_style in ("TEntry", "TCombobox", "TSpinbox"):
        style.configure(
            widget_style,
            fieldbackground=COLORS["surface"],
            background=COLORS["surface"],
            foreground=COLORS["text"],
            bordercolor=COLORS["border"],
            lightcolor=COLORS["border"],
            darkcolor=COLORS["border"],
            arrowcolor=COLORS["muted"],
            insertcolor=COLORS["text"],
            relief="flat",
            borderwidth=1,
            padding=(8, 6),
        )
        style.map(
            widget_style,
            bordercolor=[("focus", COLORS["accent"]), ("active", COLORS["accent"])],
            lightcolor=[("focus", COLORS["accent"])],
            darkcolor=[("focus", COLORS["accent"])],
        )

    style.configure(
        "TCheckbutton",
        background=COLORS["surface"],
        foreground=COLORS["text"],
        padding=(2, 4),
    )
    style.map(
        "TCheckbutton",
        foreground=[("disabled", COLORS["subtle"]), ("active", COLORS["accent"])],
        background=[("active", COLORS["surface"])],
    )
    style.configure(
        "TRadiobutton",
        background=COLORS["surface"],
        foreground=COLORS["text"],
        padding=(2, 4),
    )
    style.map(
        "TRadiobutton",
        foreground=[("active", COLORS["accent"])],
        background=[("active", COLORS["surface"])],
    )
    style.configure(
        "TSeparator",
        background=COLORS["border"],
    )

    return style


def _surface_for(widget: tk.Misc) -> str:
    """根据祖先容器，判断原生 tk 控件应使用卡片还是页面背景。"""
    current = getattr(widget, "master", None)
    while current is not None:
        try:
            if current.winfo_class() == "TLabelframe":
                return COLORS["surface"]
            if isinstance(current, ttk.Frame):
                frame_style = current.cget("style")
                if frame_style not in {"Workspace.TFrame", "App.TFrame"}:
                    return COLORS["surface"]
        except (tk.TclError, AttributeError):
            pass
        current = getattr(current, "master", None)
    return COLORS["background"]


def _cap_font(widget: tk.Misc, maximum: int = 12) -> None:
    """压住旧界面里 16~20px 的失控字号，同时保留粗体和斜体。"""
    try:
        actual = font.Font(root=widget, font=widget.cget("font")).actual()
        size = abs(int(actual.get("size", 10)))
        styles = []
        if actual.get("weight") == "bold":
            styles.append("bold")
        if actual.get("slant") == "italic":
            styles.append("italic")
        widget.configure(
            font=(
                FONT_FAMILY,
                min(size, maximum),
                " ".join(styles) or "normal",
            )
        )
    except (tk.TclError, TypeError, ValueError):
        pass


def polish_legacy_widgets(root: tk.Misc) -> None:
    """统一主程序中遗留的 tk.Label/Entry/Spinbox/Text 等原生控件。"""
    try:
        children = root.winfo_children()
    except tk.TclError:
        return

    for widget in children:
        surface = _surface_for(widget)
        widget_class = widget.winfo_class()

        try:
            if widget_class == "Label":
                widget.configure(background=surface)
                foreground = str(widget.cget("foreground")).lower()
                color_map = {
                    "red": COLORS["danger"],
                    "#ff0000": COLORS["danger"],
                    "blue": COLORS["accent"],
                    "#0000ff": COLORS["accent"],
                    "green": COLORS["success"],
                    "#008000": COLORS["success"],
                    "gray": COLORS["muted"],
                    "grey": COLORS["muted"],
                }
                widget.configure(foreground=color_map.get(foreground, COLORS["text"]))
                _cap_font(widget)

            elif widget_class in {"Entry", "Spinbox"}:
                widget.configure(
                    background=COLORS["surface"],
                    foreground=COLORS["text"],
                    insertbackground=COLORS["text"],
                    disabledbackground=COLORS["surface_alt"],
                    disabledforeground=COLORS["subtle"],
                    relief="flat",
                    highlightthickness=1,
                    highlightbackground=COLORS["border"],
                    highlightcolor=COLORS["accent"],
                )
                _cap_font(widget, 11)

            elif widget_class == "Text":
                widget.configure(
                    background=COLORS["surface"],
                    foreground=COLORS["text"],
                    insertbackground=COLORS["text"],
                    selectbackground=COLORS["accent_soft"],
                    selectforeground=COLORS["text"],
                    relief="flat",
                    borderwidth=0,
                    highlightthickness=1,
                    highlightbackground=COLORS["border"],
                    highlightcolor=COLORS["accent"],
                    padx=8,
                    pady=7,
                )
                _cap_font(widget, 11)

            elif widget_class in {"Checkbutton", "Radiobutton"}:
                widget.configure(
                    background=surface,
                    foreground=COLORS["text"],
                    activebackground=surface,
                    activeforeground=COLORS["accent"],
                    selectcolor=surface,
                    highlightthickness=0,
                    borderwidth=0,
                )
                _cap_font(widget, 11)

            elif widget_class == "Button":
                text = str(widget.cget("text"))
                is_primary = "启用" in text or "启动" in text
                widget.configure(
                    background=COLORS["accent"] if is_primary else COLORS["surface"],
                    foreground="#FFFFFF" if is_primary else COLORS["text"],
                    activebackground=COLORS["accent_hover"] if is_primary else COLORS["surface_alt"],
                    activeforeground="#FFFFFF" if is_primary else COLORS["accent"],
                    relief="flat",
                    borderwidth=0,
                    cursor="hand2",
                    padx=12,
                    pady=7,
                    highlightthickness=0,
                )
                _cap_font(widget, 10)
        except tk.TclError:
            pass

        polish_legacy_widgets(widget)
