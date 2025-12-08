"""
Main public routes
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from app.models import Article, User
from app import db
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Homepage"""
    return render_template('index.html')

@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@main_bp.route('/services')
def services():
    """Services page"""
    return render_template('services.html')

@main_bp.route('/membership')
def membership():
    """Membership page"""
    return render_template('membership.html')

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        # Basic validation
        if not name or not email or not message:
            flash('Please fill in all fields.', 'error')
            return render_template('contact.html')
        
        # Here you would typically send an email
        # For now, we'll just flash a success message
        flash('Thank you for your message. We will get back to you soon!', 'success')
        return redirect(url_for('main.contact'))
    
    return render_template('contact.html')

@main_bp.route('/blog')
def blog():
    """Blog listing page"""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('POSTS_PER_PAGE', 10)
    
    # Get published articles (public only, or member-only if user is authenticated)
    query = Article.query.filter(Article.published_at.isnot(None))
    query = query.filter(Article.published_at <= datetime.utcnow())
    
    # If user is not authenticated, only show public articles
    from flask_login import current_user
    if not current_user.is_authenticated or not current_user.is_active_member():
        query = query.filter(Article.is_member_only == False)
    
    # Order by published date (newest first)
    query = query.order_by(Article.published_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    articles = pagination.items
    
    return render_template('blog.html', articles=articles, pagination=pagination)

@main_bp.route('/blog/<slug>')
def article(slug):
    """Individual article page"""
    article = Article.query.filter_by(slug=slug).first_or_404()
    
    # Check if article is published
    if not article.is_published():
        flash('This article is not yet published.', 'info')
        return redirect(url_for('main.blog'))
    
    # Check if article is member-only and user has access
    from flask_login import current_user
    if article.is_member_only:
        if not current_user.is_authenticated or not current_user.is_active_member():
            flash('This article is available to members only. Please log in or become a member to access it.', 'info')
            return redirect(url_for('auth.login'))
    
    return render_template('article.html', article=article)

@main_bp.errorhandler(404)
def page_not_found(e):
    """404 error handler"""
    return render_template('errors/404.html'), 404

@main_bp.errorhandler(500)
def internal_server_error(e):
    """500 error handler"""
    db.session.rollback()
    return render_template('errors/500.html'), 500

