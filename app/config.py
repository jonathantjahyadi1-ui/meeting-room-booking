"""
Konfigurasi Aplikasi
----------------------
Semua konfigurasi diambil dari environment variable.
Tidak ada nilai sensitif yang di-hardcode.
"""
import os

# Tentukan base directory project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..'))


class Config:
    """Konfigurasi base — berlaku untuk semua environment."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join(PROJECT_ROOT, 'uploads'))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Maksimal upload 16MB
    MIN_BOOKING_DAYS = int(os.environ.get('MIN_BOOKING_DAYS', 14))


class DevelopmentConfig(Config):
    """Konfigurasi development — menggunakan SQLite."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{os.path.join(PROJECT_ROOT, "meeting_booking.db")}'
    )


class ProductionConfig(Config):
    DEBUG = False
    # DigitalOcean Managed Database menyediakan DATABASE_URL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # Jika DATABASE_URL menggunakan prefix postgres:// (DO lama),
    # ubah menjadi postgresql:// untuk SQLAlchemy
    @classmethod
    def init_app(cls, app):
        db_url = os.environ.get('DATABASE_URL', '')
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
            app.config['SQLALCHEMY_DATABASE_URI'] = db_url


# Mapping environment ke config class
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}


def get_config():
    """Ambil config class berdasarkan FLASK_ENV."""
    env = os.environ.get('FLASK_ENV', 'development')
    return config_map.get(env, config_map['default'])