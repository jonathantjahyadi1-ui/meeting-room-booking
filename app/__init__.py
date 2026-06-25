"""
Application Factory
--------------------
Fungsi create_app() membuat instance Flask dan mendaftarkan
semua ekstensi, blueprint, dan konfigurasi.
"""
import os
from flask import Flask
from app.config import get_config
from app.extensions import db, migrate, login_manager

# Import models agar terdaftar di SQLAlchemy
from app.models import User, Division, MeetingRoom, RoomBooking


def create_app(config_class=None):
    """
    Membuat dan mengonfigurasi aplikasi Flask.

    Args:
        config_class: Class konfigurasi (opsional, default dari FLASK_ENV)

    Returns:
        Flask app instance
    """
    app = Flask(__name__)

    # Load konfigurasi
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)
    print("DATABASE YANG DIPAKAI:", app.config.get("SQLALCHEMY_DATABASE_URI"))

    # Jika production config, panggil init_app
    if hasattr(config_class, 'init_app'):
        config_class.init_app(app)

    # Inisialisasi ekstensi
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Buat folder upload jika belum ada
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.booking import booking_bp
    from app.routes.approval import approval_bp
    from app.routes.room import room_bp
    from app.routes.schedule import schedule_bp
    from app.routes.report import report_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(approval_bp)
    app.register_blueprint(room_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(report_bp)

    # Buat tabel dan seed data awal
    with app.app_context():
        db.create_all()

        try:
            # Seed divisi default
            Division.seed_defaults()

            # Seed akun khusus perusahaan
            default_users = [
                {
                    'nama': 'Jonathan',
                    'username': 'Jonathan',
                    'password': 'Jonathan@itsupport',
                    'role': 'admin',
                    'division': 'IT',
                },
                {
                    'nama': 'Devina',
                    'username': 'Devina',
                    'password': 'Devina@hrd',
                    'role': 'hrd',
                    'division': 'HRD',
                },
                {
                    'nama': 'Martin',
                    'username': 'Martin',
                    'password': 'Martin@direktur',
                    'role': 'direktur',
                    'division': 'Direktur',
                },
            ]

            for data in default_users:
                existing_user = User.query.filter_by(username=data['username']).first()

                if not existing_user:
                    user = User(
                        nama=data['nama'],
                        username=data['username'],
                        role=data['role'],
                        division=data['division'],
                    )
                    user.set_password(data['password'])
                    db.session.add(user)

            db.session.commit()

        except Exception as e:
            db.session.rollback()
            print(f'Seed data gagal: {e}')

    return app