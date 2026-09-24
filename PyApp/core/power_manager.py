import subprocess

class PowerManager:
    @staticmethod
    def apply_optimal_policy():
        # High performance plan GUID (standard)
        high_perf_guid = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
        subprocess.run(["powercfg", "-setactive", high_perf_guid], capture_output=True)
        
        # CPU core parking attributes
        # 100% min state, disable core parking, etc.
        try:
            # Short and long thread scheduling to prefer performant (P-cores)
            subprocess.run(["powercfg", "-setacvalueindex", "SCHEME_CURRENT", "SUB_PROCESSOR", "SHORTTHREAD", "2"], capture_output=True)
            subprocess.run(["powercfg", "-setacvalueindex", "SCHEME_CURRENT", "SUB_PROCESSOR", "HETEROPOLICY", "4"], capture_output=True)
            subprocess.run(["powercfg", "-setactive", "SCHEME_CURRENT"], capture_output=True)
            return True, "Đã áp dụng tối ưu Kernel Power Policy thành công!"
        except Exception as e:
            return False, str(e)
