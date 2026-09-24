import ctypes
from ctypes import wintypes
import math
import win32api
import win32con

class ColorManager:
    _default_ramp = None
    _current_ramp = None

    @classmethod
    def get_dc(cls):
        return ctypes.windll.user32.GetDC(0)

    @classmethod
    def release_dc(cls, hdc):
        ctypes.windll.user32.ReleaseDC(0, hdc)

    @classmethod
    def init_default_ramp(cls):
        if cls._default_ramp is not None: return
        hdc = cls.get_dc()
        ramp = (wintypes.WORD * 768)()
        res = ctypes.windll.gdi32.GetDeviceGammaRamp(hdc, ctypes.byref(ramp))
        cls.release_dc(hdc)
        if res:
            cls._default_ramp = ramp
        else:
            # Fallback linear ramp
            ramp = (wintypes.WORD * 768)()
            for i in range(256):
                val = min(65535, i * 256)
                ramp[i] = val
                ramp[i + 256] = val
                ramp[i + 512] = val
            cls._default_ramp = ramp

    @classmethod
    def restore_default(cls):
        if cls._default_ramp is None: return
        hdc = cls.get_dc()
        ctypes.windll.gdi32.SetDeviceGammaRamp(hdc, ctypes.byref(cls._default_ramp))
        cls.release_dc(hdc)
        from core.nvapi_manager import NvApiManager
        NvApiManager.set_vibrance_percent(50) # default vibrance

    @classmethod
    def apply_color_profile(cls, brightness=0.0, contrast=1.0, gamma=1.0, r_gain=1.0, g_gain=1.0, b_gain=1.0, vibrance=50):
        cls.init_default_ramp()
        ramp = (wintypes.WORD * 768)()
        for i in range(256):
            # Normalize to 0-1
            val = i / 255.0
            
            # Apply Contrast
            val = (val - 0.5) * contrast + 0.5
            # Apply Brightness
            val = val + brightness
            # Apply Black Equalizer (Gamma)
            if val > 0:
                val = math.pow(val, 1.0 / max(0.01, gamma))
            
            val = max(0.0, min(1.0, val))

            # Apply RGB gains
            r = min(1.0, val * r_gain)
            g = min(1.0, val * g_gain)
            b = min(1.0, val * b_gain)

            ramp[i] = int(r * 65535)
            ramp[i + 256] = int(g * 65535)
            ramp[i + 512] = int(b * 65535)

        hdc = cls.get_dc()
        ctypes.windll.gdi32.SetDeviceGammaRamp(hdc, ctypes.byref(ramp))
        cls.release_dc(hdc)
        cls._current_ramp = ramp

        from core.nvapi_manager import NvApiManager
        NvApiManager.set_vibrance_percent(vibrance)
