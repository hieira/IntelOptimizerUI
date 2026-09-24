import ctypes
import psutil

class MemoryManager:
    @staticmethod
    def reduce_memory():
        try:
            import win32security
            import win32api
            import win32con
            
            # Enable SeProfileSingleProcessPrivilege
            priv_flags = win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY
            hToken = win32security.OpenProcessToken(win32api.GetCurrentProcess(), priv_flags)
            priv_id = win32security.LookupPrivilegeValue(None, win32security.SE_PROF_SINGLE_PROCESS_NAME)
            win32security.AdjustTokenPrivileges(hToken, 0, [(priv_id, win32security.SE_PRIVILEGE_ENABLED)])
            
            # Empty working sets for all processes
            for p in psutil.process_iter(['pid']):
                try:
                    handle = ctypes.windll.kernel32.OpenProcess(0x0400 | 0x0100, False, p.info['pid'])
                    if handle:
                        ctypes.windll.psapi.EmptyWorkingSet(handle)
                        ctypes.windll.kernel32.CloseHandle(handle)
                except Exception:
                    continue
                    
            # Clear Standby List (SystemMemoryListInformation = 80, MemoryPurgeStandbyList = 4)
            SYSTEM_MEMORY_LIST_INFORMATION = 80
            MEMORY_PURGE_STANDBY_LIST = 4
            
            command = ctypes.c_int(MEMORY_PURGE_STANDBY_LIST)
            ctypes.windll.ntdll.NtSetSystemInformation(
                SYSTEM_MEMORY_LIST_INFORMATION,
                ctypes.byref(command),
                ctypes.sizeof(command)
            )
            
            return True
        except Exception as e:
            print("Reduce Memory Error:", e)
            return False
