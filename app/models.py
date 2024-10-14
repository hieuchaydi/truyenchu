from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash

class User(db.Model):
    __tablename__ = 'user'  # Đặt tên bảng rõ ràng

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)  # Mã hóa mật khẩu
    is_active = db.Column(db.Boolean, default=True)  # Trạng thái tài khoản

    # Mối quan hệ với Story và Comment
    stories = db.relationship('Story', back_populates='author', cascade='all, delete-orphan')
    comments = db.relationship('Comment', back_populates='author', cascade='all, delete-orphan')

    def __init__(self, email, password):
        self.email = email
        self.password_hash = generate_password_hash(password)  # Mã hóa mật khẩu khi tạo


class Story(db.Model):
    __tablename__ = 'story'
    story_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

    # Mối quan hệ với User
    author = db.relationship('User', back_populates='stories')  # Sử dụng 'author' thay cho 'user'

    comments = db.relationship('Comment', back_populates='story', cascade='all, delete-orphan')

    def __init__(self, title, content, user_id):
        self.title = title
        self.content = content
        self.user_id = user_id


class Comment(db.Model):
    __tablename__ = 'comment'  # Đặt tên bảng rõ ràng

    comment_id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    story_id = db.Column(db.Integer, db.ForeignKey('story.story_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

    # Mối quan hệ với Story và User
    story = db.relationship('Story', back_populates='comments')
    author = db.relationship('User', back_populates='comments')

    def __init__(self, content, story_id, user_id):
        self.content = content
        self.story_id = story_id
        self.user_id = user_id


class Message(db.Model):
    __tablename__ = 'message'  # Đặt tên bảng rõ ràng

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages')

    def __init__(self, sender_id, recipient_id, content):
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.content = content
