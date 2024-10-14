from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

# Khởi tạo đối tượng SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Cấu hình ứng dụng từ tệp config.py
    app.config.from_object('config.Config')

    # Khởi tạo các thành phần
    db.init_app(app)

    # Import các route
    from .routes import main, admin

    # Đăng ký các blueprint cho các nhóm route
    app.register_blueprint(main)
    app.register_blueprint(admin)

    return app
