import time
import psutil
import os


class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
        self.process = psutil.Process(os.getpid())

    def measure(self, task_name):
        return TaskTimer(self, task_name)

    def record(self, task_name, duration, memory_diff):
        self.metrics[task_name] = {
            "latency_sec": round(duration, 4),
            "ram_change_mb": round(memory_diff, 2),
        }

    def get_summary(self):
        return self.metrics


class TaskTimer:
    def __init__(self, monitor, task_name):
        self.monitor = monitor
        self.task_name = task_name
        self.start_time = 0
        self.start_ram = 0

    def __enter__(self):
        self.start_time = time.perf_counter()
        self.start_ram = self.monitor.process.memory_info().rss / (1024 * 1024)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.perf_counter() - self.start_time
        ram_diff = (self.monitor.process.memory_info().rss / (1024 * 1024)) - self.start_ram
        self.monitor.record(self.task_name, duration, ram_diff)

