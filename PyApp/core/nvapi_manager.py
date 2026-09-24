import ctypes
from ctypes import wintypes
import math

class NvApiManager:
    _initialized = False
    _available = False
    _display_handles = []
    _initial_levels = {}
    
    _nvInit = None
    _nvEnumDisp = None
    _nvGetDvc = None
    _nvSetDvc = None

    class NV_DISPLAY_DVC_INFO(ctypes.Structure):
        _fields_ = [
            ("version", wintypes.DWORD),
            ("currentLevel", ctypes.c_int),
            ("minLevel", ctypes.c_int),
            ("maxLevel", ctypes.c_int),
        ]

    @classmethod
    def ensure_initialized(cls):
        if cls._initialized:
            return
        cls._initialized = True
        try:
            nvapi = ctypes.WinDLL("nvapi64.dll")
            nvapi_QueryInterface = nvapi.nvapi_QueryInterface
            nvapi_QueryInterface.restype = ctypes.c_void_p
            nvapi_QueryInterface.argtypes = [wintypes.DWORD]

            pInit = nvapi_QueryInterface(0x0150E828)
            if not pInit: return
            cls._nvInit = ctypes.CFUNCTYPE(ctypes.c_int)(pInit)
            
            if cls._nvInit() != 0: return

            pEnumDisp = nvapi_QueryInterface(0x9ABDD40D)
            pGetDvc = nvapi_QueryInterface(0x4085DE45)
            pSetDvc = nvapi_QueryInterface(0x172409B4)

            if not pEnumDisp or not pGetDvc or not pSetDvc:
                return

            cls._nvEnumDisp = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p))(pEnumDisp)
            cls._nvGetDvc = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(cls.NV_DISPLAY_DVC_INFO))(pGetDvc)
            cls._nvSetDvc = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_int)(pSetDvc)

            cls._display_handles = []
            idx = 0
            hDisp = ctypes.c_void_p()
            while cls._nvEnumDisp(idx, ctypes.byref(hDisp)) == 0 and hDisp.value is not None:
                cls._display_handles.append(hDisp.value)
                
                info = cls.NV_DISPLAY_DVC_INFO()
                info.version = ctypes.sizeof(cls.NV_DISPLAY_DVC_INFO) | 0x10000
                
                if cls._nvGetDvc(hDisp, 0, ctypes.byref(info)) == 0:
                    cls._initial_levels[hDisp.value] = info.currentLevel
                else:
                    cls._initial_levels[hDisp.value] = 0
                
                idx += 1
            
            cls._available = len(cls._display_handles) > 0
        except Exception:
            cls._available = False

    @classmethod
    def is_available(cls):
        cls.ensure_initialized()
        return cls._available

    @classmethod
    def set_vibrance_percent(cls, percentage):
        if not cls.is_available(): return False
        
        level = 0
        if percentage > 50:
            level = int(round((percentage - 50.0) / 50.0 * 63.0))
        level = max(0, min(63, level))
        
        success = False
        for hDisp in cls._display_handles:
            h = ctypes.c_void_p(hDisp)
            res = cls._nvSetDvc(h, 0, level)
            if res == 0:
                success = True
        return success
