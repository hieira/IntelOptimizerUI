import json
import os
import psutil
from psutil import BELOW_NORMAL_PRIORITY_CLASS, HIGH_PRIORITY_CLASS

class ProcessAffinityManager:
    @staticmethod
    def quick_apply(p_mask, e_mask):
        success_count = 0
        try:
            games = ["csgo.exe", "valorant.exe", "dota2.exe", "cs2.exe"]
            bg_apps = ["chrome.exe", "discord.exe", "spotify.exe", "msedge.exe", "obs64.exe"]
            
            try:
                config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.json')
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    games = config.get('HighPriority_Games', games)
                    bg_apps = config.get('Background_Apps', bg_apps)
            except Exception:
                pass
            
            games = [g.lower() for g in games]
            bg_apps = [g.lower() for g in bg_apps]
            
            for p in psutil.process_iter(['pid', 'name']):
                name = p.info['name'].lower() if p.info['name'] else ""
                try:
                    if name in games:
                        # Convert mask to list of cores
                        cores = ProcessAffinityManager.mask_to_list(p_mask)
                        p.cpu_affinity(cores)
                        p.nice(HIGH_PRIORITY_CLASS)
                        success_count += 1
                    elif name in bg_apps:
                        # For browsers/electron apps, locking solely to E-cores causes heavy UI lag.
                        # Best practice: Do not lock affinity (or give E-cores + 2 P-cores).
                        # Here, we just lower priority and let Windows Thread Director handle it.
                        p.nice(BELOW_NORMAL_PRIORITY_CLASS)
                        
                        # Optionally, we can assign E-Cores + 1 P-Core (Thread 0 and 1) to avoid total starvation
                        cores = ProcessAffinityManager.mask_to_list(e_mask)
                        # Add first P-Core (thread 0 and 1) if not already in cores
                        if 0 not in cores: cores.append(0)
                        if 1 not in cores: cores.append(1)
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

