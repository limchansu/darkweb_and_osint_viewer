import asyncio
import aiohttp
from pymongo import MongoClient
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
        "name": {"type": "string"},
        "url": {"type": "string"},
        "source": {"type": "string"},
        "screenshot": {"type": ["string", "null"]},
        "urlscan": {"type": ["string", "null"]},
    },
    "required": ["categories", "name", "url", "source"],
}

async def fetch_json(session, source):
    """
    비동기적으로 JSON 데이터를 가져오는 함수
    """
    try:
        async with session.get(source["url"], timeout=10) as response:
            response.raise_for_status()
            data = await response.json()
            print(f"[INFO] 데이터 가져오기 성공: {source['categories']}")
            return source["categories"], data
    except Exception as e:
        print(f"[ERROR] 데이터 수집 중 오류 발생 ({source['categories']}): {e}")
        return source["categories"], None

async def process_data(db, source, data):
    """
    MongoDB에 데이터를 저장하는 함수
    """
    collection = db["ctifeeds"]
    for item in data:
        item["categories"] = source
        item["Crawled Time"] = str(datetime.now())  # 크롤링 시간 추가

        # JSON Schema 검증 및 저장
        try:
            validate(instance=item, schema=schema)
            if not collection.find_one({"categories": item["categories"], "name": item["name"]}):
                collection.insert_one(item)
                print(f"Saved: {item['name']} in category {item['categories']}")
            else:
                print(f"Skipped (duplicate): {item['name']} in category {item['categories']}")
        except ValidationError as e:
            print(f"[ERROR] 데이터 검증 실패 ({item['categories']}): {e.message}")
        except Exception as e:
            print(f"[ERROR] 데이터 저장 중 오류 발생: {e}")

async def ctifeeds(db):
    """
    ctifeeds 크롤러 실행 및 MongoDB 컬렉션에 비동기적으로 데이터 저장
    """
    print("[INFO] ctifeeds 크롤러 실행 시작...")
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_json(session, source) for source in json_sources]
        results = await asyncio.gather(*tasks)

        for source, data in results:
            if data:
                await process_data(db, source, data)

    print("[INFO] ctifeeds 크롤러 실행 완료")

if __name__ == "__main__":
    # MongoDB 연결 설정
    mongo_client = MongoClient("mongodb://localhost:27017/")
    db = mongo_client["your_database_name"]

    # 비동기 실행
    asyncio.run(ctifeeds(db))
