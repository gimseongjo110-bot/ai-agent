#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""네이버 오픈API 공통 유틸리티 (클라이언트 인증, JSON POST 요청)."""

import json
import os
import urllib.error
import urllib.request

_ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")


def load_credentials():
    """환경변수 또는 naver_api/.env 파일에서 클라이언트 아이디/시크릿을 읽는다."""
    client_id = os.environ.get("NAVER_CLIENT_ID")
    client_secret = os.environ.get("NAVER_CLIENT_SECRET")

    if (not client_id or not client_secret) and os.path.exists(_ENV_PATH):
        with open(_ENV_PATH, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key, value = key.strip(), value.strip().strip('"').strip("'")
                if key == "NAVER_CLIENT_ID" and not client_id:
                    client_id = value
                elif key == "NAVER_CLIENT_SECRET" and not client_secret:
                    client_secret = value

    if not client_id or not client_secret:
        raise SystemExit(
            "NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 값을 찾을 수 없습니다. "
            "환경변수로 설정하거나 naver_api/.env 파일에 작성하세요."
        )
    return client_id, client_secret


def post_json(url: str, client_id: str, client_secret: str, body: dict) -> dict:
    """네이버 오픈API에 JSON POST 요청을 보내고 응답을 dict로 반환한다."""
    request = urllib.request.Request(
        url,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        method="POST",
    )
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    request.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise SystemExit(f"API 요청 실패 ({e.code}): {error_body}")
