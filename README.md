
@app.route("/admin")
def admin_page():
    """Hiển thị trang quản trị cho admin."""
    if "user" in session and session.get("is_admin"):
        users = User.query.all()
        stories = Story.query.all()
        return render_template("admin.html", users=users, stories=stories)
    
    flash("You need to be an admin to access this page.", "danger")
    return redirect(url_for("login"))  # Điều hướng đến trang đăng nhập nếu không có quyền

@app.route("/admin/edit_story/<int:story_id>", methods=["GET", "POST"])
def edit_story(story_id):
    """Cho phép admin chỉnh sửa câu chuyện."""
    if "user" in session and session.get("is_admin"):
        story = Story.query.get_or_404(story_id)
        
        if request.method == "POST":
            # Cập nhật thông tin câu chuyện từ biểu mẫu
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
    """Cho phép admin xóa câu chuyện."""
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
    """Hiển thị trang quản lý người dùng cho admin."""
    if "user" in session and session.get("is_admin"):
        users = User.query.all()
        return render_template("manage_users.html", users=users)

    flash("You need to be an admin to access this page.", "danger")
    return redirect(url_for("login"))

@app.route("/admin/activate_user/<int:user_id>")
def activate_user(user_id):
    """Cho phép admin kích hoạt tài khoản người dùng."""
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
    """Cho phép admin vô hiệu hóa tài khoản người dùng."""
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
    """Cho phép admin xóa tài khoản người dùng."""
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
    """Cho phép admin tạo một admin mới."""
    if not session.get("is_admin"):
        flash("You need to be an admin to create another admin.", "danger")
        return redirect(url_for("login"))

    email = "admin@example.com"
    password = "1"  # Mật khẩu yếu, nên thay đổi

    if User.query.filter_by(email=email).first():
        flash("Admin already exists.", "warning")
        return redirect(url_for("admin_page"))

    admin_user = User(name="Admin", email=email, password=password)
    db.session.add(admin_user)
    db.session.commit()
    flash("Admin created successfully!", "success")
    return redirect(url_for("admin_page"))


truyenchu.onrender.com
