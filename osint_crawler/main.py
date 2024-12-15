from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

def create_databases():
    try:
        # MongoDB 서버 연결 (연결 확인을 위해 timeout 설정 추가)
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)

        # 서버 연결 확인
        if client.server_info():  # 서버 정보 조회 (연결되지 않으면 예외 발생)
            print("MongoDB 서버 연결 성공!")

        # 첫 번째 데이터베이스 (darkweb)
        db1 = client['darkweb']
        print("darkweb 생성 완료!")

        collection_name1 = ["abyss", "blackbasta", "blacksuit", "breachdetector", "ctifeeds", "daixin", "darkleak", "darknetARMY",
                           "everest", "island", "leakbase", "lockbit", "play", "rhysida"]

        for dw in collection_name1:
            if dw not in db1.list_collection_names():
                db1.create_collection(dw)
                print(f"Collection {dw} 생성 완료")
            else:
                print(f"Collection {dw} 이미 존재합니다")

        print("darkweb 컬렉션 생성 완료!")


        # 두 번째 데이터베이스 (osint)
        db2 = client['osint']
        print("osint 생성 완료!")

        collection_name2 = ["0x00org", "github", "tuts4you"]

        for osint in collection_name2:
            if osint not in db2.list_collection_names():
                db2.create_collection(osint)
                print(f"Collection {osint} 생성 완료")
            else:
                print(f"Collection {osint} 이미 존재합니다")

        return db1, db2

    except ServerSelectionTimeoutError:
        print("MongoDB 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요!")

if __name__ == "__main__":
    dw_db, osint_db = create_databases()
