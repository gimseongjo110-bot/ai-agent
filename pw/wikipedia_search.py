#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wikipedia 자동 검색 스크립트 (Playwright 기반)

사용법:
    python wikipedia_search.py              # 기본 검색어(머신러닝) 사용
    python wikipedia_search.py 인공지능     # 검색어 직접 지정
"""

import sys
import io

# Windows 콘솔 UTF-8 출력 강제 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright


def get_article_url(query: str) -> str:
    """Wikipedia OpenSearch API로 첫 번째 문서 URL을 조회한다."""
    import urllib.parse, urllib.request, json

    encoded = urllib.parse.quote(query)
    api_url = (
        f"https://ko.wikipedia.org/w/api.php"
        f"?action=opensearch&search={encoded}&limit=1&namespace=0&format=json"
    )
    req = urllib.request.Request(
        api_url,
        headers={"User-Agent": "WikipediaSearchBot/1.0 (educational)"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    # data 형식: [query, [titles], [descriptions], [urls]]
    urls = data[3] if len(data) > 3 else []
    return urls[0] if urls else ""


def search_wikipedia(query: str) -> dict:
    result = {
        "query": query,
        "title": "",
        "url": "",
        "summary": "",
        "sections": [],
    }

    UA = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=UA,
            viewport={"width": 1280, "height": 900},
        )
        page = context.new_page()

        # 1. OpenSearch API로 문서 URL 조회
        print("  [1/4] Wikipedia API로 문서 URL 조회 중...")
        article_url = get_article_url(query)
        if not article_url:
            raise ValueError(f"'{query}'에 대한 위키백과 문서를 찾을 수 없습니다.")

        # 2. 검색어 확인
        print(f"  [2/4] 검색어: '{query}' → {article_url}")

        # 3. 문서 URL로 직접 네비게이션 (networkidle로 Parsoid 렌더링 완료 대기)
        print("  [3/4] 문서 페이지 로드 중...")
        page.goto(article_url, wait_until="networkidle")
        page.wait_for_selector("#mw-content-text p:not(.mw-empty-elt)", timeout=15000)
        page.wait_for_timeout(500)

        result["url"] = page.url
        result["title"] = page.title()

        # 4. 본문 추출
        print("  [4/4] 본문 콘텐츠 추출 중...")

        # JavaScript로 본문 단락 추출 (비어있는 단락 / 짧은 공지 제외)
        intro_parts = page.evaluate("""
            () => {
                const content = document.querySelector('#mw-content-text');
                if (!content) return [];
                const results = [];
                const allP = content.querySelectorAll('p:not(.mw-empty-elt)');
                for (const p of allP) {
                    const text = p.innerText.trim();
                    if (text.length < 60) continue;
                    results.push(text);
                    if (results.length >= 3) break;
                }
                return results;
            }
        """)
        result["summary"] = "\n\n".join(intro_parts)

        # 목차 섹션 제목 (최대 8개)
        sections = page.evaluate("""
            () => {
                const hs = document.querySelectorAll('#mw-content-text h2');
                const result = [];
                for (const h of hs) {
                    const span = h.querySelector('.mw-headline');
                    const t = span ? span.innerText.trim() : h.innerText.trim();
                    if (t && t.length > 1) result.push(t);
                    if (result.length >= 8) break;
                }
                return result;
            }
        """)
        result["sections"] = sections

        browser.close()

    return result


def print_result(result: dict) -> None:
    bar = "=" * 62
    thin = "-" * 62

    print(f"\n{bar}")
    print(f"  검색 결과")
    print(bar)
    print(f"  검색어 : {result['query']}")
    print(f"  제목   : {result['title']}")
    print(f"  URL    : {result['url']}")

    print(f"\n  [ 요약 ]")
    print(thin)
    for line in result["summary"].splitlines():
        line = line.strip()
        if line:
            # 긴 줄 줄바꿈 처리 (80자 기준)
            while len(line) > 78:
                print(f"  {line[:78]}")
                line = line[78:]
            print(f"  {line}")

    if result["sections"]:
        print(f"\n  [ 주요 목차 ]")
        print(thin)
        for i, section in enumerate(result["sections"], 1):
            print(f"  {i:2}. {section}")

    print(f"{bar}\n")


def main():
    query = sys.argv[1] if len(sys.argv) > 1 else "머신러닝"

    print(f"\n{'='*62}")
    print(f"  Wikipedia 자동 검색 스크립트  |  Playwright 기반")
    print(f"{'='*62}")
    print(f"  검색어: {query}\n")

    try:
        result = search_wikipedia(query)
        print_result(result)
    except Exception as e:
        print(f"\n  [오류] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
