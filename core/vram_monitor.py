from pynvml import *

class VRAMMonitor:
    def __init__(self):
        nvmlInit()
        self.handle = nvmlDeviceGetHandleByIndex(0)

    def get_usage(self):
        info = nvmlDeviceGetMemoryInfo(self.handle)

        return {
            "used_gb": round(info.used / 1024**3, 2),
            "total_gb": round(info.total / 1024**3, 2)
        }
