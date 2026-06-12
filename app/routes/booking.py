"""
Route: Booking
---------------
CRUD booking ruang meeting.
Karyawan hanya bisa melihat/mengelola booking miliknya sendiri.
HRD/admin/direktur bisa melihat semua booking.
"""
import os
from datetime import datetime, date
from werkzeug.utils import secure_filename
from flask import (
    Blueprint, render_template, redirect, url_for, flash,
    request, current_app
)
from flask_login import login_required, current_user
from app.extensions import db
from app.models.room_booking import RoomBooking
from app.models.meeting_room import MeetingRoom
from app.models.division import Division
from app.services.booking_service import BookingService, BookingValidationError
from app.routes.auth import admin_or_hrd_required

booking_bp = Blueprint('booking', __name__, url_prefix='/booking')


# --- Routes ---

@booking_bp.route('/')
@login_required
def my_bookings():
    """Daftar booking milik user yang sedang login."""
    if current_user.is_admin_or_above():
        # HRD, admin, direktur bisa lihat semua
        bookings = RoomBooking.query.order_by(RoomBooking.created_at.desc()).all()
    else:
        bookings = RoomBooking.query.filter_by(user_id=current_user.id).order_by(
            RoomBooking.created_at.desc()
        ).all()

    return render_template('booking/my_list.html', bookings=bookings)


@booking_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Form pengajuan booking baru."""
    rooms = MeetingRoom.get_active_rooms()
    divisions = Division.get_active_choices()
    min_days = current_app.config.get('MIN_BOOKING_DAYS', 14)

    if request.method == 'POST':
        try:
            # Ambil data dari form
            title = request.form.get('title', '').strip()
            division = request.form.get('division', '')
            room_id = request.form.get('room_id', type=int)
            meeting_date_str = request.form.get('meeting_date', '')
            start_time_str = request.form.get('start_time', '')
            end_time_str = request.form.get('end_time', '')
            participant_count = request.form.get('participant_count', type=int)
            purpose = request.form.get('purpose', '').strip()
            notes = request.form.get('notes', '').strip()

            # Validasi field wajib
            if not all([title, division, room_id, meeting_date_str, start_time_str,
                        end_time_str, participant_count, purpose]):
                flash('Semua field wajib (kecuali catatan dan lampiran) harus diisi.', 'danger')
                return render_template(
                    'booking/form.html', rooms=rooms, divisions=divisions, min_days=min_days
                )

            # Parse tanggal dan waktu
            meeting_date = datetime.strptime(meeting_date_str, '%Y-%m-%d').date()
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()

            # Validasi booking
            BookingService.validate_booking(
                room_id=room_id,
                meeting_date=meeting_date,
                start_time=start_time,
                end_time=end_time,
                participant_count=participant_count,
                min_booking_days=min_days,
            )


            # Buat booking
            booking = RoomBooking(
                user_id=current_user.id,
                room_id=room_id,
                title=title,
                division=division,
                meeting_date=meeting_date,
                start_time=start_time,
                end_time=end_time,
                participant_count=participant_count,
                purpose=purpose,
                notes=notes,
                attachment=None,
                status=RoomBooking.STATUS_PENDING,
            )
            

            db.session.add(booking)
            db.session.commit()

            flash('Booking berhasil diajukan! Menunggu approval HRD.', 'success')
            return redirect(url_for('booking.my_bookings'))

        except BookingValidationError as e:
            flash(str(e), 'danger')
        except ValueError:
            flash('Format tanggal atau jam tidak valid.', 'danger')

    return render_template(
        'booking/form.html', rooms=rooms, divisions=divisions, min_days=min_days
    )


@booking_bp.route('/<int:booking_id>')
@login_required
def detail(booking_id):
    """Halaman detail booking."""
    booking = RoomBooking.query.get_or_404(booking_id)

    # Karyawan hanya bisa lihat booking miliknya
    if not current_user.is_admin_or_above() and booking.user_id != current_user.id:
        flash('Anda tidak memiliki akses ke booking ini.', 'danger')
        return redirect(url_for('booking.my_bookings'))

    return render_template('booking/detail.html', booking=booking)


@booking_bp.route('/<int:booking_id>/cancel', methods=['POST'])
@login_required
def cancel(booking_id):
    """Batalkan booking (hanya status Pending, milik sendiri)."""
    booking = RoomBooking.query.get_or_404(booking_id)

    try:
        BookingService.cancel_booking(booking, current_user)
        flash('Booking berhasil dibatalkan.', 'success')
    except BookingValidationError as e:
        flash(str(e), 'danger')

    return redirect(url_for('booking.my_bookings'))


@booking_bp.route('/all')
@admin_or_hrd_required
def all_bookings():
    """Semua booking — hanya untuk HRD/admin/direktur."""
    bookings = RoomBooking.query.order_by(RoomBooking.created_at.desc()).all()
    return render_template('booking/my_list.html', bookings=bookings)