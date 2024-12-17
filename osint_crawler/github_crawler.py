import asyncio
import aiohttp
import json
from datetime import datetime, timedelta

GITHUB_TOKEN = ""
GITHUB_API_URL = 'https://api.github.com/search/repositories'
JSON_FILE_PATH = './osint_crawler/cleaned_keywords.json'
MIN_KEYWORDS_MATCH = 20
DAYS_AGO = 730

def filter_by_last_update(repositories, days_ago):
    threshold_date = datetime.utcnow() - timedelta(days=days_ago)
    return [
        repo for repo in repositories
        if datetime.strptime(repo['updated_at'], '%Y-%m-%dT%H:%M:%SZ') >= threshold_date
    ]

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
                return None
    except Exception as e:
        print(f"[ERROR] github_crawler.py - fetch_readme(): {e}")
        return None

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
                return []
    except Exception as e:
        print(f"[ERROR] github_crawler.py - serch_github(): {e}")
        return []

async def github(db, show=False):
    with open(JSON_FILE_PATH, 'r') as file:
        data = json.load(file)

    keywords = data.get('keywords', [])

    collection = db["github"]

    async with aiohttp.ClientSession() as session:
        for keyword in keywords:
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
                        }
                        if show:
                            print(f'github: {repo_info}')
                        existing = await collection.find_one({"repo_name": repo_info['repo_name']})
                        if not existing:
                            obj = await collection.insert_one(repo_info)
                            if show:
                                print('github insert success ' + str(obj.inserted_id))