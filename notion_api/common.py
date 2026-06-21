#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Notion API 공통 유틸리티 (인증 토큰 로드, JSON 요청)."""

import json
import os
import urllib.error
import urllib.request

_ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
NOTION_VERSION = "2022-06-28"
BASE_URL = "https://api.notion.com/v1"


def load_api_key():
    """환경변수 또는 notion_api/.env 파일에서 Notion API 키를 읽는다."""
    api_key = os.environ.get("NOTION_API_KEY")

    if not api_key and os.path.exists(_ENV_PATH):
        with open(_ENV_PATH, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key, value = key.strip(), value.strip().strip('"').strip("'")
                if key == "NOTION_API_KEY" and not api_key:
                    api_key = value

    if not api_key:
        raise SystemExit(
            "NOTION_API_KEY 값을 찾을 수 없습니다. "
            "환경변수로 설정하거나 notion_api/.env 파일에 작성하세요."
        )
    return api_key


def request_json(path: str, api_key: str, method: str = "GET", body: dict | None = None) -> dict:
    """Notion API에 요청을 보내고 응답을 dict로 반환한다."""
    url = f"{BASE_URL}{path}"
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    request = urllib.request.Request(url, data=data, method=method)
    request.add_header("Authorization", f"Bearer {api_key}")
    request.add_header("Notion-Version", NOTION_VERSION)
    request.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise SystemExit(f"API 요청 실패 ({e.code}): {error_body}")
