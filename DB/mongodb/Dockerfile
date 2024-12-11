FROM mongo:6.0

# MongoDB Shell(mongosh)을 설치하기 위한 패키지 설정
RUN apt-get update && apt-get install -y curl gnupg \
  && curl -sL https://www.mongodb.org/static/pgp/server-6.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-keyring.gpg \
  && echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-keyring.gpg ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list \
  && apt-get update && apt-get install -y mongodb-mongosh
# 작업 디렉토리 설정
WORKDIR /usr/src/configs

# 필요한 파일 복사
COPY replicaSet.js .
COPY setup.sh .

# 스크립트에 실행 권한 추가
RUN chmod +x ./setup.sh

# 초기화 스크립트 실행
CMD ["./setup.sh"]
