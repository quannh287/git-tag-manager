# Contributing Guide - Git Tag Manager

Hướng dẫn đóng góp và phát triển Git Tag Manager.

---

## 📋 Yêu Cầu

- Python 3.8+
- Git
- macOS (để build app)

---

## 🚀 Setup Development Environment

### 1. Clone repository

```bash
git clone <repository-url>
cd git-tag-manager
```

### 2. Cài đặt dependencies

```bash
# Cài đặt package ở chế độ editable
pip install -e .

# Hoặc chỉ cài dependencies
pip install -r requirements.txt
```

### 3. Verify installation

```bash
# Test import
python3 -c "from manager import __version__; print(__version__)"
```

---

## 🐛 Debug & Run

### Chạy GUI (Development)

```bash
# Cách 1: Chạy trực tiếp module
python3 -m manager.gui

# Cách 2: Dùng entry point (sau khi pip install -e .)
git-tag-gui
```

### Chạy CLI (Development)

```bash
# Cách 1: Chạy trực tiếp module
python3 -m manager.cli

# Cách 2: Dùng entry point
git-tag-cli
```

### Debug với VS Code

Tạo file `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug GUI",
      "type": "debugpy",
      "request": "launch",
      "module": "manager.gui",
      "cwd": "${workspaceFolder}"
    },
    {
      "name": "Debug CLI",
      "type": "debugpy",
      "request": "launch",
      "module": "manager.cli",
      "cwd": "${workspaceFolder}"
    }
  ]
}
```

### Debug với PyCharm

1. Run > Edit Configurations
2. Add New > Python
3. Module name: `manager.gui` hoặc `manager.cli`
4. Working directory: project root

---

## 📁 Project Structure

```
git-tag-manager/
├── manager/           # Main package
│   ├── __init__.py            # Package init, version
│   ├── core.py                # Core logic (shared)
│   ├── cli.py                 # CLI interface
│   └── gui.py                 # GUI interface
├── assets/                    # App icons
├── docs/                      # Documentation
├── build_app.sh               # Build script for macOS app
├── run_gui.py                 # Entry point for PyInstaller
├── pyproject.toml             # Build config
├── requirements.txt           # Dependencies
└── README.md
```

---

## 🔧 Making Changes

### 1. Core Logic (`core.py`)

Chứa logic xử lý Git tag, được dùng chung bởi cả CLI và GUI:

- `load_config()` / `save_config()` - Quản lý config
- `run_git()` - Chạy git commands
- `get_tag_info()` - Tính toán version tiếp theo

### 2. GUI (`gui.py`)

- Sử dụng `customtkinter` cho giao diện dark mode
- `tkinterdnd2` cho drag & drop
- Kế thừa từ `TkinterDnD.DnDWrapper`

### 3. CLI (`cli.py`)

- Sử dụng `rich` cho terminal styling
- `questionary` cho interactive prompts

---

## 🏗️ Build App

### Build macOS app

```bash
chmod +x build_app.sh
./build_app.sh
```

Output: `dist/GitTagManager.app`

### Build steps:

1. Convert PNG → `.icns` icon
2. PyInstaller với `--onedir --windowed`
3. Collect `tkinterdnd2` và `customtkinter`

---

## ✅ Testing Changes

### Manual testing

1. Chạy GUI/CLI ở development mode
2. Test các tính năng:
   - Drag & drop thêm project
   - Chọn project/strategy
   - Tính toán tag mới
   - Tạo và push tag

### Test config

Config file: `~/.git_tag_config.json`

```bash
# Xem config
cat ~/.git_tag_config.json

# Reset config (nếu cần)
rm ~/.git_tag_config.json
```

---

## 📝 Coding Guidelines

1. **Type hints**: Sử dụng type hints cho functions
2. **Docstrings**: Viết docstring cho functions/classes
3. **Error handling**: Wrap Git operations trong try/except
4. **Threading**: GUI operations cần chạy Git commands trong background thread

---

## 🔀 Pull Request

1. Fork repository
2. Tạo feature branch: `git checkout -b feat/my-feature`
3. Commit changes (theo [Conventional Commits](https://www.conventionalcommits.org/))
4. Push và tạo Pull Request

### Commit format

```
<type>(<scope>): <subject>

<body>
```

Types: `feat`, `fix`, `refactor`, `docs`, `style`, `test`, `chore`

---

## 📄 License

MIT License
