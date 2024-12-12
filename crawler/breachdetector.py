from telethon import TelegramClient
import json
import os
from jsonschema import validate, ValidationError

# 해당 크롤러는 환경 변수에서 API 정보를 가져옵니다.
# 환경 변수 설정 방법:
# Windows: 
#   set TELEGRAM_API_ID=<Your API ID>
#   set TELEGRAM_API_HASH=<Your API Hash>
#
# Linux/macOS: 
#   export TELEGRAM_API_ID=<Your API ID>
#   export TELEGRAM_API_HASH=<Your API Hash>

# 1. 텔레그램 정보
api_id = os.getenv("TELEGRAM_API_ID")  # TELEGRAM_API_ID 환경 변수에서 가져오기
api_hash = os.getenv("TELEGRAM_API_HASH")  # TELEGRAM_API_HASH 환경 변수에서 가져오기
channel_username = "breachdetector"  # 채널 이름

if not api_id or not api_hash:
    raise EnvironmentError(
        "API ID 또는 API Hash가 설정되지 않았습니다. "
        "환경 변수 TELEGRAM_API_ID와 TELEGRAM_API_HASH를 설정해주세요."
    )

# 2. JSON Schema 정의
schema = {
    "type": "object",
    "properties": {
        "content": {"type": "string"},
        "date": {"type": "string", "format": "date-time"},
        "sender_id": {"type": ["string", "number"]}
    },
    "required": ["content", "date", "sender_id"]
}

# 3. Telegram Client 초기화
client = TelegramClient("session_name", api_id, api_hash)

async def fetch_messages():
    await client.start()  # 클라이언트 시작
    messages = await client.get_messages(channel_username, limit=100)  # 메시지 가져오기

    data = []  # 데이터를 저장할 리스트

    for message in messages:
        try:
            text = message.text
            if text:
                # JSON 형식으로 저장
                entry = {
                    "content": text,
                    "date": str(message.date),  # 메시지 작성 시간
                    "sender_id": message.sender_id  # 작성자 ID
                }

                # JSON Schema 검증
                try:
                    validate(instance=entry, schema=schema)
                    data.append(entry)
                    print(f"메시지 저장 완료: {entry}")
                except ValidationError as e:
                    print(f"데이터 검증 실패: {e.message}")

        except Exception as e:
            print(f"오류 발생: {e}")

    # JSON 파일로 저장 (주석 처리)
    # with open('breachdetector.json', 'w', encoding='utf-8') as f:
    #     json.dump(data, f, ensure_ascii=False, indent=4)
    # print("데이터 저장 완료: breachdetector.json")

    return data

# 비동기 함수 실행
def crawl_breachdetector():
    with client:
        return client.loop.run_until_complete(fetch_messages())

if __name__ == "__main__":
    result = crawl_breachdetector()
    print(result)
