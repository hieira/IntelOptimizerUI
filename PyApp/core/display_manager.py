import win32api
import win32con

class DisplayManager:
    @staticmethod
    def apply_resolution(width, height, refresh_rate):
        try:
            devmode = win32api.EnumDisplaySettings(None, win32con.ENUM_CURRENT_SETTINGS)
            devmode.PelsWidth = width
            devmode.PelsHeight = height
            devmode.DisplayFrequency = refresh_rate
            devmode.Fields = win32con.DM_PELSWIDTH | win32con.DM_PELSHEIGHT | win32con.DM_DISPLAYFREQUENCY

            flags = win32con.CDS_UPDATEREGISTRY | win32con.CDS_GLOBAL
            res = win32api.ChangeDisplaySettings(devmode, flags)
            
            return res == win32con.DISP_CHANGE_SUCCESSFUL
        except Exception:
            return False
