#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Typecast TTS API 호출 스크립트

사용법:
    python tts.py                                   # 기본 문구로 테스트 합성
    python tts.py "합성할 텍스트"
    python tts.py "합성할 텍스트" output/result.wav
"""

import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from common import load_credentials, synthesize_speech

DEFAULT_TEXT = "안녕하세요 저는 김성조 입니다"
DEFAULT_OUTPUT = os.path.join(os.path.dirname(__file__), "output", "result.wav")


def main():
    args = sys.argv[1:]
    text = args[0] if len(args) >= 1 else DEFAULT_TEXT
    output_path = args[1] if len(args) >= 2 else DEFAULT_OUTPUT

    api_key, voice_id = load_credentials()
    if not voice_id:
        raise SystemExit("TYPECAST_VOICE_ID 값을 찾을 수 없습니다.")

    audio = synthesize_speech(
        api_key, voice_id, text,
        model="ssfm-v30",
        language="kor",
        output_format="wav",
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(audio)

    print(f"합성 완료: {output_path} ({len(audio):,} bytes)")


if __name__ == "__main__":
    main()
