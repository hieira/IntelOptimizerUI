import ctypes
from ctypes import wintypes
import threading
import json
import os
import psutil
from core.color_manager import ColorManager

# Constants for SetWinEventHook
EVENT_SYSTEM_FOREGROUND = 3
WINEVENT_OUTOFCONTEXT = 0

class ZeroBleedManager:
    _hook = None
    _hook_thread = None
    _is_running = False
    _games = []
    _active = False
    
    _current_profile = {
        'brightness': 0.0,
        'contrast': 1.0,
        'gamma': 1.0,
        'r_gain': 1.0,
        'g_gain': 1.0,
        'b_gain': 1.0,
        'vibrance': 50
    }

    @classmethod
    def set_profile(cls, **kwargs):
        cls._current_profile.update(kwargs)
        if cls._active:
            ColorManager.apply_color_profile(**cls._current_profile)

    @classmethod
    def load_games(cls):
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.json')
            with open(config_path, 'r') as f:
                config = json.load(f)
                cls._games = [g.lower() for g in config.get('HighPriority_Games', [])]
        except Exception:
            pass

    @classmethod
    def get_process_name_from_hwnd(cls, hwnd):
        pid = wintypes.DWORD()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value > 0:
            try:
                proc = psutil.Process(pid.value)
                return proc.name().lower()
            except Exception:
                pass
        return ""

    @classmethod
    def _event_hook_callback(cls, hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
        if event == EVENT_SYSTEM_FOREGROUND:
            exe_name = cls.get_process_name_from_hwnd(hwnd)
            if exe_name in cls._games:
                if not cls._active:
                    cls._active = True
                    ColorManager.apply_color_profile(**cls._current_profile)
            else:
                if cls._active:
                    cls._active = False
                    ColorManager.restore_default()

    @classmethod
    def start(cls):
        if cls._is_running: return
        cls.load_games()
        cls._is_running = True
        cls._active = False
        
        # Need a message loop for the hook to work
        def hook_thread_func():
            user32 = ctypes.windll.user32
            ole32 = ctypes.windll.ole32
            ole32.CoInitialize(0)
            
            WINFUNCTYPE = ctypes.WINFUNCTYPE(None, wintypes.HANDLE, wintypes.DWORD, wintypes.HWND, wintypes.LONG, wintypes.LONG, wintypes.DWORD, wintypes.DWORD)
            cls.WinEventProc = WINFUNCTYPE(cls._event_hook_callback)
            
            cls._hook = user32.SetWinEventHook(
                EVENT_SYSTEM_FOREGROUND, EVENT_SYSTEM_FOREGROUND,
                0, cls.WinEventProc, 0, 0, WINEVENT_OUTOFCONTEXT
            )
            
            msg = wintypes.MSG()
            while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
                if not cls._is_running:
                    break
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
            
            if cls._hook:
                user32.UnhookWinEvent(cls._hook)
                cls._hook = None
            ole32.CoUninitialize()

        cls._hook_thread = threading.Thread(target=hook_thread_func, daemon=True)
        cls._hook_thread.start()

    @classmethod
    def stop(cls):
        cls._is_running = False
        cls._active = False
        ColorManager.restore_default()
        # To break the message loop gracefully, we should post a quit message, but daemon thread will kill it anyway.
