import asyncio
import aiohttp
from pymongo import MongoClient
from jsonschema import validate, ValidationError
from datetime import datetime

# JSON 데이터 URL 목록 및 카테고리 이름
json_sources = [
    {"url": "https://ctifeeds.andreafortuna.org/dataleaks.json", "categories": "dataleaks"},
    {"url": "https://ctifeeds.andreafortuna.org/cybercrime_on_telegram.json", "categories": "cybercrime_on_telegram"},
    {"url": "https://ctifeeds.andreafortuna.org/datamarkets.json", "categories": "datamarkets"},
    {"url": "https://ctifeeds.andreafortuna.org/ransomware_victims.json", "categories": "ransomware_victims"},
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
        "urlscan": {"type": ["string", "null"]},
    },
    "required": ["categories", "title", "url", "source"],
}

async def fetch_json(session, source):
    """
    비동기적으로 JSON 데이터를 가져오는 함수
    """
    try:
        async with session.get(source["url"], timeout=30) as response:
            response.raise_for_status()
            data = await response.json()
            return source["categories"], data
    except Exception as e:
        print(f"[ERROR] ctifeeds_crawler.py - fetch_json(): {e}")
        return source["categories"], None

async def process_data(db, source, data, show):
    """
    MongoDB에 데이터를 저장하는 함수
    """
    collection = db["ctifeeds"]
    for item in data:
        item["categories"] = source

        # 'name'을 'title'로 변경 (name 키가 없을 경우, None 대신 건너뛰기)
        name_value = item.pop("name", None)
        if not name_value:  # name이 없으면 다음 항목으로 넘어감
            print("[WARNING] Skipping item with missing 'name' field.")
            continue
        item["title"] = name_value

        # JSON Schema 검증 및 저장
        try:
            validate(instance=item, schema=schema)
            if show:
                print(f'ctifeeds: {item}')

            # 중복 확인
            existing_doc = await collection.find_one(
                {"categories": item["categories"], "title": item["title"]}
            )
            if not existing_doc:  # 문서가 존재하지 않으면 저장
                result = await collection.insert_one(item)
                if show and result.inserted_id:
                    print('ctifeeds insert success ' + str(result.inserted_id))

        except Exception as e:
            print(f"[ERROR] ctifeeds_crawler.py - process_data(): {e}")

async def ctifeeds(db, show=False):
    """
    ctifeeds 크롤러 실행 및 MongoDB 컬렉션에 비동기적으로 데이터 저장
    """
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_json(session, source) for source in json_sources]
        results = await asyncio.gather(*tasks)

        for source, data in results:
            if data:
                await process_data(db, source, data, show)

if __name__ == "__main__":
    # MongoDB 연결 설정
    mongo_client = MongoClient("mongodb://localhost:27017/")
    db = mongo_client["your_database_name"]

    # 비동기 실행
    asyncio.run(ctifeeds(db))
