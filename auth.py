import functools
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort
import functools

bp = Blueprint('auth', __name__, url_prefix='/auth')

def login_required(view):
    """Decorator that redirects anonymous users to the login page"""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

@bp.before_app_request
def load_logged_in_user():
    """Load logged-in user info from session"""
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        # Load user from database
        g.user = {'id': user_id, 'username': 'user'}  # Implement actual user loading

@bp.route('/register', methods=('GET', 'POST'))
def register():
    """Register a new user"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Implement registration logic
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Log in a registered user"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Implement login logic
        session.clear()
        session['user_id'] = 1  # Replace with actual user ID
        return redirect(url_for('index'))
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    """Clear the current session, including the stored user id"""
    session.clear()
    return redirect(url_for('index'))