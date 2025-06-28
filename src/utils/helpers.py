import os
import subprocess
from datetime import datetime

from src.config.settings import settings


def safe_str(*values, length: int = None) -> str:
    s = ''.join([str(s) for s in values if s is not None])
    return s[:length] if length is not None else s


def write_logs_table_header(page):
    widths = [90, 35, 10, 10, 30, 16, 15, 25]
    headers = ["URL", "Title", "Price", "Odometer", "Username", "Phone", "Car Number", "VIN"]
    header_row = " ".join(f"{header:^{width}}" for header, width in zip(headers, widths))
    header_separator = " ".join("-" * width for width in widths)
    return header_row, header_separator


def make_db_dump():
    os.makedirs("dumps", exist_ok=True)
    filename = f"dumps/dump_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"

    cmd = [
        "pg_dump",
        "-h", settings.DB_HOST,
        "-p", str(settings.DB_PORT),
        "-U", settings.POSTGRES_USER,
        "-d", settings.POSTGRES_DB,
        "-f", filename
    ]

    env = os.environ.copy()
    env["PGPASSWORD"] = settings.POSTGRES_PASSWORD

    subprocess.run(cmd, env=env)
