import psutil
import wmi

class CpuTopology:
    def __init__(self):
        self.logical_cores = psutil.cpu_count(logical=True)
        self.physical_cores = psutil.cpu_count(logical=False)
        self.p_cores = 0
        self.e_cores = 0
        self.p_core_mask = 0
        self.e_core_mask = 0
        self.name = "Unknown CPU"
        self.detect()

    def detect(self):
        try:
            c = wmi.WMI()
            processors = c.Win32_Processor()
            if processors:
                self.name = processors[0].Name
        except Exception:
            pass
        
        # Alder/Raptor Lake heuristic
        # If logical > physical, then (logical - physical) are hyperthreaded P-cores.
        if self.logical_cores > self.physical_cores:
            self.p_cores = self.logical_cores - self.physical_cores
            self.e_cores = self.physical_cores - self.p_cores
        else:
            self.p_cores = self.physical_cores
            self.e_cores = 0
            
        # P-Core mask calculation (Assume P-cores are first N logical threads, hyperthreaded)
        # 12 P-core threads -> 0x0FFF
        # 8 E-core threads -> 0xFF000
        p_threads = self.p_cores * 2 if self.logical_cores > self.physical_cores else self.p_cores
        e_threads = self.e_cores
        
        self.p_core_mask = (1 << p_threads) - 1
        self.e_core_mask = ((1 << e_threads) - 1) << p_threads

if __name__ == "__main__":
    t = CpuTopology()
    print(f"CPU: {t.name}")
    print(f"Physical: {t.physical_cores}, Logical: {t.logical_cores}")
    print(f"P-Cores: {t.p_cores}, E-Cores: {t.e_cores}")
    print(f"P-Core Mask: {hex(t.p_core_mask)}, E-Core Mask: {hex(t.e_core_mask)}")
