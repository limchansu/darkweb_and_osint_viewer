import requests
import json
from datetime import datetime, timedelta

# 해당 크롤러는 환경 변수에서 API 정보를 가져옵니다.
# 환경 변수 설정 방법:
# Windows: 
#   set GITHUB_TOKEN=<Your API ID>

GITHUB_TOKEN = ""   # GitHub API 토큰
GITHUB_API_URL = 'https://api.github.com/search/repositories'   # GitHub Repository 검색 API의 기본 URL
JSON_FILE_PATH = './cleaned_keywords.json'
MIN_KEYWORDS_MATCH = 20  # 최소 10개 키워드 포함
DAYS_AGO = 730  # 마지막 수정 기준 날짜

# 리포지토리를 날짜 기준으로 필터링하는 함수(최소 2년 정도로)
def filter_by_last_update(repositories, days_ago):
    threshold_date = datetime.utcnow() - timedelta(days=days_ago)
    filtered_repos = [
        repo for repo in repositories
        if datetime.strptime(repo['updated_at'], '%Y-%m-%dT%H:%M:%SZ') >= threshold_date
    ]
    return filtered_repos


# GitHub에서 README 내용을 가져오는 함수
def fetch_readme(repo_full_name):
    url = f"https://api.github.com/repos/{repo_full_name}/readme"
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3.raw'  # Raw 형태로 README 내용 가져오기
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text  # README 내용을 텍스트로 반환
    except requests.exceptions.RequestException as e:
        print(f"Error fetching README for {repo_full_name}: {e}")
        return None
    

def search_github(keyword):
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
    }

    params = {
        'q': keyword,
        'sort': 'stars',
        'order': 'desc',
        'per_page': 10  # 상위 N개 결과
    }
    
    try:
        response = requests.get(GITHUB_API_URL, headers=headers, params=params)
        response.raise_for_status()  # HTTP 오류가 발생하면 예외 발생
        return response.json()['items']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for keyword '{keyword}': {e}")
        return []


def run(db):
    with open(JSON_FILE_PATH, 'r') as file:
        data = json.load(file)

    keywords = data.get('keywords', [])    
    print("Searching GitHub for repositories matching keywords...")

    # DB 접근 객체
    collection = db["github"]

    for keyword in keywords:
        print(f"\nKeyword: {keyword}")

        # 각 키워드에 대한 repository들을 얻어오기
        repositories = search_github(keyword)

        for repo in repositories:
            readme_content = fetch_readme(repo['full_name'])
            
            if readme_content:
                # 키워드 포함 개수 계산
                match_count = sum(kw.lower() in readme_content.lower() for kw in keywords)
                
                if match_count >= MIN_KEYWORDS_MATCH:
                    repo_info = {
                        'repo_name': repo['full_name'],
                        'url': repo['html_url'],
                        'description': ((repo['description'])[:100] + '...') if repo['description'] and len(repo['description']) > 100 else (repo['description'] or 'No description available.')
                    }

                    # 중복 확인
                    if not collection.find_one({"repo_name": repo_info['repo_name']}):
                        print(f"\nRepository: {repo['full_name']}")
                        print(f"URL: {repo['html_url']}")
                        print(f"Description: {repo['description']}\n")

                        result = collection.insert_one(repo_info)
                        print("Inserted ID : ", result.inserted_id, "\n")
                    else:
                        print(f"Duplicate found. Skipping: {repo['full_name']}")
            else:
                print(f"Could not fetch README for {repo['full_name']}.")

