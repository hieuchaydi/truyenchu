from sys import path
from app import create_app
from app import db

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Tạo tất cả các bảng trong cơ sở dữ liệu
    app.run(debug=True)
