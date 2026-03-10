import tkinter as tk
from tkinter.scrolledtext import ScrolledText


def create_conversation_text(root):
    conversation_text = ScrolledText(
        root,
        state='disabled',
        width=100,
        height=20,
        wrap="word",
        bg='#262626',
        fg='white',
        font=("Segoe UI", 12)
    )
    conversation_text.pack(padx=10, pady=10)

    conversation_text.tag_configure("AI_Tag", foreground="#00FF00")
    conversation_text.tag_configure("Me_Tag", foreground="#00BFFF")
    conversation_text.tag_configure("Client_Tag", foreground="#FFA500")
    conversation_text.tag_configure("code",
        background="#1E1E1E",
        foreground="#D4D4D4",
        font=("Consolas", 12),
        relief="solid",
        borderwidth=1,
        spacing1=10,
        spacing3=10,
        rmargin=10
    )

    return conversation_text


def create_info_label(root):
    info_label = tk.Label(
        root,
        text="",
        bg='#262626',
        fg="white",
        font=("Segoe UI", 12)
    )
    info_label.pack(side='top', pady=5)
    return info_label


def _create_radio_group(parent, label, options, default, on_change):
    """Create a labeled group of radio buttons."""
    frame = tk.Frame(parent, bg='#1E1E1E')
    frame.pack(side='left', padx=20, pady=10)

    tk.Label(
        frame, text=label, bg='#1E1E1E', fg='white', font=("Segoe UI", 12)
    ).pack(anchor='w')

    selected = tk.StringVar(value=default)

    def on_select():
        if on_change:
            on_change(selected.get())

    for option_text, option_value in options:
        tk.Radiobutton(
            frame,
            text=option_text,
            variable=selected,
            value=option_value,
            command=on_select,
            bg='#1E1E1E',
            fg='white',
            selectcolor='#262626',
            activebackground='#1E1E1E',
            font=("Segoe UI", 12)
        ).pack(anchor='w')

    return frame, selected


def create_settings_panel(root, on_language_change=None, on_framework_change=None, on_mode_change=None):
    settings_panel = tk.Frame(root, bg='#1E1E1E', height=100)

    toggle_button = tk.Label(
        root, text="▼", bg='#262626', fg='white', cursor='hand2'
    )
    toggle_button.pack(side='bottom', pady=0)

    _, selected_lang = _create_radio_group(
        settings_panel, "Language:",
        [("English", "en"), ("Serbian", "sr")],
        "en", on_language_change
    )

    _, selected_framework = _create_radio_group(
        settings_panel, "Framework:",
        [("Python", "Python"), ("SQL", "SQL")],
        "Python", on_framework_change
    )

    _, selected_mode = _create_radio_group(
        settings_panel, "Interview Mode:",
        [("Standard", "Standard"), ("Case Study", "Case Study")],
        "Standard", on_mode_change
    )

    settings_panel.is_visible = False

    def toggle_panel(event):
        if not settings_panel.is_visible:
            settings_panel.pack(side='bottom', fill='x', before=toggle_button)
            toggle_button.configure(text="▲")
        else:
            settings_panel.pack_forget()
            toggle_button.configure(text="▼")
        settings_panel.is_visible = not settings_panel.is_visible

    toggle_button.bind('<Button-1>', toggle_panel)

    return settings_panel, selected_lang, selected_framework, selected_mode
