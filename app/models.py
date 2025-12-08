"""
Database Models
"""

from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import enum

class MembershipType(enum.Enum):
    """Membership type enumeration"""
    ANNUAL = 'annual'
    LIFETIME = 'lifetime'
    SUPPORTER = 'supporter'

class MembershipStatus(enum.Enum):
    """Membership status enumeration"""
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    EXPIRED = 'expired'
    PENDING = 'pending'

class PaymentStatus(enum.Enum):
    """Payment transaction status"""
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'
    CANCELLED = 'cancelled'

class User(UserMixin, db.Model):
    """User model for members"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    membership_type = db.Column(db.Enum(MembershipType), nullable=True)
    membership_status = db.Column(db.Enum(MembershipStatus), default=MembershipStatus.INACTIVE)
    stripe_customer_id = db.Column(db.String(255), nullable=True, index=True)
    stripe_subscription_id = db.Column(db.String(255), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    articles = db.relationship('Article', backref='author', lazy='dynamic')
    transactions = db.relationship('MembershipTransaction', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_active_member(self):
        """Check if user has active membership"""
        return self.membership_status == MembershipStatus.ACTIVE
    
    def __repr__(self):
        return f'<User {self.email}>'

class Article(db.Model):
    """Blog article model"""
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text, nullable=True)
    featured_image = db.Column(db.String(255), nullable=True)
    is_member_only = db.Column(db.Boolean, default=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    published_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def is_published(self):
        """Check if article is published"""
        return self.published_at is not None and self.published_at <= datetime.utcnow()
    
    def reading_time(self):
        """Estimate reading time in minutes"""
        words_per_minute = 200
        word_count = len(self.content.split())
        return max(1, round(word_count / words_per_minute))
    
    def __repr__(self):
        return f'<Article {self.title}>'

class MembershipTransaction(db.Model):
    """Membership payment transaction model"""
    __tablename__ = 'membership_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    stripe_payment_intent_id = db.Column(db.String(255), nullable=True, index=True)
    stripe_subscription_id = db.Column(db.String(255), nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')
    status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING)
    membership_type = db.Column(db.Enum(MembershipType), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<MembershipTransaction {self.id} - {self.status.value}>'

