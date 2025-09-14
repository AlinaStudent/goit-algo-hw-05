# -*- coding: utf-8 -*-
"""
Бенчмарк пошуку підрядка (timeit) для 3 алгоритмів на двох текстах.
Запуск:
    python src/benchmark.py --iters 500
Опції:
    --iters N         кількість повторів для timeit (за замовчуванням 500)
    --exist1 S        існуючий підрядок для статті 1
    --exist2 S        існуючий підрядок для статті 2
    --fake  S         вигаданий підрядок
Результати записуються у results/measurements.csv та results/summary.md
"""
import argparse, timeit, csv, statistics, sys
from pathlib import Path
from typing import Dict, List, Tuple

HERE = Path(__file__).resolve().parent.parent
DATA = HERE / "data"
RESULTS = HERE / "results"
SRC = HERE / "src"

sys.path.insert(0, str(SRC))
from algorithms import ALGORITHMS

def read_data() -> Tuple[str, str]:
    t1 = (DATA / "стаття 1.txt").read_text(encoding="utf-8", errors="ignore")
    t2 = (DATA / "стаття 2 (1).txt").read_text(encoding="utf-8", errors="ignore")
    return t1, t2

def time_algorithm(func, text: str, pattern: str, number: int) -> float:
    t = timeit.repeat(stmt=lambda: func(text, pattern), repeat=3, number=number)
    return statistics.median(t) / number

def run(iters: int, exist1: str, exist2: str, fake: str) -> Dict:
    text1, text2 = read_data()
    cases = [
        ("стаття 1 — існуючий", text1, exist1),
        ("стаття 1 — вигаданий", text1, fake),
        ("стаття 2 — існуючий", text2, exist2),
        ("стаття 2 — вигаданий", text2, fake),
    ]
    rows: List[Dict] = []
    for case_name, text, pat in cases:
        for alg_name, func in ALGORITHMS.items():
            avg_time = time_algorithm(func, text, pat, number=iters)
            idx = func(text, pat)
            rows.append({
                "Випадок": case_name,
                "Алгоритм": alg_name,
                "Знайдено": "так" if idx != -1 else "ні",
                "Середній час, с": f"{avg_time:.9f}",
                "Ітерацій у вимірі": iters,
            })
    # write CSV
    RESULTS.mkdir(exist_ok=True)
    csv_path = RESULTS / "measurements.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Випадок","Алгоритм","Знайдено","Середній час, с","Ітерацій у вимірі"])
        writer.writeheader()
        writer.writerows(rows)
    # aggregate summaries (просте середнє по кожному тексту та загалом)
    # build structure
    per_text = {}
    overall = {}
    for r in rows:
        text_key = "стаття 1" if "стаття 1" in r["Випадок"] else "стаття 2"
        alg = r["Алгоритм"]
        t = float(r["Середній час, с"])
        per_text.setdefault(text_key, {}).setdefault(alg, []).append(t)
        overall.setdefault(alg, []).append(t)
    # compute means
    def mean(lst): return sum(lst) / len(lst) if lst else float("inf")
    winners_text = {}
    for text_key, d in per_text.items():
        means = {alg: mean(v) for alg, v in d.items()}
        winners_text[text_key] = min(means, key=means.get)
    overall_means = {alg: mean(v) for alg, v in overall.items()}
    overall_winner = min(overall_means, key=overall_means.get)

    # write summary.md
    md = []
    md.append("# Висновки щодо швидкості алгоритмів")
    md.append("")
    md.append(f"- **Найшвидший для статті 1:** **{winners_text['стаття 1']}**.")
    md.append(f"- **Найшвидший для статті 2:** **{winners_text['стаття 2']}**.")
    md.append(f"- **Найшвидший загалом:** **{overall_winner}**.")
    md.append("")
    md.append("## Пояснення")
    md.append("- Boyer–Moore часто виграє на природних текстах завдяки великим стрибкам пошуку (евристика «поганого символу»).")
    md.append("- KMP забезпечує лінійний час і стабільність, але без стрибків зазвичай повільніший на відсутніх збігах.")
    md.append("- Rabin–Karp додає накладні витрати на хешування та перевірку збігів; вигідний при пошуку багатьох патернів.")
    md_text = "\n".join(md)
    (RESULTS / "summary.md").write_text(md_text, encoding="utf-8")
    return {
        "rows": rows,
        "winners_per_text": winners_text,
        "overall_winner": overall_winner,
        "csv": str(csv_path),
        "summary_md": str(RESULTS / "summary.md"),
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--iters", type=int, default=500)
    parser.add_argument("--exist1", type=str, default="бібліотеках мов програмування")
    parser.add_argument("--exist2", type=str, default="бази даних рекомендаційної системи")
    parser.add_argument("--fake", type=str, default="xyzяблуко123")
    args = parser.parse_args()
    res = run(args.iters, args.exist1, args.exist2, args.fake)
    print("Готово. CSV:", res["csv"])
    print("Готово. Summary:", res["summary_md"])

if __name__ == "__main__":
    main()
