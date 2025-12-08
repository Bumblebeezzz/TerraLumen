"""
Admin panel routes
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from app import db
from app.models import User, Article, MembershipTransaction
from datetime import datetime
import re

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin access"""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard"""
    total_members = User.query.count()
    active_members = User.query.filter_by(membership_status=MembershipStatus.ACTIVE).count()
    total_articles = Article.query.count()
    published_articles = Article.query.filter(Article.published_at.isnot(None)).count()
    
    recent_members = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_articles = Article.query.order_by(Article.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_members=total_members,
                         active_members=active_members,
                         total_articles=total_articles,
                         published_articles=published_articles,
                         recent_members=recent_members,
                         recent_articles=recent_articles)

@admin_bp.route('/articles')
@login_required
@admin_required
def articles():
    """List all articles"""
    articles = Article.query.order_by(Article.created_at.desc()).all()
    return render_template('admin/articles.html', articles=articles)

@admin_bp.route('/articles/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_article():
    """Create new article"""
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        excerpt = request.form.get('excerpt')
        is_member_only = bool(request.form.get('is_member_only'))
        publish_now = bool(request.form.get('publish_now'))
        
        if not title or not content:
            flash('Title and content are required.', 'error')
            return render_template('admin/article_form.html')
        
        # Generate slug from title
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        
        # Ensure slug is unique
        base_slug = slug
        counter = 1
        while Article.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        article = Article(
            title=title,
            slug=slug,
            content=content,
            excerpt=excerpt,
            is_member_only=is_member_only,
            author_id=current_user.id,
            published_at=datetime.utcnow() if publish_now else None
        )
        
        db.session.add(article)
        db.session.commit()
        
        flash('Article created successfully!', 'success')
        return redirect(url_for('admin.articles'))
    
    return render_template('admin/article_form.html')

@admin_bp.route('/articles/<int:article_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_article(article_id):
    """Edit article"""
    article = Article.query.get_or_404(article_id)
    
    if request.method == 'POST':
        article.title = request.form.get('title')
        article.content = request.form.get('content')
        article.excerpt = request.form.get('excerpt')
        article.is_member_only = bool(request.form.get('is_member_only'))
        
        # Update slug if title changed
        new_slug = re.sub(r'[^\w\s-]', '', article.title.lower())
        new_slug = re.sub(r'[-\s]+', '-', new_slug)
        if new_slug != article.slug:
            base_slug = new_slug
            counter = 1
            while Article.query.filter(Article.slug == new_slug, Article.id != article.id).first():
                new_slug = f"{base_slug}-{counter}"
                counter += 1
            article.slug = new_slug
        
        # Handle publishing
        if request.form.get('publish_now') and not article.published_at:
            article.published_at = datetime.utcnow()
        elif request.form.get('unpublish'):
            article.published_at = None
        
        db.session.commit()
        flash('Article updated successfully!', 'success')
        return redirect(url_for('admin.articles'))
    
    return render_template('admin/article_form.html', article=article)

@admin_bp.route('/articles/<int:article_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_article(article_id):
    """Delete article"""
    article = Article.query.get_or_404(article_id)
    db.session.delete(article)
    db.session.commit()
    flash('Article deleted successfully!', 'success')
    return redirect(url_for('admin.articles'))

@admin_bp.route('/members')
@login_required
@admin_required
def members():
    """List all members"""
    members = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/members.html', members=members)

@admin_bp.route('/members/<int:user_id>')
@login_required
@admin_required
def view_member(user_id):
    """View member details"""
    user = User.query.get_or_404(user_id)
    transactions = MembershipTransaction.query.filter_by(user_id=user_id).order_by(MembershipTransaction.created_at.desc()).all()
    return render_template('admin/member_detail.html', user=user, transactions=transactions)

