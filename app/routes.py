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
    """Blog listing page - No database required"""
    from app.utils.blog_loader import get_published_articles
    from flask_login import current_user
    
    # Get published articles (filter member-only if user is not authenticated)
    is_member = current_user.is_authenticated and hasattr(current_user, 'is_active_member') and current_user.is_active_member()
    articles = get_published_articles(member_only=False)
    
    # If user is authenticated member, also include member-only articles
    if is_member:
        member_articles = get_published_articles(member_only=True)
        all_articles = articles + [a for a in member_articles if a.is_member_only]
        articles = sorted(all_articles, key=lambda x: x.published_at or datetime.min, reverse=True)
    
    # Simple pagination
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('POSTS_PER_PAGE', 10)
    total = len(articles)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_articles = articles[start:end]
    
    # Create simple pagination object
    class SimplePagination:
        def __init__(self, items, page, per_page, total):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1 if self.has_prev else None
            self.next_num = page + 1 if self.has_next else None
    
    pagination = SimplePagination(paginated_articles, page, per_page, total)
    
    return render_template('blog.html', articles=paginated_articles, pagination=pagination)

@main_bp.route('/blog/<slug>')
def article(slug):
    """Individual article page - No database required"""
    from app.utils.blog_loader import get_article_by_slug
    from flask_login import current_user
    
    article = get_article_by_slug(slug)
    if not article:
        from flask import abort
        abort(404)
    
    # Check if article is published
    if not article.is_published():
        flash('This article is not yet published.', 'info')
        return redirect(url_for('main.blog'))
    
    # Check if article is member-only and user has access
    if article.is_member_only:
        is_member = current_user.is_authenticated and hasattr(current_user, 'is_active_member') and current_user.is_active_member()
        if not is_member:
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

