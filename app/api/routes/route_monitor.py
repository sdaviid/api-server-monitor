from fastapi import(
    Depends,
    status,
    APIRouter
)

from app.api.deps import(
    User,
    get_current_active_user
)
from app.core.monitor import(
    Monitor,
    get_Monitor
)

router = APIRouter()

def frmt_speed(num, suffix="B"):
    num = num / 2
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


@router.get("/status/")
async def monitor_status(current_user: User = Depends(get_current_active_user), monitor: Monitor = Depends(get_Monitor)):
    inst_monitor = get_Monitor()
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