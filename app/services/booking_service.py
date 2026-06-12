"""
Service: Booking
-----------------
Business logic untuk booking ruang meeting.
Menangani validasi bentrok jadwal, batas H-14/H-30, dan aturan booking.
"""
from datetime import date, datetime, time
from app.extensions import db
from app.models.room_booking import RoomBooking
from app.models.meeting_room import MeetingRoom


class BookingValidationError(Exception):
    """Exception custom untuk validasi booking yang gagal."""
    pass


class BookingService:
    """Service class untuk operasi booking."""

    @staticmethod
    def validate_booking(
        room_id,
        meeting_date,
        start_time,
        end_time,
        participant_count,
        min_booking_days=14,
        exclude_booking_id=None,
    ):
        """
        Validasi semua aturan booking sebelum disimpan.

        Args:
            room_id: ID ruangan
            meeting_date: Tanggal meeting (date object)
            start_time: Jam mulai (time object)
            end_time: Jam selesai (time object)
            participant_count: Jumlah peserta
            min_booking_days: Minimal H- berapa hari sebelum meeting (default 14)
            exclude_booking_id: Booking ID yang dikecualikan (untuk edit)

        Raises:
            BookingValidationError: Jika validasi gagal
        """
        today = date.today()

        # 1. Validasi H-14 atau H-30
        if isinstance(meeting_date, str):
            meeting_date = datetime.strptime(meeting_date, '%Y-%m-%d').date()

        delta_days = (meeting_date - today).days
        if delta_days < min_booking_days:
            raise BookingValidationError(
                f'Booking harus diajukan minimal H-{min_booking_days} sebelum tanggal meeting. '
                f'Tanggal meeting: {meeting_date}, hari ini: {today}'
            )

        # 2. Validasi jam selesai > jam mulai
        if isinstance(start_time, str):
            start_time = datetime.strptime(start_time, '%H:%M').time()
        if isinstance(end_time, str):
            end_time = datetime.strptime(end_time, '%H:%M').time()

        if end_time <= start_time:
            raise BookingValidationError(
                'Jam selesai tidak boleh lebih awal atau sama dengan jam mulai.'
            )

        # 3. Validasi kapasitas ruangan
        room = MeetingRoom.query.get(room_id)
        if not room:
            raise BookingValidationError('Ruangan tidak ditemukan.')

        if not room.is_active:
            raise BookingValidationError('Ruangan sedang tidak aktif.')

        if participant_count > room.capacity:
            raise BookingValidationError(
                f'Jumlah peserta ({participant_count}) melebihi kapasitas ruangan '
                f'({room.capacity} orang).'
            )

        # 4. Validasi bentrok jadwal
        BookingService._validate_no_schedule_conflict(
            room_id, meeting_date, start_time, end_time, exclude_booking_id
        )

    @staticmethod
    def _validate_no_schedule_conflict(
        room_id, meeting_date, start_time, end_time, exclude_booking_id=None
    ):
        """
        Cek apakah ada jadwal bentrok di ruangan yang sama.

        Kondisi bentrok:
        - Ruangan sama
        - Tanggal sama
        - Status Pending atau Approved
        - Waktu bertabrakan:
          a. Booking baru mulai di tengah jadwal lain
          b. Booking baru selesai di tengah jadwal lain
          c. Booking baru menutupi seluruh jadwal lain
          d. Booking baru berada di dalam jadwal lain
        """
        # Cari booking yang bentrok
        conflicts = RoomBooking.query.filter(
            RoomBooking.room_id == room_id,
            RoomBooking.meeting_date == meeting_date,
            RoomBooking.status.in_([RoomBooking.STATUS_PENDING, RoomBooking.STATUS_APPROVED]),
        )

        if exclude_booking_id:
            conflicts = conflicts.filter(RoomBooking.id != exclude_booking_id)

        conflicts = conflicts.all()

        for existing in conflicts:
            # Cek tabrakan waktu
            # existing_start < new_end AND existing_end > new_start = bentrok
            if existing.start_time < end_time and existing.end_time > start_time:
                raise BookingValidationError(
                    'Ruangan sudah dibooking pada tanggal dan jam tersebut.'
                )

    @staticmethod
    def cancel_booking(booking, user):
        """
        Batalkan booking.

        Args:
            booking: RoomBooking object
            user: User yang membatalkan

        Raises:
            BookingValidationError: Jika tidak bisa dibatalkan
        """
        if booking.status == RoomBooking.STATUS_APPROVED:
            raise BookingValidationError(
                'Booking sudah disetujui. Silakan hubungi HRD untuk pembatalan.'
            )

        if booking.user_id != user.id:
            raise BookingValidationError(
                'Anda hanya bisa membatalkan booking milik sendiri.'
            )

        if booking.status not in (RoomBooking.STATUS_PENDING,):
            raise BookingValidationError(
                'Booking tidak dapat dibatalkan pada status saat ini.'
            )

        booking.status = RoomBooking.STATUS_CANCELLED
        db.session.commit()

    @staticmethod
    def approve_booking(booking, approver):
        """
        Setujui booking.

        Args:
            booking: RoomBooking object
            approver: User yang menyetujui
        """
        if booking.status != RoomBooking.STATUS_PENDING:
            raise BookingValidationError('Hanya booking dengan status Pending yang bisa di-approve.')

        booking.status = RoomBooking.STATUS_APPROVED
        booking.approved_by = approver.id
        booking.approved_at = datetime.utcnow()
        booking.reject_reason = None
        db.session.commit()

    @staticmethod
    def reject_booking(booking, approver, reason):
        """
        Tolak booking.

        Args:
            booking: RoomBooking object
            approver: User yang menolak
            reason: Alasan penolakan (wajib)

        Raises:
            BookingValidationError: Jika alasan kosong
        """
        if not reason or not reason.strip():
            raise BookingValidationError('Alasan penolakan wajib diisi.')

        if booking.status != RoomBooking.STATUS_PENDING:
            raise BookingValidationError('Hanya booking dengan status Pending yang bisa di-reject.')

        booking.status = RoomBooking.STATUS_REJECTED
        booking.approved_by = approver.id
        booking.approved_at = datetime.utcnow()
        booking.reject_reason = reason.strip()
        db.session.commit()