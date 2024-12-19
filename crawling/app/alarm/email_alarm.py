import os
import smtplib
from email.mime.text import MIMEText
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError
import asyncio
from datetime import datetime, timedelta
from config import EMAIL_SENDER, EMAIL_PASSWORD

print(EMAIL_SENDER, EMAIL_PASSWORD)

# MongoDB 연결 설정
MONGO_URI = "mongodb://mongo1:30001,mongo2:30002,mongo3:30003/?replicaSet=my-rs"
DB_NAME = "example_collection"

# 이메일 전송 함수
async def send_email(subject, body):
    try:
        msg = MIMEText(body, "plain")
        msg["Subject"] = subject
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_SENDER

        # SMTP 클라이언트 생성 및 이메일 전송
        loop = asyncio.get_event_loop()

        def smtp_send():
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                server.sendmail(EMAIL_SENDER, EMAIL_SENDER, msg.as_string())

        # SMTP 전송을 비동기로 실행
        await loop.run_in_executor(None, smtp_send)
        print("[INFO] 이메일 전송 성공!")
    except Exception as e:
        print(f"[ERROR] 이메일 전송 실패: {e}")

# UTC 시간 및 한국 시간 변환 함수
def format_times_from_id(change_id):
    utc_time = change_id.generation_time
    kor_time = utc_time + timedelta(hours=9)  # UTC+9 시간대
    return utc_time, kor_time

# 변경 사항 모니터링 및 알림 발신
async def watch_database():
    try:
        client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]

        print("[INFO] 데이터베이스 변경 사항 모니터링 시작...")
        changed_docs = []

        async with client.watch() as stream:
            async for change in stream:
                print("[INFO] 변경 사항 발생:", change)
                operation_type = change["operationType"]

                # 변경 사항 처리
                if operation_type in ["insert", "update", "replace"]:
                    collection_name = change["ns"]["coll"]
                    document_key = change["documentKey"]["_id"]
                    updated_document = await db[collection_name].find_one({"_id": document_key})

                    # title이 존재하는 경우만 수집
                    if updated_document and "title" in updated_document:
                        utc_time, kor_time = format_times_from_id(document_key)
                        changed_docs.append(
                            f"- **제목**: {updated_document['title']}\n"
                            f"- **유출한 사이트**: {collection_name}\n"
                            f"- **UTC 시간**: {utc_time}\n"
                            f"- **한국 시간**: {kor_time}"
                        )

                # 변경 사항이 여러 개라면, 누적된 내용으로 이메일 발송
                if changed_docs:
                    subject = "[MongoDB 알림] 데이터베이스 변경 사항"
                    body = "\n\n".join(changed_docs)
                    await send_email(subject, body)
                    changed_docs.clear()  # 이메일 발송 후 리스트 초기화
    except ServerSelectionTimeoutError as e:
        print(f"[ERROR] MongoDB 연결 실패: {e}")
    except Exception as e:
        print(f"[ERROR] Change Stream 모니터링 중 오류 발생: {e}")

# 메인 함수
async def main():
    await watch_database()

if __name__ == "__main__":
    asyncio.run(main())
