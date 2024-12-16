import os
import smtplib
from email.mime.text import MIMEText
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

# 이메일 정보 설정
EMAIL_SENDER = "tastyTiramisu110@gmail.com"
EMAIL_PASSWORD = "duca bjnc ynsf mmup"

# MongoDB 연결 설정
MONGO_URI = "mongodb://mongo1:30001,mongo2:30002,mongo3:30003/?replicaSet=my-rs"
DB_NAME = "example_collection"
COLLECTION_NAME = "example_collection"

# 이메일 전송 함수
def send_email(subject, body):
    try:
        msg = MIMEText(body, "plain")
        msg["Subject"] = subject
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_SENDER

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_SENDER, msg.as_string())
        print("[INFO] 이메일 전송 성공!")
    except Exception as e:
        print(f"[ERROR] 이메일 전송 실패: {e}")

# MongoDB 변경 사항 감지 및 알림 발신
def watch_collection():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        print(f"[INFO] {COLLECTION_NAME} 컬렉션 변경 사항 모니터링 시작...")
        changed_titles = []  # 변경된 title 저장 리스트

        with collection.watch() as stream:
            for change in stream:
                print("[INFO] 변경 사항 발생:", change)
                operation_type = change["operationType"]

                # insert, update, replace 이벤트에 대해 title만 수집
                if operation_type in ["insert", "update", "replace"]:
                    document_key = change["documentKey"]["_id"]
                    updated_document = collection.find_one({"_id": document_key})

                    # title이 존재하는 경우만 수집
                    if updated_document and "title" in updated_document:
                        changed_titles.append(updated_document["title"])

                # 변경 사항이 여러 개라면, 누적된 title 리스트로 알림 발송
                if changed_titles:
                    subject = f"[MongoDB 알림] {COLLECTION_NAME} 컬렉션 변경 사항"
                    body = "다음 데이터가 변경되었습니다:\n" + "\n".join(changed_titles)
                    send_email(subject, body)
                    changed_titles.clear()  # 알림 발송 후 리스트 초기화
    except ServerSelectionTimeoutError as e:
        print(f"[ERROR] MongoDB 연결 실패: {e}")
    except Exception as e:
        print(f"[ERROR] Change Stream 모니터링 중 오류 발생: {e}")

if __name__ == "__main__":
    watch_collection()
