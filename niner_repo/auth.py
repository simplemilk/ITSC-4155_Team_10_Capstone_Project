import functools
import secrets
from datetime import datetime, timedelta
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from db import get_db

# Blueprint must be defined FIRST before any routes
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        email = request.form.get('email', '').strip()
        confirm_password = request.form.get('confirmPassword', '')
        agree_terms = request.form.get('agreeTerms')
        
        # Security questions
        security_question_1 = request.form.get('securityQuestion1', '')
        security_answer_1 = request.form.get('securityAnswer1', '').strip()
        security_question_2 = request.form.get('securityQuestion2', '')
        security_answer_2 = request.form.get('securityAnswer2', '').strip()
        
        error = None

        # Debug: Print form data
        print(f"Registration attempt - Username: {username}, Email: {email}")
        print(f"Security questions provided: {bool(security_question_1 and security_answer_1)}")

        # Basic validation
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not email:
            error = 'Email is required.'
        elif not confirm_password:
            error = 'Password confirmation is required.'
        elif not agree_terms:
            error = 'You must agree to the Terms of Service and Privacy Policy.'
        elif len(username) < 3:
            error = 'Username must be at least 3 characters long.'
        elif len(password) < 8:
            error = 'Password must be at least 8 characters long.'
        elif password != confirm_password:
            error = 'Password confirmation does not match.'
        elif not '@' in email or '.' not in email:
            error = 'Please enter a valid email address.'
        elif not security_question_1 or not security_answer_1:
            error = 'First security question and answer are required.'
        elif not security_question_2 or not security_answer_2:
            error = 'Second security question and answer are required.'
        elif len(security_answer_1) < 2:
            error = 'Security answers must be at least 2 characters long.'
        elif len(security_answer_2) < 2:
            error = 'Security answers must be at least 2 characters long.'

        if error is None:
            try:
                db = get_db()
                print(f"Database connection successful")
                
                # Check if users already exists
                existing_user = db.execute(
                    'SELECT id FROM users WHERE username = ? OR email = ?', 
                    (username, email)
                ).fetchone()
                
                if existing_user:
                    existing_check = db.execute(
                        'SELECT username, email FROM users WHERE username = ? OR email = ?', 
                        (username, email)
                    ).fetchone()
                    if existing_check['username'] == username:
                        error = f"Username '{username}' is already taken."
                    else:
                        error = f"Email '{email}' is already registered."
                else:
                    # Hash security answers for storage
                    hashed_answer_1 = generate_password_hash(security_answer_1.lower())
                    hashed_answer_2 = generate_password_hash(security_answer_2.lower())
                    
                    # Insert new users with security questions
                    print(f"Inserting new users: {username}, {email}")
                    db.execute('''
                        INSERT INTO users (username, email, password, security_question_1, security_answer_1, security_question_2, security_answer_2) 
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        username, 
                        email, 
                        generate_password_hash(password),
                        security_question_1,
                        hashed_answer_1,
                        security_question_2,
                        hashed_answer_2
                    ))
                    db.commit()
                    print("users inserted successfully")
                    flash('Registration successful! Please log in.', 'success')
                    return redirect(url_for("auth.login"))
                    
            except Exception as e:
                print(f"Registration error details: {e}")
                import traceback
                traceback.print_exc()
                
                error_str = str(e).lower()
                if 'username' in error_str or 'unique' in error_str:
                    if 'username' in error_str:
                        error = f"Username '{username}' is already taken."
                    elif 'email' in error_str:
                        error = f"Email '{email}' is already registered."
                    else:
                        error = "This username or email is already in use."
                else:
                    error = f"Registration failed: {str(e)}"

        if error:
            print(f"Registration error: {error}")
            return render_template('auth/register.html', error=error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        error = None
        
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        else:
            try:
                db = get_db()
                users = db.execute(
                    'SELECT * FROM users WHERE username = ?', (username,)
                ).fetchone()

                if users is None:
                    error = 'Username not found.'
                elif not check_password_hash(users['password'], password):
                    error = 'Incorrect password.'
                else:
                    session.clear()
                    session['user_id'] = users['id']
                    flash('Welcome back!', 'success')
                    return redirect(url_for('dashboard'))
                    
            except Exception as e:
                print(f"Login error: {e}")
                error = 'Login failed. Please try again.'

        if error:
            return render_template('auth/login.html', error=error)

    return render_template('auth/login.html')

@bp.route('/demo')
def demo_login():
    """Automatically log in with demo account"""
    try:
        db = get_db()
        users = db.execute(
            'SELECT * FROM users WHERE username = ?', ('demo',)
        ).fetchone()
        
        if users:
            session.clear()
            session['user_id'] = users['id']
            flash('Welcome to the demo!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Demo account not found.', 'error')
            return redirect(url_for('auth.login'))
            
    except Exception as e:
        print(f"Demo login error: {e}")
        flash(f'Error accessing demo account: {str(e)}', 'error')
        return redirect(url_for('auth.login'))

@bp.route('/forgot-password-questions', methods=('GET', 'POST'))
def forgot_password_questions():
    """Password recovery using security questions"""
    if request.method == 'POST':
        step = request.form.get('step', '1')
        
        if step == '1':
            # Step 1: Get username/email and show security questions
            identifier = request.form.get('identifier', '').strip()
            
            if not identifier:
                flash('Please enter your username or email.', 'error')
                return render_template('auth/forgot_password_questions.html', step=1)
            
            try:
                db = get_db()
                
                # Find users by username or email
                if '@' in identifier:
                    users = db.execute('''
                        SELECT id, username, email, security_question_1, security_question_2 
                        FROM users WHERE email = ?
                    ''', (identifier,)).fetchone()
                else:
                    users = db.execute('''
                        SELECT id, username, email, security_question_1, security_question_2 
                        FROM users WHERE username = ?
                    ''', (identifier,)).fetchone()
                
                if users and users['security_question_1'] and users['security_question_2']:
                    # Show security questions
                    return render_template('auth/forgot_password_questions.html', 
                                         step=2, 
                                         users=users)
                else:
                    flash('users not found or security questions not set up.', 'error')
                    return render_template('auth/forgot_password_questions.html', step=1)
                    
            except Exception as e:
                print(f"Error in password recovery step 1: {e}")
                flash('An error occurred. Please try again.', 'error')
                return render_template('auth/forgot_password_questions.html', step=1)
        
        elif step == '2':
            # Step 2: Verify security answers and reset password
            user_id = request.form.get('user_id')
            answer_1 = request.form.get('answer1', '').strip()
            answer_2 = request.form.get('answer2', '').strip()
            new_password = request.form.get('newPassword', '')
            confirm_password = request.form.get('confirmPassword', '')
            
            if not all([user_id, answer_1, answer_2, new_password, confirm_password]):
                flash('All fields are required.', 'error')
                return redirect(url_for('auth.forgot_password_questions'))
            
            if len(new_password) < 8:
                flash('New password must be at least 8 characters long.', 'error')
                return redirect(url_for('auth.forgot_password_questions'))
            
            if new_password != confirm_password:
                flash('Passwords do not match.', 'error')
                return redirect(url_for('auth.forgot_password_questions'))
            
            try:
                db = get_db()
                
                # Get users's security answers
                users = db.execute('''
                    SELECT username, security_answer_1, security_answer_2 
                    FROM users WHERE id = ?
                ''', (user_id,)).fetchone()
                
                if not users:
                    flash('Invalid users.', 'error')
                    return redirect(url_for('auth.forgot_password_questions'))
                
                # Verify security answers (compare lowercase)
                if (check_password_hash(users['security_answer_1'], answer_1.lower()) and 
                    check_password_hash(users['security_answer_2'], answer_2.lower())):
                    
                    # Reset password
                    new_password_hash = generate_password_hash(new_password)
                    db.execute('UPDATE users SET password = ? WHERE id = ?', 
                              (new_password_hash, user_id))
                    db.commit()
                    
                    flash('Password reset successful! You can now log in with your new password.', 'success')
                    return redirect(url_for('auth.login'))
                else:
                    flash('Security answers are incorrect. Please try again.', 'error')
                    return redirect(url_for('auth.forgot_password_questions'))
                    
            except Exception as e:
                print(f"Error in password recovery step 2: {e}")
                flash('An error occurred. Please try again.', 'error')
                return redirect(url_for('auth.forgot_password_questions'))
    
    return render_template('auth/forgot_password_questions.html', step=1)

@bp.route('/forgot-password', methods=('GET', 'POST'))
def forgot_password():
    """Redirect to security questions since we don't have email"""
    flash('Please use security questions to reset your password.', 'info')
    return redirect(url_for('auth.forgot_password_questions'))

@bp.route('/reset-password', methods=('GET', 'POST'))
def reset_password():
    token = request.args.get('token') or request.form.get('token')
    
    if not token:
        flash('Invalid reset link.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        new_password = request.form.get('newPassword', '')
        confirm_password = request.form.get('confirmPassword', '')
        
        if not new_password or len(new_password) < 8:
            flash('Password must be at least 8 characters.', 'error')
            return render_template('auth/reset_password.html', token=token)
        
        if new_password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/reset_password.html', token=token)
        
        try:
            db = get_db()
            reset_record = db.execute('''
                SELECT pr.*, u.username FROM password_resets pr
                JOIN users u ON pr.user_id = u.id
                WHERE pr.token = ? AND pr.expires_at > ?
            ''', (token, datetime.now())).fetchone()
            
            if not reset_record:
                flash('Invalid or expired reset link.', 'error')
                return redirect(url_for('auth.forgot_password'))
            
            # Update password and delete token
            db.execute('UPDATE users SET password = ? WHERE id = ?',
                      (generate_password_hash(new_password), reset_record['user_id']))
            db.execute('DELETE FROM password_resets WHERE token = ?', (token,))
            db.commit()
            
            flash('Password reset successful! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            print(f"Reset password error: {e}")
            flash('An error occurred. Please try again.', 'error')
    
    return render_template('auth/reset_password.html', token=token)

@bp.route('/profile', methods=('GET', 'POST'))
def profile():
    if g.user is None:
        flash('Please log in to access your profile.', 'warning')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        current_password = request.form.get('currentPassword', '')
        new_password = request.form.get('newPassword', '')
        confirm_password = request.form.get('confirmPassword', '')
        
        error = None
        
        if not email or '@' not in email:
            error = 'Valid email is required.'
        
        if new_password:
            if not current_password:
                error = 'Current password is required to change password.'
            elif not check_password_hash(g.user['password'], current_password):
                error = 'Current password is incorrect.'
            elif len(new_password) < 8:
                error = 'New password must be at least 8 characters.'
            elif new_password != confirm_password:
                error = 'New passwords do not match.'
        
        if error is None:
            try:
                db = get_db()
                db.execute('UPDATE users SET email = ? WHERE id = ?', (email, g.user['id']))
                
                if new_password:
                    db.execute('UPDATE users SET password = ? WHERE id = ?',
                              (generate_password_hash(new_password), g.user['id']))
                
                db.commit()
                flash('Profile updated successfully!', 'success')
                return redirect(url_for('auth.profile'))
                
            except Exception as e:
                error = 'Email already in use by another account.' if 'email' in str(e).lower() else 'An error occurred updating your profile.'
        
        if error:
            return render_template('auth/profile.html', error=error)
    
    return render_template('auth/profile.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        try:
            g.user = get_db().execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        except Exception as e:
            print(f"Error loading users: {e}")
            g.user = None

@bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

def create_demo_user():
    """Create a demo users for testing purposes"""
    try:
        db = get_db()
        existing_user = db.execute('SELECT * FROM users WHERE username = ?', ('demo',)).fetchone()
        
        if not existing_user:
            # Hash security answers for demo users
            demo_answer_1 = generate_password_hash('fluffy')
            demo_answer_2 = generate_password_hash('rover')
            
            db.execute('''
                INSERT INTO users (username, email, password, security_question_1, security_answer_1, security_question_2, security_answer_2) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                'demo', 
                'demo@ninerfinance.com', 
                generate_password_hash('demo123'),
                "What was the name of your first pet?",
                demo_answer_1,
                "What was the name of your childhood best friend?",
                demo_answer_2
            ))
            db.commit()
            print("Demo users created successfully")
        else:
            print("Demo users already exists")
            
    except Exception as e:
        print(f"Error creating demo users: {e}")