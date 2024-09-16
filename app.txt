from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from os import path
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.config['SECRET_KEY'] = 'b5d4f2c7e1e2c6d93c8b7d5b9e3f71a2c6d4b5e8f7d6a3b8e4e1b5d4a7f8c6d9a'
app.permanent_session_lifetime = timedelta(days=5)  # Set session lifetime

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///user.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# User model
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)  # Password hash
    is_active = db.Column(db.Boolean, default=True)  # Account status

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password_hash = generate_password_hash(password)  # Hash password on creation

# Story model
class Story(db.Model):
    story_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    user = db.relationship('User', backref=db.backref('stories', lazy=True))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)  # Date posted

    def __init__(self, title, content, user_id):
        self.title = title
        self.content = content
        self.user_id = user_id

# Comment model
class Comment(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    story_id = db.Column(db.Integer, db.ForeignKey('story.story_id'), nullable=False)
    story = db.relationship('Story', backref=db.backref('comments', lazy=True))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    user = db.relationship('User', backref=db.backref('comments', lazy=True))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, content, story_id, user_id):
        self.content = content
        self.story_id = story_id
        self.user_id = user_id

# Message model
class Message(db.Model):
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

@app.route("/")
def home():
    stories = Story.query.all()  # Get all stories
    return render_template("home.html", stories=stories)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password) and user.is_active:
            session.permanent = True  # Set session to permanent
            session["user"] = user.email  # Store email in session
            session["is_admin"] = (user.email == "admin@example.com")  # Store admin status based on email
            return redirect(url_for("user"))

        flash("Invalid credentials or account is deactivated", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "warning")
            return redirect(url_for("register"))

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/user")
def user():
    if "user" in session:
        email = session["user"]
        return render_template("user.html", username=email)
    return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("is_admin", None)  # Remove admin info on logout
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

@app.route("/blog", methods=["GET", "POST"])
def blog():
    if "user" in session:
        if request.method == "POST":
            title = request.form.get("title")
            content = request.form.get("content")
            email = session.get('user')
            user = User.query.filter_by(email=email).first()
            if user:
                new_story = Story(title=title, content=content, user_id=user.user_id)
                db.session.add(new_story)
                db.session.commit()
                flash("Story posted successfully.", "success")
                return redirect(url_for("home"))
            flash("User not found.", "danger")
            return redirect(url_for("login"))
        
        return render_template("blog.html")
    return redirect(url_for("login"))

@app.route("/story/<int:story_id>")
def story_detail(story_id):
    story = Story.query.get_or_404(story_id)
    comments = Comment.query.filter_by(story_id=story_id).all()
    return render_template("story_detail.html", story=story, comments=comments)

@app.route("/add_comment/<int:story_id>", methods=["POST"])
def add_comment(story_id):
    if "user" in session:
        content = request.form.get("content")
        email = session.get('user')
        user = User.query.filter_by(email=email).first()
        
        if user:
            new_comment = Comment(content=content, story_id=story_id, user_id=user.user_id)
            db.session.add(new_comment)
            db.session.commit()
            flash("Comment added successfully.", "success")
        else:
            flash("User not found.", "danger")
        
    return redirect(url_for("story_detail", story_id=story_id))

@app.route("/admin")
def admin_page():
    if "user" in session and session.get("is_admin"):
        users = User.query.all()
        stories = Story.query.all()
        return render_template("admin.html", users=users, stories=stories)
    flash("You need to be an admin to access this page.", "danger")
    return redirect(url_for("login"))

@app.route("/admin/edit_story/<int:story_id>", methods=["GET", "POST"])
def edit_story(story_id):
    if "user" in session and session.get("is_admin"):
        story = Story.query.get_or_404(story_id)
        if request.method == "POST":
            story.title = request.form.get("title")
            story.content = request.form.get("content")
            db.session.commit()
            flash("Story updated successfully.", "success")
            return redirect(url_for("admin_page"))
        return render_template("edit_story.html", story=story)
    flash("You need to be an admin to access this page.", "danger")
    return redirect(url_for("login"))

@app.route("/admin/delete_story/<int:story_id>")
def delete_story(story_id):
    if "user" in session and session.get("is_admin"):
        story = Story.query.get_or_404(story_id)
        db.session.delete(story)
        db.session.commit()
        flash("Story deleted successfully.", "success")
        return redirect(url_for("admin_page"))
    flash("You need to be an admin to access this page.", "danger")
    return redirect(url_for("login"))

@app.route("/admin/manage_users")
def manage_users():
    if "user" in session and session.get("is_admin"):
        users = User.query.all()
        return render_template("manage_users.html", users=users)
    flash("You need to be an admin to access this page.", "danger")
    return redirect(url_for("login"))

@app.route("/admin/activate_user/<int:user_id>")
def activate_user(user_id):
    if "user" in session and session.get("is_admin"):
        user = User.query.get_or_404(user_id)
        user.is_active = True
        db.session.commit()
        flash("User activated successfully.", "success")
        return redirect(url_for("manage_users"))
    flash("You need to be an admin to access this page.", "danger")
    return redirect(url_for("login"))

@app.route("/admin/deactivate_user/<int:user_id>")
def deactivate_user(user_id):
    if "user" in session and session.get("is_admin"):
        user = User.query.get_or_404(user_id)
        user.is_active = False
        db.session.commit()
        flash("User deactivated successfully.", "success")
        return redirect(url_for("manage_users"))
    flash("You need to be an admin to access this page.", "danger")
    return redirect(url_for("login"))

@app.route("/admin/delete_user/<int:user_id>")
def delete_user(user_id):
    if "user" in session and session.get("is_admin"):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        flash("User deleted successfully.", "success")
        return redirect(url_for("manage_users"))
    flash("You need to be an admin to access this page.", "danger")
    return redirect(url_for("login"))

@app.route("/create_admin", methods=["POST"])
def create_admin():
    if not session.get("is_admin"):
        flash("You need to be an admin to create another admin.", "danger")
        return redirect(url_for("login"))
    
    email = "admin@example.com"
    password = "adminpassword"
    if User.query.filter_by(email=email).first():
        flash("Admin already exists.", "warning")
        return redirect(url_for("admin_page"))

    admin_user = User(name="Admin", email=email, password=password)
    db.session.add(admin_user)
    db.session.commit()
    flash("Admin created successfully!", "success")
    return redirect(url_for("admin_page"))

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.errorhandler(HTTPException)
def handle_exception(e):
    return render_template("error.html", error=e), e.code

@app.route("/send_message", methods=["GET", "POST"])
def send_message():
    if "user" in session:
        if request.method == "POST":
            recipient_email = request.form.get("recipient")
            content = request.form.get("content")
            sender_email = session["user"]

            recipient = User.query.filter_by(email=recipient_email).first()
            if recipient:
                sender = User.query.filter_by(email=sender_email).first()
                new_message = Message(sender_id=sender.user_id, recipient_id=recipient.user_id, content=content)
                db.session.add(new_message)
                db.session.commit()
                flash("Tin nhắn đã được gửi thành công!", "success")
            else:
                flash("Người nhận không tồn tại.", "danger")
        
        return render_template("send_message.html")
    return redirect(url_for("login"))

@app.route("/messages")
def messages():
    if "user" in session:
        user_email = session["user"]
        user = User.query.filter_by(email=user_email).first()

        sent_messages = Message.query.filter_by(sender_id=user.user_id).all()
        received_messages = Message.query.filter_by(recipient_id=user.user_id).all()

        return render_template("messages.html", sent_messages=sent_messages, received_messages=received_messages)
    return redirect(url_for("login"))

if __name__ == "__main__":
    if not path.exists("user.db"):
        with app.app_context():
            db.create_all()  # Create all tables
    app.run(debug=True)
