# Git Tag Manager 🧙‍♂️

Công cụ tự động hóa việc đánh version (tagging) cho các dự án Git.

## ✨ Tính Năng

- **Drag & Drop**: Kéo thả thư mục dự án vào GUI để thêm nhanh
- **Đa nền tảng**: Chạy trên macOS, Windows, Linux
- **Dynamic Pattern**: Hỗ trợ mọi định dạng tag thông qua cấu hình
- **Auto Increment**: Tự động tăng version (Major, Minor, Patch, Build)
- **GUI & CLI**: Hỗ trợ cả giao diện đồ họa và dòng lệnh

## 📦 Cài Đặt

### Yêu cầu

- Python 3.8+
- Git đã được cài đặt

### Cài đặt từ source

```bash
# Clone repository
git clone https://github.com/quannh/git-tag-manager.git
cd git-tag-manager

# Cài đặt (editable mode)
pip install -e .
```

### Cài đặt dependencies thủ công

```bash
pip install -r requirements.txt
```

## 🚀 Sử Dụng

### GUI (Giao diện đồ họa)

```bash
git-tag-gui
```

Hoặc chạy trực tiếp:

```bash
python -m git_tag_manager.gui
```

**Thêm dự án mới:**

1. Mở App
2. Kéo thư mục Git repository vào cửa sổ App
3. Nhập tên dự án và nhấn OK

### CLI (Dòng lệnh)

```bash
git-tag-cli
```

Hoặc chạy trực tiếp:

```bash
python -m git_tag_manager.cli
```

## ⚙️ Cấu Hình

Tool sử dụng file cấu hình JSON tại `~/.git_tag_config.json`.

### Ví dụ cấu hình

```json
{
  "projects": {
    "MyApp": {
      "path": "/Users/username/Projects/MyApp",
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

### Format placeholders

| Placeholder | Mô tả                            |
| ----------- | -------------------------------- |
| `{major}`   | Version chính (breaking changes) |
| `{minor}`   | Version phụ (new features)       |
| `{patch}`   | Bản vá (bug fixes)               |
| `{build}`   | Số build                         |

### Increment types

| Type    | Mô tả                               |
| ------- | ----------------------------------- |
| `major` | Tăng major, reset minor/patch/build |
| `minor` | Tăng minor, reset patch/build       |
| `patch` | Tăng patch, reset build             |
| `build` | Chỉ tăng build                      |

## 📦 Đóng gói thành ứng dụng

```bash
# Cài pyinstaller
pip install pyinstaller

# Build ứng dụng (với hỗ trợ drag & drop)
pyinstaller --noconfirm --onefile --windowed \
  --name "GitTagManager" \
  --collect-all tkinterdnd2 \
  -m git_tag_manager.gui
```

## 📄 License

MIT License - xem file [LICENSE](LICENSE) để biết thêm chi tiết.
