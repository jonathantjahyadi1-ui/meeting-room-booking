"""
Inisialisasi Ekstensi Flask
-----------------------------
Semua ekstensi (SQLAlchemy, Migrate, LoginManager)
diinisialisasi di sini agar bisa di-import oleh modul lain.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Inisialisasi tanpa app (akan di-init di factory)
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# Konfigurasi login manager
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Silakan login terkahir dahulu.'
login_manager.login_message_category = 'warning'