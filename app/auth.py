"""
Member authentication routes
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, MembershipType, MembershipStatus
from werkzeug.security import check_password_hash
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Member registration"""
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        membership_type = request.form.get('membership_type', 'annual')
        
        # Validation
        if not name or not email or not password:
            flash('Please fill in all required fields.', 'error')
            return render_template('register.html', membership_type=membership_type)
        
        if password != password_confirm:
            flash('Passwords do not match.', 'error')
            return render_template('register.html', membership_type=membership_type)
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return render_template('register.html', membership_type=membership_type)
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('An account with this email already exists. Please log in instead.', 'error')
            return redirect(url_for('auth.login'))
        
        # Create new user
        try:
            user = User(
                name=name,
                email=email,
                membership_type=MembershipType[membership_type.upper()] if membership_type.upper() in [e.name for e in MembershipType] else MembershipType.ANNUAL,
                membership_status=MembershipStatus.PENDING
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please log in to continue.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'error')
            return render_template('register.html', membership_type=membership_type)
    
    # GET request
    membership_type = request.args.get('membership_type', 'annual')
    return render_template('register.html', membership_type=membership_type)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Member login"""
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))
        
        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('auth.dashboard'))
        else:
            flash('Invalid email or password.', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Member logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/dashboard')
@login_required
def dashboard():
    """Member dashboard"""
    return render_template('member_dashboard.html')

@auth_bp.route('/content')
@login_required
def member_content():
    """Exclusive member content"""
    if not current_user.is_active_member():
        flash('This content is available to active members only.', 'info')
        return redirect(url_for('main.membership'))
    
    from app.models import Article
    articles = Article.query.filter_by(is_member_only=True).filter(
        Article.published_at.isnot(None)
    ).filter(
        Article.published_at <= datetime.utcnow()
    ).order_by(Article.published_at.desc()).limit(10).all()
    
    return render_template('member_content.html', articles=articles)

@auth_bp.route('/download-membership-card')
@login_required
def download_membership_card():
    """Generate and download membership card PDF"""
    from app.utils.membership_card import generate_membership_card
    return generate_membership_card(current_user)

