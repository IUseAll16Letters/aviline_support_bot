from pathlib import Path
from typing import List, Dict

from config import settings


def log_files_list() -> List[Path]:
    files = []
    for log_file in Path(settings.LOG_FILE_LOCATION.parent).iterdir():
        if not log_file.name.startswith('.'):
            files.append(log_file)
    return sorted(files, reverse=True)


def parse_log_file(file_dest: Path) -> str:
    file_lines_str: List[str] = []
    err_status_item = 2
    log_types_colors: Dict[str, str] = {
        'INFO': 'dark',
        'DEBUG': 'primary',
        'WARNING': 'warning',
        'ERROR': 'danger',
        'CRITICAL': 'danger',
    }

    with open(file_dest, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            if line.startswith('20'):
                line = line.split()
                status_color = log_types_colors[line[err_status_item].split(':')[0]]
                line_as_html = f'<p class="text-{status_color}">' + ' '.join(line) + '</p>\n'
                file_lines_str.append(line_as_html)
            else:
                file_lines_str.append(line)

    return f'<hr><h3>{file_dest.name}</h3>\n' + ''.join(file_lines_str)


def pack_log_files_as_html() -> str:
    log_files_read_as_str = []
    for log_file_dest in log_files_list():
        log_files_read_as_str.append(parse_log_file(log_file_dest))

    return "\n".join(log_files_read_as_str)
