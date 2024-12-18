import os
import smtplib
import logging
from email.mime.text import MIMEText
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError
import asyncio
from datetime import datetime, timedelta
from bson import ObjectId

# 직접 설정하는 configuration
EMAIL_SENDER = "tastyTiramisu110@gmail.com"  # 발신자 이메일
EMAIL_PASSWORD = "duca bjnc ynsf mmup"       #"vgeb jnij gntt dubr"  # 이메일 비밀번호 
MONGO_URI = "mongodb://localhost:27017/"  # MongoDB 연결 주소
DB_NAME = "darkweb"  # 데이터베이스 이름
POLLING_INTERVAL = 10  # 10초마다 확인 (테스트를 위해 간격 줄임)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mongodb_watch.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DatabaseWatcher:
    def __init__(self):
        self.client = None
        self.db = None
        self.last_check_time = datetime.utcnow()

    async def connect_to_mongodb(self):
        """MongoDB에 연결하는 함수"""
        try:
            if not self.client:
                self.client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
                self.db = self.client[DB_NAME]
            await self.client.admin.command('ping')
            return self.client
        except Exception as e:
            logger.error(f"MongoDB 연결 실패: {e}")
            raise

    async def send_email(self, subject, body):
        """이메일 전송 함수"""
        try:
            msg = MIMEText(body, "plain")
            msg["Subject"] = subject
            msg["From"] = EMAIL_SENDER
            msg["To"] = EMAIL_SENDER

            loop = asyncio.get_event_loop()

            def smtp_send():
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                    server.sendmail(EMAIL_SENDER, EMAIL_SENDER, msg.as_string())

            await loop.run_in_executor(None, smtp_send)
            logger.info("이메일 전송 성공")
        except Exception as e:
            logger.error(f"이메일 전송 실패: {e}")
            raise

    async def check_new_documents(self):
        """새로운 문서 확인"""
        try:
            collections = await self.db.list_collection_names()
            changed_docs = []
            current_time = datetime.utcnow()
            
            # 현재 시간 기준으로 ObjectId 생성
            last_check_id = ObjectId.from_datetime(self.last_check_time)
            
            for collection in collections:
                # 컬렉션별 문서 수 로깅
                count = await self.db[collection].count_documents({})
                logger.info(f"컬렉션 {collection}의 총 문서 수: {count}")
                
                # ObjectId 기준으로 쿼리
                query = {
                    "_id": {
                        "$gt": last_check_id
                    }
                }
                
                cursor = self.db[collection].find(query)
                async for doc in cursor:
                    if "title" in doc:
                        # 발견된 문서 로깅
                        logger.info(f"새 문서 발견: collection={collection}, id={doc['_id']}, title={doc['title']}")
                        
                        kor_time = doc["_id"].generation_time + timedelta(hours=9)
                        changed_docs.append(
                            f"- **제목**: {doc['title']}\n"
                            f"- **유출한 사이트**: {collection}\n"
                            f"- **UTC 시간**: {doc['_id'].generation_time}\n"
                            f"- **한국 시간**: {kor_time}"
                        )

            if changed_docs:
                logger.info(f"새로운 문서 {len(changed_docs)}개 발견")
                subject = f"[MongoDB 알림] 새로운 데이터 {len(changed_docs)}개 발견"
                body = "\n\n".join(changed_docs)
                await self.send_email(subject, body)
            
            self.last_check_time = current_time
            logger.debug(f"마지막 확인 시간 업데이트: {self.last_check_time}")

        except Exception as e:
            logger.error(f"문서 확인 중 오류 발생: {e}")
            import traceback
            logger.error(traceback.format_exc())

    async def watch_database(self):
        """데이터베이스 모니터링 메인 로직"""
        while True:
            try:
                await self.connect_to_mongodb()
                logger.info(f"데이터베이스 확인 중... (간격: {POLLING_INTERVAL}초)")
                await self.check_new_documents()
                await asyncio.sleep(POLLING_INTERVAL)

            except Exception as e:
                logger.error(f"모니터링 중 오류 발생: {e}")
                await asyncio.sleep(5)  # 오류 발생 시 5초 대기 후 재시도
            finally:
                if self.client:
                    self.client.close()
                    self.client = None

async def main():
    watcher = DatabaseWatcher()
    await watcher.watch_database()

if __name__ == "__main__":
    asyncio.run(main())
