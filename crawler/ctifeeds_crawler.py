import json
import os
import requests
from jsonschema import validate, ValidationError

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
        "urlscan": {"type": ["string", "null"]}
    },
    "required": ["categories", "name", "url", "source"]
}

# 데이터 저장용 리스트
all_data = []

def fetch_json_data():
    for source in json_sources:
        try:
            response = requests.get(source["url"], timeout=10)
            response.raise_for_status()
            
            # JSON 데이터를 로드
            data = response.json()

            # 카테고리 항목 추가 및 데이터 처리
            for item in data:
                item["categories"] = source["categories"]

                # JSON Schema 검증
                try:
                    validate(instance=item, schema=schema)
                    all_data.append(item)
                except ValidationError as e:
                    print(f"데이터 검증 실패 ({source['categories']}): {e.message}")

            print(f"데이터 수집 완료: {source['categories']}")
        except Exception as e:
            print(f"데이터 수집 중 오류 발생 ({source['categories']}): {e}")

    # 결과 데이터를 JSON 파일로 저장 (주석 처리)
    # with open("ctifeeds_data.json", "w", encoding="utf-8") as f:
    #     json.dump(all_data, f, ensure_ascii=False, indent=4)
    # print("ctifeeds_data.json 파일 저장 완료.")

    return all_data

if __name__ == "__main__":
    result = fetch_json_data()
    print(result)
