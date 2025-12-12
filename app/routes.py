"""
Main public routes
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from app import db
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/health')
def health():
    """Health check endpoint for Render"""
    return {'status': 'ok', 'service': 'terralumen'}, 200

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
    try:
        from app.utils.blog_loader import load_blog_articles
        from flask_login import current_user
        
        # Load all articles
        all_articles = load_blog_articles()
        
        # Filter published articles
        published_articles = [a for a in all_articles if a.is_published()]
        
        # Check if user is authenticated member
        is_member = False
        if current_user.is_authenticated:
            try:
                is_member = hasattr(current_user, 'is_active_member') and current_user.is_active_member()
            except:
                is_member = False
        
        # Filter by member-only status
        if is_member:
            # Show all published articles (including member-only)
            articles = published_articles
        else:
            # Only show public articles
            articles = [a for a in published_articles if not a.is_member_only]
        
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
                self.pages = (total + per_page - 1) // per_page if total > 0 else 1
                self.has_prev = page > 1
                self.has_next = page < self.pages
                self.prev_num = page - 1 if self.has_prev else None
                self.next_num = page + 1 if self.has_next else None
            
            def iter_pages(self, left_edge=1, right_edge=1, left_current=2, right_current=2):
                """Simple page iterator for compatibility"""
                if self.pages <= 10:
                    return range(1, self.pages + 1)
                # For many pages, show first, last, and current area
                pages = []
                for i in range(1, min(left_edge + 1, self.pages + 1)):
                    pages.append(i)
                if left_edge < self.page - left_current - 1:
                    pages.append(None)  # Ellipsis
                for i in range(max(1, self.page - left_current), min(self.page + right_current + 1, self.pages + 1)):
                    if i not in pages:
                        pages.append(i)
                if self.page + right_current < self.pages - right_edge:
                    pages.append(None)  # Ellipsis
                for i in range(max(1, self.pages - right_edge + 1), self.pages + 1):
                    if i not in pages:
                        pages.append(i)
                return pages
        
        pagination = SimplePagination(paginated_articles, page, per_page, total)
        
        return render_template('blog.html', articles=paginated_articles, pagination=pagination)
    except Exception as e:
        current_app.logger.error(f"Error loading blog: {e}")
        import traceback
        traceback.print_exc()
        # Return empty blog page on error
        class SimplePagination:
            def __init__(self):
                self.items = []
                self.page = 1
                self.pages = 1
                self.has_prev = False
                self.has_next = False
        return render_template('blog.html', articles=[], pagination=SimplePagination())

@main_bp.route('/blog/<slug>')
def article(slug):
    """Individual article page - No database required"""
    try:
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
            is_member = False
            if current_user.is_authenticated:
                try:
                    is_member = hasattr(current_user, 'is_active_member') and current_user.is_active_member()
                except:
                    is_member = False
            
            if not is_member:
                flash('This article is available to members only. Please log in or become a member to access it.', 'info')
                return redirect(url_for('auth.login'))
        
        return render_template('article.html', article=article)
    except Exception as e:
        current_app.logger.error(f"Error loading article {slug}: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading article. Please try again later.', 'error')
        return redirect(url_for('main.blog'))

@main_bp.errorhandler(404)
def page_not_found(e):
    """404 error handler"""
    return render_template('errors/404.html'), 404

@main_bp.errorhandler(500)
def internal_server_error(e):
    """500 error handler"""
    db.session.rollback()
    return render_template('errors/500.html'), 500

