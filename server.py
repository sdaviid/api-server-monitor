import time
import psutil
from threading import Thread
from fastapi import(
    Depends,
    FastAPI,
    HTTPException,
    Response,
    status
)
from fastapi.middleware.cors import CORSMiddleware

def frmt_speed(num, suffix="B"):
    num = num / 2
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"




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
    def update_disk(self):
        for disk in self.disk:
            hdd = psutil.disk_usage(disk)
            self.disk_space.update(
                {
                    disk: {
                        'total': hdd.total / (2**30),
                        'free': hdd.free / (2**30),
                        'used': hdd.used / (2**30)
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
                'percent': status.percent
            }
        )
    def run(self):
        while True:
            self.update_bandwidth()
            self.update_disk()
            self.update_cpu()
            self.update_ram()
            time.sleep(1)


DISK_MONITOR = ['/var/www/html/dump']
inst_monitor = Monitor(disk=DISK_MONITOR)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.get(
    '/status'
)
def get_status():
    return {
        'bandwidth': {
            'speed_up': inst_monitor.speed_sent,
            'speed_down': inst_monitor.speed_recv,
            'speed_up_descr': frmt_speed(inst_monitor.speed_sent),
            'speed_down_descr': frmt_speed(inst_monitor.speed_recv)
        },
        'disk': inst_monitor.disk_space,
        'cpu': inst_monitor.cpu,
        'ram': inst_monitor.ram
    }


a = inst_monitor.start();