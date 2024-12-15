import os
import smtplib
from email.mime.text import MIMEText
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from pymongo.change_stream import ChangeStream

# MongoDB 연결 설정
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")  # MongoDB URI (환경변수 기본값 사용)
DB_NAME = os.environ.get("DB_NAME", "darkweb_db")  # DB 이름
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "example_collection")  # Collection 이름

# 환경변수로 이메일 정보 가져오기
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")  # 보내는 이메일
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")  # 이메일 비밀번호 (앱 비밀번호 사용 권장)
EMAIL_RECIPIENT = os.environ.get("EMAIL_RECIPIENT")  # 받는 이메일

# MongoDB 연결
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    print(f"MongoDB 연결 성공: {MONGO_URI}")
except ServerSelectionTimeoutError as e:
    print(f"MongoDB 연결 실패: {e}")
    exit(1)

# 이메일 보내기 함수
def send_email(subject, body):
    try:
        msg = MIMEText(body, "plain")
        msg["Subject"] = subject
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECIPIENT

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, msg.as_string())
        print("이메일 전송 성공!")
    except Exception as e:
        print(f"이메일 전송 실패: {e}")

# Change Streams로 업데이트 확인
def watch_collection():
    try:
        with collection.watch() as stream:  # Change Streams 활성화
            print("컬렉션 변경 사항 모니터링 시작...")
            for change in stream:
                print("변경 사항 발생:", change)
                operation_type = change["operationType"]

                # 업데이트가 발생한 경우 이메일 알림
                if operation_type in ["insert", "update", "replace"]:
                    document_key = change["documentKey"]["_id"]
                    updated_fields = change.get("updateDescription", {}).get("updatedFields", {})
                    subject = f"MongoDB 업데이트 알림: {operation_type}"
                    body = f"문서 ID: {document_key}\n변경된 필드: {updated_fields}"
                    send_email(subject, body)
    except Exception as e:
        print(f"Change Stream 모니터링 중 오류 발생: {e}")

if __name__ == "__main__":
    watch_collection()
