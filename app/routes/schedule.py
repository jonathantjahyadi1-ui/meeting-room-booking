from datetime import date, datetime, timedelta

from flask import Blueprint, render_template, request
from flask_login import login_required

from app.models.room_booking import RoomBooking
from app.models.meeting_room import MeetingRoom
from app.models.division import Division


schedule_bp = Blueprint('schedule', __name__, url_prefix='/schedule')


@schedule_bp.route('/')
@login_required
def index():
    """
    Halaman jadwal ruang meeting.
    Mendukung tampilan harian, mingguan, dan bulanan.
    """

    # Ambil mode tampilan: day, week, atau month
    view_mode = request.args.get('view', 'day')
    if view_mode not in ('day', 'week', 'month'):
        view_mode = 'day'

    # Ambil tanggal dari query string
    current_date_str = request.args.get('date', '')

    try:
        current_date = (
            datetime.strptime(current_date_str, '%Y-%m-%d').date()
            if current_date_str
            else date.today()
        )
    except ValueError:
        current_date = date.today()

    # Filter tambahan
    room_id = request.args.get('room_id', type=int)
    division = request.args.get('division', '')
    status = request.args.get('status', 'Approved')

    # Tentukan range tanggal berdasarkan mode tampilan
    days = []

    if view_mode == 'day':
        start_date = current_date
        end_date = current_date
        days = [current_date]

    elif view_mode == 'week':
        # Mulai dari Senin sampai Minggu
        start_date = current_date - timedelta(days=current_date.weekday())
        end_date = start_date + timedelta(days=6)
        days = [start_date + timedelta(days=i) for i in range(7)]

    else:
        # Bulanan
        start_date = current_date.replace(day=1)

        if current_date.month == 12:
            next_month = current_date.replace(year=current_date.year + 1, month=1, day=1)
        else:
            next_month = current_date.replace(month=current_date.month + 1, day=1)

        end_date = next_month - timedelta(days=1)

    # Query booking
    query = RoomBooking.query.filter(
        RoomBooking.meeting_date >= start_date,
        RoomBooking.meeting_date <= end_date
    )

    if room_id:
        query = query.filter(RoomBooking.room_id == room_id)

    if division:
        query = query.filter(RoomBooking.division == division)

    if status and status != 'All':
        query = query.filter(RoomBooking.status == status)

    bookings = query.order_by(
        RoomBooking.meeting_date.asc(),
        RoomBooking.start_time.asc()
    ).all()

    rooms = MeetingRoom.get_active_rooms()
    divisions = Division.get_active_choices()

    return render_template(
        'schedule/index.html',
        bookings=bookings,
        rooms=rooms,
        divisions=divisions,
        view_mode=view_mode,
        current_date=current_date,
        room_id=room_id,
        division=division,
        status=status,
        days=days
    )