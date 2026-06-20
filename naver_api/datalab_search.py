#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 데이터랩 통합검색어 트렌드 API 호출 스크립트

사용법:
    python datalab_search.py                            # 기본 예시(한글 vs 영어) 조회
    python datalab_search.py "한글:한글,korean" "영어:영어,english"
"""

import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import json

from common import load_credentials, post_json

API_URL = "https://openapi.naver.com/v1/datalab/search"

DEFAULT_KEYWORD_GROUPS = [
    {"groupName": "한글", "keywords": ["한글", "korean"]},
    {"groupName": "영어", "keywords": ["영어", "english"]},
]


def parse_keyword_groups(args: list) -> list:
    """'그룹명:키워드1,키워드2' 형식의 인자를 keywordGroups 배열로 변환한다."""
    groups = []
    for arg in args:
        if ":" not in arg:
            raise SystemExit(f"잘못된 형식입니다: {arg} (예: '한글:한글,korean')")
        name, _, keywords = arg.partition(":")
        groups.append({
            "groupName": name.strip(),
            "keywords": [k.strip() for k in keywords.split(",") if k.strip()],
        })
    return groups


def fetch_search_trend(client_id, client_secret, start_date, end_date, time_unit,
                        keyword_groups, **filters) -> dict:
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": time_unit,
        "keywordGroups": keyword_groups,
    }
    body.update({k: v for k, v in filters.items() if v})
    return post_json(API_URL, client_id, client_secret, body)


def main():
    client_id, client_secret = load_credentials()

    args = sys.argv[1:]
    keyword_groups = parse_keyword_groups(args) if args else DEFAULT_KEYWORD_GROUPS

    result = fetch_search_trend(
        client_id, client_secret,
        start_date="2026-01-01",
        end_date="2026-06-01",
        time_unit="month",
        keyword_groups=keyword_groups,
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
