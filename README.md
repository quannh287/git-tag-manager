# Git Tag Manager 🧙‍♂️

Công cụ tự động hóa việc đánh version (tagging) cho các dự án Git.

---

## ✨ Tính Năng

| Tính năng           | Mô tả                                             |
| ------------------- | ------------------------------------------------- |
| **Drag & Drop**     | Kéo thả thư mục dự án vào GUI để thêm nhanh       |
| **Đa nền tảng**     | Chạy trên macOS, Windows, Linux                   |
| **Dynamic Pattern** | Hỗ trợ mọi định dạng tag thông qua cấu hình       |
| **Auto Increment**  | Tự động tăng version (Major, Minor, Patch, Build) |
| **GUI & CLI**       | Hỗ trợ cả giao diện đồ họa và dòng lệnh           |

---

## 📦 Cài Đặt

### Yêu cầu hệ thống

- Python 3.8 trở lên
- Git đã được cài đặt

### Cài đặt từ source

```bash
# Clone repository
git clone https://github.com/quannh287/git-tag-manager.git
cd git-tag-manager

# Cài đặt package (editable mode)
pip install -e .
```

### Cài đặt thủ công

```bash
pip install -r requirements.txt
```

---

## ⚙️ Cấu Hình

Tool sử dụng file cấu hình JSON tại `~/.git_tag_config.json`.

### Cấu trúc file config

```json
{
  "projects": {
    "TenDuAn": {
      "path": "/duong/dan/den/project",
      "strategies": {
        "staging": {
          "format": "{major}.{minor}.{patch}.{build}-stag",
          "increment": "build"
        },
        "production": {
          "format": "{major}.{minor}.{patch}",
          "increment": "patch"
        }
      }
    }
  }
}
```

### Format Placeholders

| Placeholder | Mô tả                            | Ví dụ      |
| ----------- | -------------------------------- | ---------- |
| `{major}`   | Version chính (breaking changes) | `2.0.0`    |
| `{minor}`   | Version phụ (new features)       | `1.3.0`    |
| `{patch}`   | Bản vá (bug fixes)               | `1.0.5`    |
| `{build}`   | Số build                         | `1.0.0.42` |

### Increment Types

| Type    | Hành động                                | Ví dụ                 |
| ------- | ---------------------------------------- | --------------------- |
| `major` | Tăng major, reset minor/patch/build về 0 | `1.2.3` → `2.0.0`     |
| `minor` | Tăng minor, reset patch/build về 0       | `1.2.3` → `1.3.0`     |
| `patch` | Tăng patch, reset build về 1             | `1.2.3` → `1.2.4`     |
| `build` | Chỉ tăng build                           | `1.0.0.5` → `1.0.0.6` |

---

## 🚀 Hướng Dẫn Sử Dụng

### GUI (Giao diện đồ họa)

**Khởi chạy:**

```bash
git-tag-gui
# hoặc
python3 -m manager.gui
```

**Thêm dự án mới:**

1. Mở App
2. Mở Finder/File Explorer, tìm thư mục dự án Git
3. **Kéo thư mục** và **thả vào cửa sổ App**
4. Nhập tên dự án và nhấn **OK**
5. App sẽ tự tạo config mẫu với 2 strategies: `staging` và `production`

**Tạo tag:**

1. Chọn **Project** từ dropdown
2. Chọn **Strategy** (staging/production)
3. Xem thông tin **Current Tag** và **Next Tag**
4. Click **Create Tag & Push**
5. Xác nhận và chờ push lên origin

### CLI (Dòng lệnh)

**Khởi chạy:**

```bash
git-tag-cli
# hoặc
python3 -m manager.cli
```

**Quy trình:**

1. Chọn project từ danh sách
2. Chọn strategy
3. Xem bảng thông tin (path, branch, current tag, next tag, commit)
4. Xác nhận tạo tag và push

**Ví dụ output:**

```
┌─────────────────────────────────────┐
│     Git Tag Manager CLI             │
└─────────────────────────────────────┘
? Select Project: MyApp
? Select Strategy: staging

┌──────────────┬────────────────────────────┐
│ Property     │ Value                      │
├──────────────┼────────────────────────────┤
│ Project Path │ /Users/dev/MyApp           │
│ Branch       │ main                       │
│ Current Tag  │ 1.0.0.5-stag               │
│ NEXT TAG     │ 1.0.0.6-stag               │
│ Commit       │ fix: update login flow...  │
└──────────────┴────────────────────────────┘

? Create tag 1.0.0.6-stag and PUSH? Yes
✔ Tag 1.0.0.6-stag created and pushed to origin.
```

---

## 📦 Build & Đóng Gói

### Build DMG cho macOS

```bash
./build_app.sh
```

**Output:**

- `dist/GitTagManager.app` - macOS app bundle
- `dist/GitTagManager-{version}.dmg` - DMG installer

### Build thủ công với PyInstaller

```bash
pip install pyinstaller

pyinstaller --noconfirm --onedir --windowed \
  --name "GitTagManager" \
  --collect-all tkinterdnd2 \
  --collect-all customtkinter \
  run_gui.py
```

**Lưu ý:** `--collect-all tkinterdnd2` là **bắt buộc** để drag & drop hoạt động.

---

## 🔧 Troubleshooting

### Config file không tồn tại

App sẽ tự tạo file config rỗng khi khởi chạy lần đầu:

```bash
echo '{"projects": {}}' > ~/.git_tag_config.json
```

### Drag & Drop không hoạt động

Đảm bảo đã cài đặt `tkinterdnd2`:

```bash
pip install tkinterdnd2
```

### Permission denied khi push

Kiểm tra Git credentials và quyền truy cập repository.

---

## 📄 License

MIT License - Xem file [LICENSE](LICENSE) để biết thêm chi tiết.
