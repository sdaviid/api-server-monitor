import time
import psutil
from threading import Thread
from app.config import DISK_MONITOR
from app.utils.utils import(
    frmt_speed,
    frmt_bytes
)






class Monitor(Thread):
    def __init__(self, disk=[]):
        Thread.__init__(self)
        self.disk = disk
        self.disk_space = {}
        self.cpu = {}
        self.ram = {}
        self.last_recv = psutil.net_io_counters().bytes_recv
        self.last_sent = psutil.net_io_counters().bytes_sent
        self.speed_recv = 0
        self.speed_sent = 0
        self.speed_sent_descr = 0
        self.speed_recv_descr = 0
    def update_bandwidth(self):
        current_recv = psutil.net_io_counters().bytes_recv
        current_sent = psutil.net_io_counters().bytes_sent
        if current_recv > self.last_recv:
            total_recv = current_recv - self.last_recv
        else:
            total_recv = self.last_recv - current_recv
        if current_sent > self.last_sent:
            total_sent = current_sent - self.last_sent
        else:
            total_sent = self.last_sent - current_sent
        self.speed_recv = total_recv
        self.speed_sent = total_sent
        self.last_recv = current_recv
        self.last_sent = current_sent
        self.speed_sent_descr = frmt_speed(self.speed_sent),
        self.speed_recv_descr = frmt_speed(self.speed_recv)
    def update_disk(self):
        for disk in self.disk:
            hdd = psutil.disk_usage(disk)
            self.disk_space.update(
                {
                    disk: {
                        'total': hdd.total / (2**30),
                        'free': hdd.free / (2**30),
                        'used': hdd.used / (2**30),
                        'total_descr': frmt_bytes(hdd.total),
                        'free_descr': frmt_bytes(hdd.free),
                        'used_descr': frmt_bytes(hdd.used)
                    }
                }
            )
    def update_cpu(self):
        self.cpu.update({'total': psutil.cpu_count(), 'using_percent': psutil.cpu_percent()})
    def update_ram(self):
        status = psutil.virtual_memory()
        self.ram.update(
            {
                'total': status.total,
                'free': status.available,
                'used': status.used,
                'percent': status.percent,
                'total_descr': frmt_bytes(status.total),
                'free_descr': frmt_bytes(status.available),
                'used_descr': frmt_bytes(status.used)
            }
        )
    def run(self):
        while True:
            self.update_bandwidth()
            self.update_disk()
            self.update_cpu()
            self.update_ram()
            time.sleep(1)




monitor = Monitor(DISK_MONITOR)
monitor.start()

def get_Monitor():
    return monitor