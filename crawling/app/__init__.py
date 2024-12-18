from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import asyncio
import threading
import sys, os

# Flask 앱 초기화
app = Flask(__name__)
CORS(app)

# 경로 설정
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from main import setup_database, run_crawler_periodically

# 라우팅 핸들러들은 그대로 유지...
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
async def search():
    # 데이터베이스 생성 및 연결
    dw_collections = ["abyss", "blackbasta", "blacksuit", "breachdetector", "ctifeeds",
                      "daixin", "darkleak", "darknetARMY", "everest", "island",
                      "leakbase", "lockbit", "play", "rhysida", "htdark"]
    osint_collections = ["github", "tuts4you", "x00org"]

    dw_db, osint_db = await asyncio.gather(
        setup_database("darkweb", dw_collections),
        setup_database("osint", osint_collections)
    )

    # 요청 파라미터
    data = request.get_json()
    keywords = data.get('keywords', '').strip()
    category = data.get('category', '')
    option = data.get('option', '')

    # 초기화
    results = []

    if category == "all" and option == "all" and keywords == "":
        # 두 카테고리의 모든 컬렉션을 순회
        for collection_name in dw_collections + osint_collections:
            db_collection = dw_db[collection_name] if collection_name in dw_collections else osint_db[collection_name]
            cursor = db_collection.find().sort("_id", -1)  # _id 기준으로 내림차순 정렬 (최신순)
            async for doc in cursor:
                result = {key: (str(value) if key == "_id" else value) for key, value in doc.items()}
                results.append(result)
    else:
        # 카테고리 및 옵션에 따라 컬렉션 선택
        if category == "osint":
            if option not in osint_collections:
                return jsonify({"error": f"Invalid collection '{option}' in osint"}), 400
            db_collection = osint_db[option]
        elif category == "darkweb":
            if option not in dw_collections:
                return jsonify({"error": f"Invalid collection '{option}' in darkweb"}), 400
            db_collection = dw_db[option]
        else:
            print("얜 뭐임?")
            return jsonify({"error": "Invalid category or option"}), 400

        # 검색 필터
        if keywords:
            search_filter = {"title": {"$regex": keywords, "$options": "i"}}
            cursor = db_collection.find(search_filter).sort("_id", -1)
        else:
            cursor = db_collection.find().sort("_id", -1)

        async for doc in cursor:
            result = {key: (str(value) if key == "_id" else value) for key, value in doc.items()}
            results.append(result)

    return jsonify({"results": results})




def run_flask():
    """Flask 서버를 별도의 쓰레드에서 실행"""
    print("[START] Flask 웹 서버를 실행합니다...")
    app.run(debug=False, use_reloader=False, threaded=True)

def run_async_crawler():
    """비동기 크롤러를 별도의 이벤트 루프에서 실행"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_crawler_periodically())
    finally:
        loop.close()


async def main():
    """Flask 서버 및 스케줄된 크롤링 작업 실행"""
    # Flask 서버를 쓰레드에서 실행
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # 크롤러 스레드 시작 (스케줄링 포함)
    crawler_thread = threading.Thread(target=run_async_crawler, daemon=True)
    crawler_thread.start()

    # 메인 스레드 유지
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] 프로그램을 종료합니다...")


if __name__ == "__main__":
    asyncio.run(main())