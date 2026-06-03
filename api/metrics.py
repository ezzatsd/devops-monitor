import psutil


def get_system_metrics() -> dict:
    """Return a non-blocking snapshot of local system metrics."""
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return {
        "cpu_percent": psutil.cpu_percent(interval=None),
        "memory_percent": memory.percent,
        "memory_used_gb": round(memory.used / 1e9, 2),
        "memory_total_gb": round(memory.total / 1e9, 2),
        "disk_percent": disk.percent,
    }
