from ctypes import windll

import win32con


def make_window_capture_invisible(root):
    try:
        root.update_idletasks()
        hwnd = windll.user32.GetParent(root.winfo_id())

        if hwnd:
            style = windll.user32.GetWindowLongA(hwnd, win32con.GWL_EXSTYLE)
            style |= win32con.WS_EX_LAYERED | win32con.WS_EX_TOOLWINDOW
            windll.user32.SetWindowLongA(hwnd, win32con.GWL_EXSTYLE, style)
            # Prevent window from appearing in screen captures/recordings
            windll.user32.SetWindowDisplayAffinity(hwnd, 0x00000011)

            alpha = root.attributes('-alpha')
            root.attributes('-alpha', alpha)
    except Exception as e:
        print(f"Failed to set window capture invisibility: {e}")


def setup_window(root, resource_path):
    root.withdraw()
    root.after(100, lambda: (
        make_window_capture_invisible(root),
        root.deiconify()
    ))

    root.after(0, lambda: root.attributes('-alpha', 0.8))
    root.attributes('-fullscreen', False)
    root.attributes('-topmost', True)
    root.title("BoberAI")
    root.configure(bg='#262626')
    root.resizable(False, False)
    root.tk.call('tk', 'scaling', 1.5)

    return root
