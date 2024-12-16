import json
import requests
from jsonschema import validate, ValidationError
from datetime import datetime

# JSON 데이터 URL 목록 및 카테고리 이름
json_sources = [
    {"url": "https://ctifeeds.andreafortuna.org/dataleaks.json", "categories": "dataleaks"},
    {"url": "https://ctifeeds.andreafortuna.org/cybercrime_on_telegram.json", "categories": "cybercrime_on_telegram"},
    {"url": "https://ctifeeds.andreafortuna.org/phishing_sites.json", "categories": "phishing_sites"},
    {"url": "https://ctifeeds.andreafortuna.org/datamarkets.json", "categories": "datamarkets"},
    {"url": "https://ctifeeds.andreafortuna.org/ransomware_victims.json", "categories": "ransomware_victims"},
    {"url": "https://ctifeeds.andreafortuna.org/recent_defacements.json", "categories": "recent_defacements"},
]

# JSON Schema 정의
schema = {
    "type": "object",
    "properties": {
        "categories": {"type": "string"},
        "title": {"type": "string"},
        "url": {"type": "string"},
        "source": {"type": "string"},
        "screenshot": {"type": ["string", "null"]},
        "urlscan": {"type": ["string", "null"]}
    },
    "required": ["categories", "title", "url", "source"]
}

def run(db):
    """
    ctifeeds 크롤러 실행 및 MongoDB 컬렉션에 데이터 저장
    """
    collection = db["ctifeeds"]  # MongoDB 컬렉션 선택

    for source in json_sources:
        try:
            # JSON 데이터 가져오기
            response = requests.get(source["url"], timeout=10)
            response.raise_for_status()
            data = response.json()

            # 카테고리 항목 추가 및 데이터 처리
            for item in data:
                item["categories"] = source["categories"]
                item["Crawled Time"] = str(datetime.now())  # 크롤링 시간 추가

                # JSON Schema 검증
                try:
                    validate(instance=item, schema=schema)

                    # 중복 데이터 확인 및 저장
                    if not collection.find_one({"categories": item["categories"], "title": item["title"]}):
                        collection.insert_one(item)
                        print(f"Saved: {item['title']} in category {item['categories']}")
                    else:
                        print(f"Skipped (duplicate): {item['title']} in category {item['categories']}")

                except ValidationError as e:
                    print(f"데이터 검증 실패 ({source['categories']}): {e.message}")

            print(f"데이터 수집 완료: {source['categories']}")

        except Exception as e:
            print(f"데이터 수집 중 오류 발생 ({source['categories']}): {e}")