"""Підсумок навантажувального тесту JMeter і моніторингу контейнерів.

Використання: python3 scripts/summarize-load-test.py results.jtl [docker-stats.csv]

Виводить таблиці у форматі Markdown (для GitHub Step Summary). Завершується
з кодом 1, якщо частка помилок перевищує MAX_ERROR_RATE (відсотків, за
замовчуванням 1).
"""

import csv
import math
import os
import re
import sys
from collections import defaultdict

MAX_ERROR_RATE = float(os.getenv("MAX_ERROR_RATE", "1"))
UNITS = {
    "B": 1 / 1024**2,
    "KB": 1 / 1024,
    "KIB": 1 / 1024,
    "MB": 1.0,
    "MIB": 1.0,
    "GB": 1024.0,
    "GIB": 1024.0,
}


def read_csv(path):
    with open(path, encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def percentile(sorted_values, fraction):
    index = max(math.ceil(fraction * len(sorted_values)) - 1, 0)
    return sorted_values[index]


def summarize_jmeter(path):
    rows = read_csv(path)
    if not rows:
        print("## Навантажувальне тестування\n\nФайл результатів порожній.")
        return None

    elapsed = sorted(int(r["elapsed"]) for r in rows)
    failed = sum(1 for r in rows if r["success"].lower() != "true")
    start = min(int(r["timeStamp"]) for r in rows)
    end = max(int(r["timeStamp"]) + int(r["elapsed"]) for r in rows)
    duration = max((end - start) / 1000, 0.001)
    error_rate = failed * 100 / len(rows)

    print("## Навантажувальне тестування (JMeter)\n")
    print("| Показник | Значення |")
    print("|---|---|")
    print(f"| Запитів | {len(rows)} |")
    print(f"| Помилок | {failed} ({error_rate:.2f} %) |")
    print(f"| Пропускна здатність | {len(rows) / duration:.1f} запитів/с |")
    print(f"| Середній час відповіді | {sum(elapsed) / len(elapsed):.1f} мс |")
    print(f"| 95-й перцентиль | {percentile(elapsed, 0.95)} мс |")
    print(f"| Максимум | {elapsed[-1]} мс |")

    by_label = defaultdict(list)
    for r in rows:
        by_label[r["label"]].append(int(r["elapsed"]))
    print("\n| Запит | Кількість | Середній, мс | 95-й перцентиль, мс |")
    print("|---|---|---|---|")
    for label, values in by_label.items():
        values.sort()
        average = sum(values) / len(values)
        p95 = percentile(values, 0.95)
        print(f"| `{label}` | {len(values)} | {average:.1f} | {p95} |")
    return error_rate


def to_mib(text):
    match = re.match(r"\s*([\d.]+)\s*([A-Za-z]+)", text)
    if not match:
        return 0.0
    return float(match.group(1)) * UNITS.get(match.group(2).upper(), 1.0)


def summarize_containers(path):
    rows = read_csv(path)
    if not rows:
        return
    stats = defaultdict(lambda: {"cpu": [], "mem": [], "mem_pct": []})
    for r in rows:
        item = stats[r["container"]]
        item["cpu"].append(float(r["cpu_percent"].strip("%") or 0))
        item["mem"].append(to_mib(r["mem_usage"].split("/")[0]))
        item["mem_pct"].append(float(r["mem_percent"].strip("%") or 0))

    print("\n## Ресурси контейнерів (docker stats)\n")
    print("| Контейнер | Вимірювань | CPU сер., % | CPU макс., % | RAM макс., МіБ |")
    print("|---|---|---|---|---|")
    for name, item in sorted(stats.items()):
        count = len(item["cpu"])
        cpu_avg = sum(item["cpu"]) / count
        print(
            f"| `{name}` | {count} | {cpu_avg:.1f} | {max(item['cpu']):.1f} "
            f"| {max(item['mem']):.1f} |"
        )


def main():
    if len(sys.argv) < 2:
        sys.exit("Використання: summarize-load-test.py results.jtl [docker-stats.csv]")
    error_rate = summarize_jmeter(sys.argv[1])
    if len(sys.argv) > 2 and os.path.exists(sys.argv[2]):
        summarize_containers(sys.argv[2])
    if error_rate is None or error_rate > MAX_ERROR_RATE:
        print(f"\n**Тест не пройдено:** помилок більше за {MAX_ERROR_RATE} %.")
        sys.exit(1)
    print(f"\n**Тест пройдено:** помилок не більше за {MAX_ERROR_RATE} %.")


if __name__ == "__main__":
    main()
