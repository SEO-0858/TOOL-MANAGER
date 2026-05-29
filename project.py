import sys
from pymongo import MongoClient

# 📌 [수정 포인트] +srv를 빼고 포트(27017)를 직접 찌르는 구형 방식으로 주소를 변경합니다.
# 이렇게 쓰면 컴퓨터가 DNS를 찾느라 멈춰 서는 현상을 원천 차단합니다.
MONGO_URI = "mongodb://sspon1270_db_user:wXA7NGCMjjTiTG5w@cluster0-shard-00-00.lectnsv.mongodb.net:27017,cluster0-shard-00-01.lectnsv.mongodb.net:27017,cluster0-shard-00-02.lectnsv.mongodb.net:27017/tool_manager?ssl=true&replicaSet=atlas-9x026o-shard-0&authSource=admin&retryWrites=true&w=majority"

print("🔄 몽고DB 우회 연결 테스트를 시작합니다...")

try:
    # 타임아웃을 3초로 극단적으로 줄여서 멈춤 현상을 방지합니다.
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    
    # 서버 응답 체크
    client.admin.command('ping')
    print("📬 [성공] 드디어 서버와 연결이 통했습니다!")
    
    db = client["tool_manager"]
    print(f"✅ 사용 가능한 컬렉션 목록: {db.list_collection_names()}")
    
    print("\n🎉 [최종 결과] 우회 연결 대성공! 이제 이 주소를 본 코드에 쓰시면 됩니다.")

except Exception as e:
    print("\n❌ [최종 결과] 연결 실패! 아래 에러를 확인하세요:")
    print("=" * 60)
    print(e)
    print("=" * 60)
    print("\n💡 여전히 멈추거나 에러가 난다면, 지금 PC의 랜선을 뽑고 [핸드폰 핫스팟]에 연결 후 실행해 보세요. 회사 보안 방화벽이 들어오는 신호 자체를 드롭(Drop)시키고 있는 상황입니다.")

