#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 데이터랩 쇼핑인사이트 분야별 트렌드 조회 API 호출 스크립트

사용법:
    python datalab_shopping_category.py                              # 기본 예시(패션의류 vs 화장품/미용) 조회
    python datalab_shopping_category.py "패션의류:50000000" "화장품/미용:50000002"
"""

import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import json

from common import load_credentials, post_json

API_URL = "https://openapi.naver.com/v1/datalab/shopping/categories"

DEFAULT_CATEGORIES = [
    {"name": "패션의류", "param": ["50000000"]},
    {"name": "화장품/미용", "param": ["50000002"]},
]


def parse_categories(args: list) -> list:
    """'분야명:카테고리코드1,카테고리코드2' 형식의 인자를 category 배열로 변환한다."""
    categories = []
    for arg in args:
        if ":" not in arg:
            raise SystemExit(f"잘못된 형식입니다: {arg} (예: '패션의류:50000000')")
        name, _, param = arg.partition(":")
        categories.append({
            "name": name.strip(),
            "param": [p.strip() for p in param.split(",") if p.strip()],
        })
    return categories


def fetch_shopping_category_trend(client_id, client_secret, start_date, end_date,
                                   time_unit, categories, **filters) -> dict:
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": time_unit,
        "category": categories,
    }
    body.update({k: v for k, v in filters.items() if v})
    return post_json(API_URL, client_id, client_secret, body)


def main():
    client_id, client_secret = load_credentials()

    args = sys.argv[1:]
    categories = parse_categories(args) if args else DEFAULT_CATEGORIES

    result = fetch_shopping_category_trend(
        client_id, client_secret,
        start_date="2026-01-01",
        end_date="2026-06-01",
        time_unit="month",
        categories=categories,
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
