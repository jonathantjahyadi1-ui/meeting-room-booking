"""
Route: Auth
-----------
Login, register, dan logout.
Menggunakan Flask session login + password hashing.
Decorator role untuk akses kontrol.
"""
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.user import User
from app.models.division import Division

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def role_required(*roles):
    """
    Decorator untuk membatasi akses berdasarkan role.
    Harus digunakan setelah @login_required.

    Usage:
        @route('/admin-only')
        @login_required
        @role_required('admin', 'direktur')
        def admin_page():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.role not in roles:
                flash('Anda tidak memiliki akses ke halaman ini.', 'danger')
                return redirect(url_for('dashboard.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_or_hrd_required(f):
    """Decorator khusus untuk akses HRD, admin, atau direktur."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin_or_above():
            flash('Anda tidak memiliki akses ke halaman ini.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Halaman login."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Username dan password wajib diisi.', 'danger')
            return render_template('auth/login.html')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash(f'Login berhasil. Selamat datang, {user.nama}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('Username atau password salah.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Halaman registrasi user baru."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    # Ambil daftar divisi aktif untuk dropdown
    divisions = Division.get_active_choices()

    if request.method == 'POST':
        nama = request.form.get('nama', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        role = 'karyawan'
        division = request.form.get('division', '')

        # Validasi input
        errors = []
        if not nama:
            errors.append('Nama lengkap wajib diisi.')
        if not username:
            errors.append('Username wajib diisi.')
        if not password:
            errors.append('Password wajib diisi.')
        if len(password) < 6:
            errors.append('Password minimal 6 karakter.')
        if role != 'karyawan':
            errors.append('Role register hanya boleh karyawan.')
        if not division:
            errors.append('Divisi wajib dipilih.')

        # Cek username sudah dipakai
        if User.query.filter_by(username=username).first():
            errors.append('Username sudah digunakan.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html', divisions=divisions)

        # Buat user baru
        user = User(
            nama=nama,
            username=username,
            role=role,
            division=division,
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash('Register berhasil! Silakan login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', divisions=divisions)


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout user."""
    logout_user()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('auth.login'))