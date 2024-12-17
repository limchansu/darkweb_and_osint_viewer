import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dw_crawler.htdark_crawler import htdark
from dw_crawler.island_crawler import island
from dw_crawler.leakbase_crawler import leakbase
from dw_crawler.lockbit_crawler import lockbit
from dw_crawler.play_crawler import play
from dw_crawler.rhysida_crawler import rhysida
from osint_crawler.github_crawler import github

async def setup_database(db_name, collection_names):
    """
    MongoDB 데이터베이스 및 컬렉션 생성
    """
    print(f"[INFO] MongoDB 설정 시작: {db_name}")
    client = AsyncIOMotorClient("mongodb://mongo1:30001,mongo2:30002,mongo:30003/?replicaSet=my-rs")
    db = client[db_name]

    # 비동기 메서드에 await 사용
    existing_collections = await db.list_collection_names()
    for collection in collection_names:
        if collection not in existing_collections:
            await db.create_collection(collection)
            print(f"[INFO] {collection} 컬렉션 생성 완료! ({db_name})")

    print(f"[INFO] MongoDB 설정 완료: {db_name}")
    return db

async def exec_crawler():
    db_name = 'darkweb'
    collection_name = ['htdark', 'island', 'leakbase', 'lockbit', 'play', 'rhysida', 'github']
    db = await setup_database(db_name, collection_name)
    # 비동기 함수들을 동시에 실행
    await asyncio.gather(
        htdark(db),
        island(db),
        leakbase(db),
        lockbit(db),
        play(db),
        rhysida(db),
        github(db)
    )
    print("[INFO] 모든 크롤러 실행 완료!")

asyncio.run(exec_crawler())
