#!/usr/bin/env python3
"""Замер скорости скачивания: N последовательных запросов к одному URL."""

import argparse
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import urlparse

REQUESTS_COUNT = 10
CHUNK_SIZE = 64 * 1024
TIMEOUT = 30  # секунд на установку соединения / ожидание данных


def download(url: str) -> tuple[int, float]:
    """Скачивает ответ целиком, возвращает (байты, секунды)."""
    req = urllib.request.Request(url, headers={"User-Agent": "speedtest/1.0"})
    start = time.perf_counter()
    total = 0
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        while True:
            chunk = resp.read(CHUNK_SIZE)
            if not chunk:
                break
            total += len(chunk)
    return total, time.perf_counter() - start


def main() -> int:
    parser = argparse.ArgumentParser(description="Замер скорости скачивания по URL.")
    parser.add_argument("url", help="адрес файла, например тяжёлой картинки")
    args = parser.parse_args()

    parsed = urlparse(args.url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        print("Ошибка: нужен полный URL, например https://example.com/big.jpg", file=sys.stderr)
        return 2

    total_bytes = 0
    total_time = 0.0

    for i in range(1, REQUESTS_COUNT + 1):
        try:
            size, elapsed = download(args.url)
        except (urllib.error.URLError, OSError) as exc:
            print(f"Запрос {i} не удался: {exc}", file=sys.stderr)
            return 1
        total_bytes += size
        total_time += elapsed
        print(f"Запрос {i:>2}/{REQUESTS_COUNT}: {size} Б за {elapsed:.3f} с")

    avg_time = total_time / REQUESTS_COUNT
    mbit_s = total_bytes * 8 / total_time / 1_000_000 if total_time else 0.0
    mb_s = total_bytes / total_time / 1_000_000 if total_time else 0.0

    print()
    print(f"Среднее время запроса: {avg_time:.3f} с")
    print(f"Всего скачано: {total_bytes} Б ({total_bytes / 1_000_000:.2f} МБ)")
    print(f"Скорость скачивания: {mbit_s:.2f} Мбит/с ({mb_s:.2f} МБ/с)")
    return 0


if __name__ == "__main__":
    sys.exit(main())