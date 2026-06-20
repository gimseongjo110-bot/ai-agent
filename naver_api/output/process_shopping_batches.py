#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""5개 배치(JSON)를 '패션의류' 앵커 기준으로 환산해 11개 대분류를 하나의 척도로 합친다."""

import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.abspath(__file__))
ANCHOR = "패션의류"

batch_files = [f"batch{i}.json" for i in range(1, 6)]
batches = []
for fname in batch_files:
    with open(os.path.join(BASE, fname), encoding="utf-8") as f:
        batches.append(json.load(f))

# 1) period -> anchor ratio, 배치1(=정규 기준 척도) 기준으로
anchor_by_period_batch1 = {}
for result in batches[0]["results"]:
    if result["title"] == ANCHOR:
        for d in result["data"]:
            anchor_by_period_batch1[d["period"]] = d["ratio"]

periods = sorted(anchor_by_period_batch1.keys())

# 2) 카테고리별 rescaled ratio 테이블 구성
table = {p: {} for p in periods}
table_for_period = {p: {ANCHOR: anchor_by_period_batch1[p]} for p in periods}

for batch in batches:
    anchor_in_batch = {}
    for result in batch["results"]:
        if result["title"] == ANCHOR:
            for d in result["data"]:
                anchor_in_batch[d["period"]] = d["ratio"]

    for result in batch["results"]:
        if result["title"] == ANCHOR:
            continue
        for d in result["data"]:
            period = d["period"]
            raw_ratio = d["ratio"]
            anchor_ref = anchor_by_period_batch1.get(period)
            anchor_here = anchor_in_batch.get(period)
            if anchor_ref is None or not anchor_here:
                continue
            rescaled = raw_ratio * (anchor_ref / anchor_here)
            table_for_period[period][result["title"]] = rescaled

categories = [ANCHOR, "패션잡화", "화장품_미용", "디지털_가전", "가구_인테리어",
              "출산_육아", "식품", "스포츠_레저", "생활_건강", "여가_생활편의", "도서"]

# 3) CSV 출력 (주간 ratio 표, 환산된 공통 척도)
csv_path = os.path.join(BASE, "shopping_category_weekly_ratio_2025-01_2026-06_20-30s.csv")
with open(csv_path, "w", encoding="utf-8-sig") as f:
    f.write("period," + ",".join(categories) + "\n")
    for p in periods:
        row = [p]
        for c in categories:
            v = table_for_period[p].get(c)
            row.append(f"{v:.4f}" if v is not None else "")
        f.write(",".join(row) + "\n")

# 4) 주간 1위 카테고리
weekly_top_path = os.path.join(BASE, "shopping_weekly_top_category_20-30s.csv")
with open(weekly_top_path, "w", encoding="utf-8-sig") as f:
    f.write("period,top_category,top_ratio\n")
    for p in periods:
        row = table_for_period[p]
        top_cat = max(row, key=row.get)
        f.write(f"{p},{top_cat},{row[top_cat]:.4f}\n")

# 5) 전체 평균 기준 랭킹
avg_ranking = []
for c in categories:
    vals = [table_for_period[p][c] for p in periods if c in table_for_period[p]]
    avg_ranking.append((c, sum(vals) / len(vals), len(vals)))
avg_ranking.sort(key=lambda x: -x[1])

print("=== 카테고리 평균 ratio 순위 (2025-01-01~2026-06-20, 주간, 20~30대) ===")
for rank, (c, avg, n) in enumerate(avg_ranking, 1):
    print(f"{rank:2d}. {c:10s}  평균 {avg:7.2f}  (n={n})")

print()
print(f"전체 주간 ratio 표 저장: {csv_path}")
print(f"주간 1위 카테고리 표 저장: {weekly_top_path}")
print(f"총 주(week) 수: {len(periods)}")

# 6) 주간 1위 카테고리 집계 (몇 주씩 1위였는지)
from collections import Counter
top_counter = Counter()
with open(weekly_top_path, encoding="utf-8-sig") as f:
    next(f)
    for line in f:
        period, top_cat, top_ratio = line.strip().split(",")
        top_counter[top_cat] += 1

print()
print("=== 주간 1위 횟수 (전체", len(periods), "주 중) ===")
for cat, cnt in top_counter.most_common():
    print(f"{cat:10s} : {cnt}주")
