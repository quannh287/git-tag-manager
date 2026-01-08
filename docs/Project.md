Git Tag Manager - Documentation

Git Tag Manager là công cụ tự động hóa việc đánh version (tagging) cho các dự án Git.

1. Tính Năng Chính

Drag & Drop (Mới): Kéo thả thư mục dự án vào GUI để thêm nhanh.

Đa nền tảng: Chạy trên macOS, Windows, Linux.

Dynamic Pattern: Hỗ trợ mọi định dạng tag thông qua cấu hình.

Auto Increment: Tự động tăng version (Major, Minor, Patch, Build).

GUI & CLI: Hỗ trợ cả giao diện và dòng lệnh.

2. Cài Đặt

Yêu cầu hệ thống

Python 3.8 trở lên.

Git đã được cài đặt.

Cài đặt thư viện

Lưu ý: Bạn cần cài thêm tkinterdnd2 cho tính năng kéo thả.

pip install customtkinter rich questionary packaging pyinstaller tkinterdnd2

3. Cấu Hình

Tool sử dụng file cấu hình JSON tại ~/.git_tag_config.json.
Bạn có thể sửa file này thủ công hoặc dùng tính năng Drag & Drop trong App để thêm dự án.

4. Hướng Dẫn Sử Dụng

4.1. Phiên bản GUI (Giao diện)

Chạy app:

python3 git_tag_gui.py

Thêm dự án mới:

Mở App.

Mở Finder/File Explorer, tìm thư mục dự án của bạn.

Kéo thư mục đó và thả vào cửa sổ App.

Nhập tên dự án và nhấn OK. App sẽ tự tạo config mẫu.

Đóng gói thành file chạy (.app):
Khi đóng gói với tính năng kéo thả, bạn cần thêm tham số cho tkinterdnd2:

# Lệnh này yêu cầu pyinstaller tự thu thập hooks

pyinstaller --noconfirm --onefile --windowed --name "GitTagManager" --collect-all tkinterdnd2 git_tag_gui.py

4.2. Phiên bản CLI

python3 git_tag_cli.py
