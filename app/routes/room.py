"""
Route: Master Ruangan
----------------------
CRUD Meeting Room — hanya HRD, admin, dan direktur.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.extensions import db
from app.models.meeting_room import MeetingRoom
from app.routes.auth import admin_or_hrd_required

room_bp = Blueprint('room', __name__, url_prefix='/rooms')


@room_bp.route('/')
@admin_or_hrd_required
def list_rooms():
    """Daftar semua ruang meeting."""
    rooms = MeetingRoom.query.order_by(MeetingRoom.room_name).all()
    return render_template('room/list.html', rooms=rooms)


@room_bp.route('/create', methods=['GET', 'POST'])
@admin_or_hrd_required
def create():
    """Tambah ruang meeting baru."""
    if request.method == 'POST':
        room_name = request.form.get('room_name', '').strip()
        capacity = request.form.get('capacity', type=int)
        location = request.form.get('location', '').strip()
        facilities = request.form.get('facilities', '').strip()

        errors = []
        if not room_name:
            errors.append('Nama ruangan wajib diisi.')
        if not capacity or capacity < 1:
            errors.append('Kapasitas minimal 1 orang.')
        if not location:
            errors.append('Lokasi wajib diisi.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('room/form.html', room=None)

        room = MeetingRoom(room_name=room_name, capacity=capacity, location=location, facilities=facilities)
        db.session.add(room)
        db.session.commit()
        flash('Data ruangan berhasil ditambahkan.', 'success')
        return redirect(url_for('room.list_rooms'))

    return render_template('room/form.html', room=None)


@room_bp.route('/<int:room_id>/edit', methods=['GET', 'POST'])
@admin_or_hrd_required
def edit(room_id):
    """Edit ruang meeting."""
    room = MeetingRoom.query.get_or_404(room_id)
    if request.method == 'POST':
        room.room_name = request.form.get('room_name', '').strip()
        room.capacity = request.form.get('capacity', type=int)
        room.location = request.form.get('location', '').strip()
        room.facilities = request.form.get('facilities', '').strip()

        errors = []
        if not room.room_name:
            errors.append('Nama ruangan wajib diisi.')
        if not room.capacity or room.capacity < 1:
            errors.append('Kapasitas minimal 1 orang.')
        if not room.location:
            errors.append('Lokasi wajib diisi.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('room/form.html', room=room)

        db.session.commit()
        flash('Data ruangan berhasil diedit.', 'success')
        return redirect(url_for('room.list_rooms'))

    return render_template('room/form.html', room=room)


@room_bp.route('/<int:room_id>/delete', methods=['POST'])
@admin_or_hrd_required
def delete(room_id):
    """Hapus ruang meeting."""
    room = MeetingRoom.query.get_or_404(room_id)
    db.session.delete(room)
    db.session.commit()
    flash('Data ruangan berhasil dihapus.', 'success')
    return redirect(url_for('room.list_rooms'))


@room_bp.route('/<int:room_id>/toggle', methods=['POST'])
@admin_or_hrd_required
def toggle(room_id):
    """Aktifkan/nonaktifkan ruangan."""
    room = MeetingRoom.query.get_or_404(room_id)
    room.is_active = not room.is_active
    db.session.commit()
    status = 'diaktifkan' if room.is_active else 'dinonaktifkan'
    flash(f'Ruangan berhasil {status}.', 'success')
    return redirect(url_for('room.list_rooms'))