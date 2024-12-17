import asyncio
import aiohttp
import json
from datetime import datetime, timedelta

# 환경 변수 설정
GITHUB_TOKEN = ""  # GitHub API 토큰
GITHUB_API_URL = 'https://api.github.com/search/repositories'
JSON_FILE_PATH = './cleaned_keywords.json'
MIN_KEYWORDS_MATCH = 20
DAYS_AGO = 730  # 날짜 기준 필터링

# 날짜 기준으로 필터링하는 함수
def filter_by_last_update(repositories, days_ago):
    threshold_date = datetime.utcnow() - timedelta(days=days_ago)
    return [
        repo for repo in repositories
        if datetime.strptime(repo['updated_at'], '%Y-%m-%dT%H:%M:%SZ') >= threshold_date
    ]

# 비동기적으로 GitHub API에서 README 파일 가져오기
async def fetch_readme(session, repo_full_name):
    url = f"https://api.github.com/repos/{repo_full_name}/readme"
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3.raw'
    }
    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.text()
            else:
                print(f"[WARNING] Failed to fetch README for {repo_full_name} - {response.status}")
                return None
    except Exception as e:
        print(f"[ERROR] Error fetching README for {repo_full_name}: {e}")
        return None

# 비동기적으로 GitHub 검색
async def search_github(session, keyword):
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    params = {
        'q': keyword,
        'sort': 'stars',
        'order': 'desc',
        'per_page': 10
    }
    try:
        async with session.get(GITHUB_API_URL, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('items', [])
            else:
                print(f"[WARNING] Failed to fetch data for keyword '{keyword}' - {response.status}")
                return []
    except Exception as e:
        print(f"[ERROR] Error fetching data for keyword '{keyword}': {e}")
        return []

# 메인 크롤링 함수
async def github(db):
    with open(JSON_FILE_PATH, 'r') as file:
        data = json.load(file)

    keywords = data.get('keywords', [])
    print("[INFO] Searching GitHub for repositories matching keywords...")

    collection = db["github"]

    async with aiohttp.ClientSession() as session:
        for keyword in keywords:
            print(f"\n[INFO] Keyword: {keyword}")
            repositories = await search_github(session, keyword)
            repositories = filter_by_last_update(repositories, DAYS_AGO)

            for repo in repositories:
                readme_content = await fetch_readme(session, repo['full_name'])

                if readme_content:
                    match_count = sum(kw.lower() in readme_content.lower() for kw in keywords)

                    if match_count >= MIN_KEYWORDS_MATCH:
                        repo_info = {
                            'repo_name': repo['full_name'],
                            'url': repo['html_url'],
                            'description': (repo['description'] or 'No description available.')[:100],
                            'crawled_time': str(datetime.utcnow())
                        }

                        # 중복 확인 및 데이터 저장
                        existing = await collection.find_one({"repo_name": repo_info['repo_name']})
                        if not existing:
                            await collection.insert_one(repo_info)
                            print(f"Saved: {repo['full_name']}")
                        else:
                            print(f"Skipped (duplicate): {repo['full_name']}")
                else:
                    print(f"Could not fetch README for {repo['full_name']}.")