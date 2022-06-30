from fastapi import(
    Depends,
    status,
    APIRouter
)

from app.api.deps import(
    allow_access_resource
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



@router.get(
    "/status/",
    dependencies=[Depends(allow_access_resource)]
)
async def monitor_status(monitor: Monitor = Depends(get_Monitor)):
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