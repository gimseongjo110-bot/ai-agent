#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Typecast TTS API 공통 유틸리티 (자격증명 로드, 음성 합성 요청)."""

import json
import os
import urllib.error
import urllib.request

_ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
API_URL = "https://api.typecast.ai/v1/text-to-speech"


def load_credentials():
    """환경변수 또는 typecast_api/.env 파일에서 API 키/기본 보이스 ID를 읽는다."""
    api_key = os.environ.get("TYPECAST_API_KEY")
    voice_id = os.environ.get("TYPECAST_VOICE_ID")

    if (not api_key or not voice_id) and os.path.exists(_ENV_PATH):
        with open(_ENV_PATH, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key, value = key.strip(), value.strip().strip('"').strip("'")
                if key == "TYPECAST_API_KEY" and not api_key:
                    api_key = value
                elif key == "TYPECAST_VOICE_ID" and not voice_id:
                    voice_id = value

    if not api_key:
        raise SystemExit(
            "TYPECAST_API_KEY 값을 찾을 수 없습니다. "
            "환경변수로 설정하거나 typecast_api/.env 파일에 작성하세요."
        )
    return api_key, voice_id


def synthesize_speech(api_key: str, voice_id: str, text: str, model: str = "ssfm-v30",
                       language: str | None = None, output_format: str = "wav",
                       **extra) -> bytes:
    """Typecast TTS API를 호출해 합성된 오디오 바이너리를 반환한다."""
    body = {
        "voice_id": voice_id,
        "text": text,
        "model": model,
    }
    if language:
        body["language"] = language
    if output_format:
        body["output"] = {"audio_format": output_format}
    body.update(extra)

    request = urllib.request.Request(
        API_URL,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        method="POST",
    )
    request.add_header("X-API-KEY", api_key)
    request.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(request) as response:
            return response.read()
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise SystemExit(f"API 요청 실패 ({e.code}): {error_body}")
