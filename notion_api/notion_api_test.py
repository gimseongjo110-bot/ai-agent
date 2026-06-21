#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Notion API 접근 테스트: 토큰 유효성 확인 및 접근 가능한 페이지/데이터베이스 조회."""

import json

from common import load_api_key, request_json


def main():
    api_key = load_api_key()

    print("=== 1. 토큰 유효성 확인 (GET /v1/users/me) ===")
    me = request_json("/users/me", api_key)
    print(json.dumps(me, ensure_ascii=False, indent=2))

    print("\n=== 2. 접근 가능한 페이지/데이터베이스 조회 (POST /v1/search) ===")
    search_result = request_json(
        "/search",
        api_key,
        method="POST",
        body={"page_size": 10},
    )
    results = search_result.get("results", [])
    print(f"접근 가능한 객체 수: {len(results)}")
    for item in results:
        obj_type = item.get("object")
        item_id = item.get("id")
        title = None
        if obj_type == "page":
            props = item.get("properties", {})
            for prop in props.values():
                if prop.get("type") == "title":
                    title_parts = prop.get("title", [])
                    title = "".join(t.get("plain_text", "") for t in title_parts)
                    break
        elif obj_type == "database":
            title_parts = item.get("title", [])
            title = "".join(t.get("plain_text", "") for t in title_parts)
        print(f"- [{obj_type}] {item_id}: {title or '(제목 없음)'}")


if __name__ == "__main__":
    main()
