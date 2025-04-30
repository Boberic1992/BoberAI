from ctypes import windll
import win32con

def make_window_capture_invisible(root):
    try:
        root.update_idletasks()
        hwnd = windll.user32.GetParent(root.winfo_id())
        
        # Store current window settings
        alpha = root.attributes('-alpha')
        
        # Apply capture protection
        style = windll.user32.GetWindowLongA(hwnd, win32con.GWL_EXSTYLE)
        style |= win32con.WS_EX_LAYERED | win32con.WS_EX_TOOLWINDOW
        windll.user32.SetWindowLongA(hwnd, win32con.GWL_EXSTYLE, style)
        windll.user32.SetWindowDisplayAffinity(hwnd, 0x00000011)
        
        # Reapply transparency without disturbing capture protection
        root.attributes('-alpha', alpha)
        
        current = windll.user32.GetWindowDisplayAffinity(hwnd)
        if current != 0x00000011:
            root.after(50, lambda: make_window_capture_invisible(root))
    except Exception as e:
        print(f"Failed to set window capture invisibility: {e}")
        root.after(50, lambda: make_window_capture_invisible(root))
        
def setup_window(root, resource_path):
    # Initialize window properties
    root.withdraw()
    root.after(100, lambda: (
        make_window_capture_invisible(root),
        root.deiconify()
    ))
    
    # Set window properties
    root.after(0, lambda: root.attributes('-alpha', 0.8))
    root.attributes('-fullscreen', False)
    root.attributes('-topmost', True)
    root.title("BoberAI")
    root.configure(bg='#262626')
    root.resizable(False, False)
    root.tk.call('tk', 'scaling', 1.5)
    
    return root