from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.booking import booking_bp
from app.routes.approval import approval_bp
from app.routes.room import room_bp
from app.routes.schedule import schedule_bp
from app.routes.report import report_bp

__all__ = [
    'auth_bp', 'dashboard_bp', 'booking_bp',
    'approval_bp', 'room_bp', 'schedule_bp', 'report_bp',
]