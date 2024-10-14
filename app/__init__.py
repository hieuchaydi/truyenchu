from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

# Khởi tạo đối tượng SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Cấu hình ứng dụng
    app.config['SECRET_KEY'] = 'b5d4f2c7e1e2c6d93c8b7d5b9e3f71a2c6d4b5e8f7d6a3b8e4e1b5d4a7f8c6d9a'
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///user.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.permanent_session_lifetime = timedelta(days=5)
    
    # Khởi tạo các thành phần
    db.init_app(app)

    # Import các route
    from .routes import main, admin

    # Đăng ký các blueprint cho các nhóm route
    app.register_blueprint(main)
    app.register_blueprint(admin)

    return app
