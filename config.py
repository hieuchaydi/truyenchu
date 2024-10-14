import os

class Config:
    # Sử dụng biến môi trường để lấy SECRET_KEY, nếu không thì dùng giá trị mặc định
    SECRET_KEY = os.getenv('SECRET_KEY', 'b5d4f2c7e1e2c6d93c8b7d5b9e3f71a2c6d4b5e8f7d6a3b8e4e1b5d4a7f8c6d9a')

    # Đường dẫn tuyệt đối đến cơ sở dữ liệu SQLite
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'user.db'))

    # Vô hiệu hóa thông báo về theo dõi sửa đổi
    SQLALCHEMY_TRACK_MODIFICATIONS = False
