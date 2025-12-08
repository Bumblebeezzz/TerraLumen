"""
Blog loader utility - Loads blog articles from JSON files
No database required
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class BlogArticle:
    """Simple blog article class"""
    def __init__(self, data: dict):
        self.id = data.get('id')
        self.title = data.get('title', '')
        self.slug = data.get('slug', '')
        self.content = data.get('content', '')
        self.excerpt = data.get('excerpt', '')
        self.author = data.get('author', 'TerraLumen Team')
        self.published_at = data.get('published_at')
        self.is_member_only = data.get('is_member_only', False)
        self.tags = data.get('tags', [])
        self.featured_image = data.get('featured_image', '')
        
        # Parse published_at if it's a string
        if isinstance(self.published_at, str):
            try:
                self.published_at = datetime.fromisoformat(self.published_at.replace('Z', '+00:00'))
            except:
                self.published_at = None
    
    def is_published(self) -> bool:
        """Check if article is published"""
        if not self.published_at:
            return False
        return self.published_at <= datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'content': self.content,
            'excerpt': self.excerpt,
            'author': self.author,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'is_member_only': self.is_member_only,
            'tags': self.tags,
            'featured_image': self.featured_image
        }

def load_blog_articles() -> List[BlogArticle]:
    """Load all blog articles from JSON files"""
    articles = []
    # Get the project root directory
    current_file = Path(__file__).resolve()
    # Go up: utils -> app -> terralumen_website
    blog_dir = current_file.parent.parent.parent / 'app' / 'data' / 'blog'
    
    # Create directory if it doesn't exist
    blog_dir.mkdir(parents=True, exist_ok=True)
    
    # Load articles from JSON files
    if blog_dir.exists():
        for json_file in blog_dir.glob('*.json'):
            # Skip .gitkeep and other non-article files
            if json_file.name.startswith('.'):
                continue
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    article = BlogArticle(data)
                    articles.append(article)
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
                continue
    
    # Sort by published_at (newest first)
    articles.sort(key=lambda x: x.published_at if x.published_at else datetime.min, reverse=True)
    
    return articles

def get_article_by_slug(slug: str) -> Optional[BlogArticle]:
    """Get a single article by slug"""
    articles = load_blog_articles()
    for article in articles:
        if article.slug == slug:
            return article
    return None

def get_published_articles(member_only: bool = False) -> List[BlogArticle]:
    """Get published articles, optionally filter by member-only"""
    articles = load_blog_articles()
    published = [a for a in articles if a.is_published()]
    
    if not member_only:
        published = [a for a in published if not a.is_member_only]
    
    return published

