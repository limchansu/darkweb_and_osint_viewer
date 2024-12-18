import time
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import asyncio
import multiprocessing
import os

# Flask 앱 초기화
app = Flask(__name__)
CORS(app)

from main import setup_database, exec_crawler


# 라우팅
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
    db_collection = None
    results = []

    # 컬렉션 선택
    if category == "osint":
        db_collection = osint_db[option]
    elif category == "darkweb":
        db_collection = dw_db[option]
    else:
        return jsonify({"error": "Invalid collection"}), 400

    # 검색어가 있을 경우 제목에서 검색
    if keywords:
        search_filter = {"title": {"$regex": keywords, "$options": "i"}}
        cursor = db_collection.find(search_filter)
    else:
        cursor = db_collection.find()

    # DB 탐색 결과 가공
    async for doc in cursor:
        # 모든 필드를 포함하여 반환
        result = {key: (str(value) if key == "_id" else value) for key, value in doc.items()}
        results.append(result)

    return jsonify({"results": results})


def run_flask():
    """
    Flask 서버를 실행
    """
    print("[START] Flask 웹 서버를 실행합니다...")
    app.run(debug=True, use_reloader=False, threaded=True, host="0.0.0.0")


def run_crawler():
    """
    크롤러 작업을 실행
    """
    print("[INFO] 크롤러 작업을 실행합니다...")
    asyncio.run(exec_crawler())


if __name__ == "__main__":
    time.sleep(25)
    try:
        # 크롤러 작업을 별도의 프로세스로 실행
        crawler_process = multiprocessing.Process(target=run_crawler, daemon=True)
        crawler_process.start()

        # 메인 프로세스에서 Flask 서버 실행
        run_flask()

        # 크롤러 프로세스 종료 관리
        crawler_process.join()
    except KeyboardInterrupt:
        print("\n[EXIT] 프로그램을 종료합니다.")

