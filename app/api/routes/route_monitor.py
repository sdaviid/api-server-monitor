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
from app.utils.utils import(
    frmt_speed,
    frmt_bytes
)


router = APIRouter()



@router.get("/status/")
async def monitor_status(current_user: User = Depends(get_current_active_user), monitor: Monitor = Depends(get_Monitor)):
    inst_monitor = get_Monitor()
    return {
        'bandwidth': {
            'speed_up': inst_monitor.speed_sent,
            'speed_down': inst_monitor.speed_recv,
            'speed_up_descr': inst_monitor.speed_sent_descr[0],
            'speed_down_descr': inst_monitor.speed_recv_descr
        },
        'disk': inst_monitor.disk_space,
        'cpu': inst_monitor.cpu,
        'ram': inst_monitor.ram
    }