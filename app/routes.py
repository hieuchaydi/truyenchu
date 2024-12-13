from mailbox import Message
from sys import path
from flask import Blueprint, app, render_template, redirect, url_for, session, flash, request
from flask_login import login_user
from requests_oauthlib import OAuth1
from authlib.integrations.flask_client import OAuth
from config import Config
from .models import Story, Comment, User
from . import db
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import HTTPException
from flask_dance.contrib.github import make_github_blueprint, github

from flask import request, jsonify
from . import db
from .models import User

main = Blueprint('main', __name__)
admin = Blueprint('admin', __name__)








# Trang chủ
@main.route("/")
def home():
    stories = Story.query.all()
    return render_template("home.html", stories=stories)

# Đăng nhập
@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password) and user.is_active:
            session.permanent = True  # Đặt phiên làm việc là vĩnh viễn
            session["user"] = user.email  # Lưu email vào phiên làm việc
            session["is_admin"] = (user.email == "admin@gmail.com")  # Lưu trạng thái admin dựa trên email
            return redirect(url_for("main.user"))  # Sử dụng prefix Blueprint

        flash("Thông tin đăng nhập không hợp lệ hoặc tài khoản đã bị vô hiệu hóa", "danger")
        return redirect(url_for("main.login"))  # Sử dụng prefix Blueprint

    return render_template("login.html")

# Đăng ký
@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Validate email format
        if not email or "@" not in email:
            flash("Địa chỉ email không hợp lệ.", "danger")
            return redirect(url_for("main.register"))

        # Check if the email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email đã được đăng ký.", "warning")
            return redirect(url_for("main.register"))

        # Check if the passwords match
        if password != confirm_password:
            flash("Mật khẩu không khớp.", "danger")
            return redirect(url_for("main.register"))

        try:
            # Create a new user
            new_user = User(email=email)
            new_user.set_password(password)  # Assuming you have a method to hash the password
            db.session.add(new_user)
            db.session.commit()

            flash("Đăng ký thành công! Vui lòng đăng nhập.", "success")
            return redirect(url_for("main.login"))
        except Exception as e:
            db.session.rollback()
            flash("Đăng ký thất bại. Vui lòng thử lại.", "danger")
            print(f"Error during registration: {e}")
            # Optional: Log the error for better debugging
            app.logger.error(f"Error during registration: {e}")

    return render_template("register.html")


@main.route("/check_email", methods=["POST"])
def check_email():
    # Get the email from the request data
    data = request.get_json()
    email = data.get('email')

    # Check if the email already exists in the database
    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({"exists": True})
    else:
        return jsonify({"exists": False})

# User Dashboard Route
@main.route("/user")
def user():
    if "user" in session:
        email = session["user"]
        return render_template("user.html", username=email)
    return redirect(url_for("main.login"))  # Updated to use the Blueprint prefix

# Logout Route
@main.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("is_admin", None)  # Remove admin info on logout
    flash("Bạn đã đăng xuất.", "info")
    return redirect(url_for("main.login"))

# Blog Creation Route
@main.route("/blog", methods=["GET", "POST"])
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
                return redirect(url_for("main.home"))  # Updated to use the Blueprint prefix
            flash("User not found.", "danger")
            return redirect(url_for("main.login"))  # Updated to use the Blueprint prefix
        
        return render_template("blog.html")
    return redirect(url_for("main.login"))  # Updated to use the Blueprint prefix

# Story Detail Route
@main.route("/story/<int:story_id>")
def story_detail(story_id):
    story = Story.query.get_or_404(story_id)
    comments = Comment.query.filter_by(story_id=story_id).all()
    return render_template("story_detail.html", story=story, comments=comments)

# Add Comment Route
@main.route("/add_comment/<int:story_id>", methods=["POST"])
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
        
    return redirect(url_for("main.story_detail", story_id=story_id))  # Updated to use the Blueprint prefix

# Admin Page Route
@admin.route("/admin")
def admin_page():
    """Admin dashboard."""
    if "user" in session and session.get("is_admin"):
        users = User.query.all()
        stories = Story.query.all()
        return render_template("admin.html", users=users, stories=stories)

    flash("You need to be an admin to access this page.", "danger")
    return redirect(url_for("main.login"))

# Route cho quản lý người dùng
@admin.route("/admin/manage_users")
def manage_users():
    """Admin user management page."""
    if "user" in session and session.get("is_admin"):
        users = User.query.all()
        return render_template("manage_users.html", users=users)

    flash("You need to be an admin to access this page.", "danger")
    return redirect(url_for("main.login"))

# Route kích hoạt người dùng
@admin.route("/admin/activate_user/<int:user_id>")
def activate_user(user_id):
    """Admin can activate a user account."""
    if "user" in session and session.get("is_admin"):
        user = User.query.get_or_404(user_id)
        user.is_active = True
        db.session.commit()
        flash("User activated successfully.", "success")
        return redirect(url_for("admin.manage_users"))

    flash("You need to be an admin to access this page.", "danger")
    return redirect(url_for("main.login"))

# Route vô hiệu hóa người dùng
@admin.route("/admin/deactivate_user/<int:user_id>")
def deactivate_user(user_id):
    """Admin can deactivate a user account."""
    if "user" in session and session.get("is_admin"):
        user = User.query.get_or_404(user_id)
        user.is_active = False
        db.session.commit()
        flash("User deactivated successfully.", "success")
        return redirect(url_for("admin.manage_users"))

    flash("You need to be an admin to access this page.", "danger")
    return redirect(url_for("main.login"))

# Route xóa người dùng
@admin.route("/admin/delete_user/<int:user_id>")
def delete_user(user_id):
    """Admin can delete a user account."""
    if "user" in session and session.get("is_admin"):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        flash("User deleted successfully.", "success")
        return redirect(url_for("admin.manage_users"))

    flash("You need to be an admin to access this page.", "danger")
    return redirect(url_for("main.login"))

# Route cho chỉnh sửa câu chuyện
@admin.route("/admin/edit_story/<int:story_id>", methods=["GET", "POST"])
def edit_story(story_id):
    """Allow admin to edit a story."""
    if "user" in session and session.get("is_admin"):
        story = Story.query.get_or_404(story_id)

        if request.method == "POST":
            story.title = request.form.get("title")
            story.content = request.form.get("content")
            db.session.commit()
            flash("Story updated successfully.", "success")
            return redirect(url_for("admin.admin_page"))

        return render_template("edit_story.html", story=story)

    flash("You need to be an admin to access this page.", "danger")
    return redirect(url_for("main.login"))

# Route xóa câu chuyện
@admin.route("/admin/delete_story/<int:story_id>")
def delete_story(story_id):
    """Allow admin to delete a story."""
    if "user" in session and session.get("is_admin"):
        story = Story.query.get_or_404(story_id)
        db.session.delete(story)
        db.session.commit()
        flash("Story deleted successfully.", "success")
        return redirect(url_for("admin.admin_page"))

    flash("You need to be an admin to access this page.", "danger")
    return redirect(url_for("main.login"))

# Route tạo admin
@admin.route("/create_admin", methods=["POST"])
def create_admin():
    """Admin can create a new admin."""
    if "user" not in session or not session.get("is_admin"):
        flash("You need to be an admin to create another admin.", "danger")
        return redirect(url_for("main.login"))

    email = "admin@gmail.com"
    password = "1"  # Weak password, change this in production

    if User.query.filter_by(email=email).first():
        flash("Admin already exists.", "warning")
        return redirect(url_for("admin.admin_page"))

    admin_user = User(email=email, password_hash=generate_password_hash(password))
    db.session.add(admin_user)
    db.session.commit()
    flash("Admin created successfully!", "success")
    return redirect(url_for("admin.admin_page"))

# Route đăng nhập
@admin.route("/login", methods=["GET", "POST"])
def login():
    """User login."""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):  # Sửa ở đây
            session["user"] = user.email
            session["is_admin"] = user.is_admin
            flash("Logged in successfully.", "success")
            return redirect(url_for("admin.admin_page"))

        flash("Login failed. Check your email and password.", "danger")

    return render_template("login.html")


# Route đăng xuất
@admin.route("/logout")
def logout():
    """User logout."""
    session.pop("user", None)
    session.pop("is_admin", None)
    flash("Logged out successfully.", "success")
    return redirect(url_for("main.login")) # Updated to use the Blueprint prefix

# Contact Route
@main.route("/contact")
def contact():
    return render_template("contact.html")

# Caro Game Route
@main.route("/caro")
def caro():
    return render_template("caro.html")

# Error Handling
@main.errorhandler(HTTPException)
def handle_exception(e):
    return render_template("error.html", error=e), e.code

# Send Message Route
@main.route("/send_message", methods=["GET", "POST"])
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
    return redirect(url_for("main.login"))  # Redirect nếu người dùng không đăng nhập

# Messages Route
# Messages Route
@main.route("/messages", methods=["GET"])
def messages():
    if "user" in session:
        user_email = session["user"]
        user = User.query.filter_by(email=user_email).first()

        if user:
            sent_messages = Message.query.filter_by(sender_id=user.user_id).all()
            received_messages = Message.query.filter_by(recipient_id=user.user_id).all()
            return render_template("messages.html", 
                                   sent_messages=sent_messages, 
                                   received_messages=received_messages)
        else:
            flash("User not found.", "danger")
            return redirect(url_for("main.login"))
    return redirect(url_for("main.login"))
@main.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Kiểm tra mật khẩu hiện tại
        user_email = session.get('user')
        user = User.query.filter_by(email=user_email).first()
        if user and check_password_hash(user.password_hash, current_password):
            if new_password == confirm_password:
                user.password_hash = generate_password_hash(new_password)  # Cập nhật mật khẩu mới
                db.session.commit()
                flash("Password changed successfully.", "success")
                return redirect(url_for('main.user'))  # Redirect đến trang người dùng
            else:
                flash("New passwords do not match.", "danger")
        else:
            flash("Current password is incorrect.", "danger")

    return render_template('change_password.html')


if __name__ == "__main__":
    if not path.exists("user.db"):
        with app.app_context():
            db.create_all()  # Create all tables
    app.run(debug=True)

