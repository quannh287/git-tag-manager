"""
Core module - Chứa logic xử lý Git tag chung cho cả CLI và GUI.
"""

import os
import json
import re
import subprocess
import platform
from typing import Tuple, Dict, Any, Optional

# --- CONFIGURATION ---
CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".git_tag_config.json")


def load_config() -> Dict[str, Any]:
    """
    Load config từ file JSON.
    Nếu file không tồn tại, trả về config rỗng.
    """
    if not os.path.exists(CONFIG_PATH):
        return {"projects": {}}

    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"projects": {}}


def load_or_create_config() -> Tuple[Dict[str, Any], bool]:
    """
    Load config, tạo mới nếu chưa có.
    Returns: (config_data, is_newly_created)
    """
    if not os.path.exists(CONFIG_PATH):
        sample_config = {"projects": {}}
        try:
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(sample_config, f, indent=4)
            return sample_config, True
        except IOError:
            return {"projects": {}}, False

    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f), False
    except (json.JSONDecodeError, IOError):
        return {"projects": {}}, False


def save_config(config_data: Dict[str, Any]) -> None:
    """Lưu config vào file JSON."""
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=4)


def open_config_file() -> None:
    """Mở file config bằng text editor."""
    try:
        if platform.system() == "Darwin":
            # -t flag: mở với default text editor
            subprocess.call(('open', '-t', CONFIG_PATH))
        elif platform.system() == "Windows":
            # Mở với notepad
            subprocess.call(('notepad', CONFIG_PATH))
        else:
            # Linux: thử xdg-open hoặc các text editors phổ biến
            subprocess.call(('xdg-open', CONFIG_PATH))
    except (OSError, subprocess.SubprocessError):
        pass


def run_git(args: list, cwd: str, raise_on_error: bool = True) -> Optional[str]:
    """
    Chạy lệnh git trong thư mục chỉ định.

    Args:
        args: Danh sách tham số cho git (không bao gồm 'git')
        cwd: Thư mục làm việc
        raise_on_error: Nếu True, raise Exception khi lỗi. Nếu False, trả về None.

    Returns:
        Output của lệnh git (stripped), hoặc None nếu lỗi và raise_on_error=False.
    """
    if not os.path.exists(cwd):
        if raise_on_error:
            raise Exception(f"Path not found: {cwd}")
        return None

    try:
        result = subprocess.run(
            ['git'] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        if raise_on_error:
            raise Exception(e.stderr)
        return None


def _build_tag_regex(format_str: str) -> re.Pattern:
    r"""
    Chuyển đổi format string thành regex pattern.

    Ví dụ: "{major}.{minor}.{patch}" -> r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)$"
    """
    regex_pattern = format_str.replace('.', r'\.') \
        .replace('{major}', r'(?P<major>\d+)') \
        .replace('{minor}', r'(?P<minor>\d+)') \
        .replace('{patch}', r'(?P<patch>\d+)') \
        .replace('{build}', r'(?P<build>\d+)')
    return re.compile(f"^{regex_pattern}$")


def _increment_version(parts: Dict[str, int], increment_type: str) -> Dict[str, int]:
    """
    Tăng version theo loại increment.

    Args:
        parts: Dict chứa major, minor, patch, build
        increment_type: 'major', 'minor', 'patch', hoặc 'build'

    Returns:
        Dict mới với version đã được tăng.
    """
    new_parts = parts.copy()

    if increment_type == 'major':
        new_parts['major'] += 1
        new_parts['minor'] = 0
        new_parts['patch'] = 0
        new_parts['build'] = 1
    elif increment_type == 'minor':
        new_parts['minor'] += 1
        new_parts['patch'] = 0
        new_parts['build'] = 1
    elif increment_type == 'patch':
        new_parts['patch'] += 1
        new_parts['build'] = 1
    elif increment_type == 'build':
        new_parts['build'] += 1

    return new_parts


def get_tag_info(path: str, strategy: Dict[str, str]) -> Tuple[str, str]:
    """
    Lấy thông tin tag hiện tại và tính toán tag tiếp theo.

    Args:
        path: Đường dẫn đến Git repository
        strategy: Dict chứa 'format' và 'increment'

    Returns:
        Tuple (current_tag, next_tag)
    """
    # Fetch tags từ remote
    try:
        run_git(['fetch', '--tags'], cwd=path, raise_on_error=False)
        tags_output = run_git(['tag'], cwd=path, raise_on_error=False)
    except Exception:
        return "Error", "Check Path"

    fmt = strategy['format']
    regex = _build_tag_regex(fmt)

    # Parse tất cả tags matching format
    matched_tags = []
    if tags_output:
        for tag in tags_output.split('\n'):
            match = regex.match(tag)
            if match:
                parts = {k: int(v) for k, v in match.groupdict().items()}
                matched_tags.append({'tag': tag, 'parts': parts})

    # Khởi tạo version mặc định
    current_parts = {'major': 1, 'minor': 0, 'patch': 0, 'build': 0}
    latest_tag_str = "None"

    # Tìm tag mới nhất
    if matched_tags:
        matched_tags.sort(key=lambda x: (
            x['parts'].get('major', 0),
            x['parts'].get('minor', 0),
            x['parts'].get('patch', 0),
            x['parts'].get('build', 0)
        ))
        latest = matched_tags[-1]
        current_parts.update(latest['parts'])
        latest_tag_str = latest['tag']

    # Tính toán version tiếp theo
    new_parts = _increment_version(current_parts, strategy['increment'])
    new_tag = fmt.format(**new_parts)

    return latest_tag_str, new_tag


def get_commit_info(path: str) -> str:
    """
    Lấy thông tin commit HEAD hiện tại.

    Returns:
        String format "[hash] message (author)"
    """
    try:
        msg = run_git(['log', '-1', '--pretty=%s (%an)'], cwd=path)
        hash_short = run_git(['rev-parse', '--short', 'HEAD'], cwd=path)
        return f"[{hash_short}] {msg}"
    except Exception:
        return "Unknown Commit"


def get_current_branch(path: str) -> Optional[str]:
    """Lấy tên branch hiện tại."""
    return run_git(['rev-parse', '--abbrev-ref', 'HEAD'], cwd=path, raise_on_error=False)


def create_and_push_tag(path: str, tag: str, message: Optional[str] = None) -> None:
    """
    Tạo annotated tag và push lên origin.

    Args:
        path: Đường dẫn đến Git repository
        tag: Tên tag cần tạo
        message: Message cho tag (mặc định: "Release {tag}")
    """
    if message is None:
        message = f"Release {tag}"

    run_git(['tag', '-a', tag, '-m', message], cwd=path)
    run_git(['push', 'origin', tag], cwd=path)


# Default strategies cho project mới
DEFAULT_STRATEGIES = {
    "staging": {
        "format": "{major}.{minor}.{patch}.{build}-stag",
        "increment": "build"
    },
    "production": {
        "format": "{major}.{minor}.{patch}",
        "increment": "patch"
    }
}
