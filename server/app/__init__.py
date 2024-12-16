from flask import Flask, request, jsonify, render_template
import sys, os

# 실행 시 경로 포함
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from connect_db import connect_databases

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    # 요청 파라미터
    query = request.args.get('query', '').strip()
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    search_type = request.args.get('searchType', 'osint').lower()  # 'osint' 또는 'darkweb'

    # 데이터베이스 연결
    osint_db, dw_db = connect_databases()

    # 초기화
    db_collection = None
    results = []
    total_results = 0

    # 컬렉션 선택
    if search_type == 'osint':
        valid_collections = ['0x00org', 'github', 'tuts4you']
        collection_name = request.args.get('collection', '0x00org')
        if collection_name not in valid_collections:
            return jsonify({"error": "Invalid collection for OSINT"}), 400
        db_collection = osint_db[collection_name]
    elif search_type == 'darkweb':
        valid_collections = ['abyss', 'blackbasta', 'blacksuit', 'breachdetector', 'ctifeeds', 'daixin', 'darkleak', 'darknetARMY', 'everest', 'island', 'leakbase', 'lockbit', 'play', 'rhysida']
        collection_name = request.args.get('collection', 'abyss')
        if collection_name not in valid_collections:
            return jsonify({"error": "Invalid collection for Darkweb"}), 400
        db_collection = dw_db[collection_name]
    else:
        return jsonify({"error": "Invalid searchType"}), 400

    # 데이터베이스에서 검색
    if query:
        search_filter = {"title": {"$regex": query, "$options": "i"}}  # 대소문자 구분 없는 검색
        cursor = db_collection.find(search_filter).skip((page - 1) * limit).limit(limit)
        total_results = db_collection.count_documents(search_filter)
    else:
        cursor = db_collection.find().skip((page - 1) * limit).limit(limit)
        total_results = db_collection.count_documents({})

    # 결과 가공
    for doc in cursor:
        result = {
            "_id": str(doc.get("_id")),  # ObjectId를 문자열로 변환
            "title": doc.get("title"),
            "url": doc.get("url")
        }
        results.append(result)

    # 총 페이지 수 계산
    total_pages = (total_results + limit - 1) // limit

    return jsonify({
        "results": results,
        "totalPages": total_pages,
        "currentPage": page,
        "totalResults": total_results
    })

if __name__ == '__main__':
    app.run(debug=True)
