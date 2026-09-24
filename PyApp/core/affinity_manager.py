import psutil

class ProcessAffinityManager:
    @staticmethod
    def quick_apply(p_mask, e_mask):
        success_count = 0
        try:
            # Example heuristic: assign typical games to P-Core, background to E-Core
            # For simplicity, we just list processes and their expected mask
            # P-Core = lower bits, E-Core = upper bits
            games = ["csgo.exe", "valorant.exe", "dota2.exe"]
            bg_apps = ["chrome.exe", "discord.exe", "spotify.exe"]
            
            for p in psutil.process_iter(['pid', 'name']):
                name = p.info['name'].lower() if p.info['name'] else ""
                try:
                    if name in games:
                        # Convert mask to list of cores
                        cores = ProcessAffinityManager.mask_to_list(p_mask)
                        p.cpu_affinity(cores)
                        success_count += 1
                    elif name in bg_apps:
                        cores = ProcessAffinityManager.mask_to_list(e_mask)
                        p.cpu_affinity(cores)
                        success_count += 1
                except Exception:
                    pass
        except Exception:
            pass
        return success_count

    @staticmethod
    def mask_to_list(mask):
        cores = []
        bit = 0
        while mask > 0:
            if mask & 1:
                cores.append(bit)
            mask >>= 1
            bit += 1
        return cores

    @staticmethod
    def get_process_list():
        proc_list = []
        # Get a subset to avoid lagging the UI
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                name = p.info['name']
                pid = p.info['pid']
                cpu = p.info['cpu_percent']
                if name and name != "System Idle Process":
                    aff = p.cpu_affinity()
                    aff_str = f"{len(aff)} Cores" if aff else "All"
                    proc_list.append({"pid": pid, "name": name, "cpu": cpu, "affinity": aff_str})
            except Exception:
                pass
        # Sort by CPU usage
        proc_list.sort(key=lambda x: x['cpu'] or 0, reverse=True)
        return proc_list[:50]  # Return top 50

