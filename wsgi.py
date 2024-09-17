import sys
import os

# Đường dẫn đến thư mục chứa dự án của bạn
project_home = '/home/hieu4200/truyenchu'
if project_home not in sys.path:
    sys.path.append(project_home)

from app import app as application  # Thay đổi 'app' thành tên của file chính chứa Flask app
