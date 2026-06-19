"""
Route: Approval
----------------
Halaman approval booking oleh HRD, admin, dan direktur.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.room_booking import RoomBooking
from app.services.booking_service import BookingService, BookingValidationError
from app.routes.auth import admin_or_hrd_required

approval_bp = Blueprint('approval', __name__, url_prefix='/approval')


@approval_bp.route('/')
@admin_or_hrd_required
def list_pending():
    """Daftar booking yang menunggu approval."""
    status_filter = request.args.get('status', 'Pending')
    query = RoomBooking.query
    if status_filter and status_filter != 'All':
        query = query.filter_by(status=status_filter)
    bookings = query.order_by(RoomBooking.created_at.asc()).all()
    return render_template('approval/list.html', bookings=bookings,
                            current_filter=status_filter, statuses=RoomBooking.VALID_STATUSES)


@approval_bp.route('/<int:booking_id>')
@admin_or_hrd_required
def detail(booking_id):
    """Detail booking untuk approval."""
    booking = RoomBooking.query.get_or_404(booking_id)
    return render_template('approval/detail.html', booking=booking)


@approval_bp.route('/<int:booking_id>/approve', methods=['POST'])
@admin_or_hrd_required
def approve(booking_id):
    """Approve booking."""
    booking = RoomBooking.query.get_or_404(booking_id)
    try:
        BookingService.approve_booking(booking, current_user)
        flash('Booking berhasil di-approve.', 'success')
    except BookingValidationError as e:
        flash(str(e), 'danger')
    return redirect(url_for('approval.list_pending'))


@approval_bp.route('/<int:booking_id>/reject', methods=['POST'])
@admin_or_hrd_required
def reject(booking_id):
    """Reject booking (wajib isi alasan)."""
    booking = RoomBooking.query.get_or_404(booking_id)
    reason = request.form.get('reject_reason', '').strip()
    try:
        BookingService.reject_booking(booking, current_user, reason)
        flash('Booking berhasil di-reject.', 'success')
    except BookingValidationError as e:
        flash(str(e), 'danger')
    return redirect(url_for('approval.list_pending'))