import streamlit as st
import pandas as pd
from pymongo import MongoClient
from streamlit_autorefresh import st_autorefresh
import os

# 💡 [DNS 에러 방지] 주소를 해석하지 못하는 버그를 막기 위해 강제 로드 시도
try:
    import dns.resolver
except ImportError:
    pass

# =================================================================
# 🚨 [중요 설정] 5초마다 자동으로 화면을 새로고침하여 양방향 동기화 유지
# =================================================================
st_autorefresh(interval=5000, limit=9999, key="db_sync_counter")

st.set_page_config(page_title="다이아몬드 툴 관리 시스템", layout="wide")

st.title("🏭 4PART (검색/필터 기능)")
st.write("사무실 및 현장관리 (실시간 클라우드 DB 양방향 연동)")
st.markdown("---")


MONGO_URI = "mongodb+srv://sspon1270_db_user:wXA7NGCMjjTiTG5w@cluster0.lectnsv.mongodb.net/tool_manager?appName=Cluster0"

# 에러로 인해 변수가 미정의되는 것을 방지하기 위해 초기화
collection = None

def get_mongo_collection():
    # 연결 타임아웃을 5초로 제한하여 무한 대기 방지
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client["tool_manager"]  # 데이터베이스 이름
    return db["tools"]           # 컬렉션(테이블) 이름

try:
    collection = get_mongo_collection()
    # 실제로 연결이 잘 붙는지 핑을 때려 확인해봅니다.
    collection.database.client.admin.command('ping')
except Exception as e:
    st.error(f"❌ 데이터베이스 연결 실패: {e}")
    st.info("💡 팁: 컴퓨터가 회사 보안망(인터넷 차단) 환경이거나, 파이썬 환경에 dnspython 패키지가 없는 경우 발생할 수 있습니다.")

# --- DB에서 최신 데이터를 실시간으로 가져오는 함수 ---
def load_live_data():
    # 위의 try문에서 collection 연결이 실패했다면 빈 데이터프레임 반환
    if collection is None:
        return pd.DataFrame()
        
    try:
        live_data = list(collection.find({}, {"_id": 0}))
        
        if not live_data:
            sample_data = [
                {"툴ID": "4P260529-200161", "툴종류": "#200전착", "상태": "사용중", "입고날짜": "2026-05-29", "장착기계": "#3호기", "가공제품": "하우징A", "가공수량": 150},
                {"툴ID": "4P260529-200162", "툴종류": "#200전착", "상태": "재연마 필요", "입고날짜": "2026-05-29", "장착기계": "#2호기", "가공제품": "하우징B", "가공수량": 420},
                {"툴ID": "4P260530-200163", "툴종류": "#200전착", "상태": "폐기완료", "입고날짜": "2026-05-30", "장착기계": "#1호기", "가공제품": "커버C", "가공수량": 850},
                {"툴ID": "4P260601-300001", "툴종류": "#400레진", "상태": "신품", "입고날짜": "2026-06-01", "장착기계": "미장착", "가공제품": "없음", "가공수량": 0},
                {"툴ID": "4P260602-200164", "툴종류": "#200전착", "상태": "사용중", "입고날짜": "2026-06-02", "장착기계": "#3호기", "가공제품": "하우징A", "가공수량": 95}
            ]
            collection.insert_many(sample_data)
            live_data = sample_data
            
        return pd.DataFrame(live_data)
    except Exception as e:
        st.error(f"⚠️ 데이터를 불러오는 중 오류 발생: {e}")
        return pd.DataFrame()

# 갱신된 최신 데이터프레임 확보
current_df = load_live_data()

# 화면을 왼쪽(입력창)과 오른쪽(검색 및 테이블)으로 나눕니다.
col1, col2 = st.columns([1, 2])

# --- 왼쪽: 현장 정보 입력 및 수정 칸 ---
with col1:
    st.subheader("📥 툴 정보 등록/수정")
    target_id = st.text_input("🆔 대상 툴 고유번호 입력", value="4P260529-200161")
    
    in_date = st.date_input("📅 입고 날짜", value=pd.Timestamp.now().date())
    mount_date = st.date_input("🛠️ 기계 장착 날짜", value=pd.Timestamp.now().date())
    
    machine_num = st.text_input("🤖 장착 기계 번호", value="#3호기")
    product_name = st.text_input("📦 가공 제품명", value="스마트폰 하우징A")
    tool_status = st.selectbox("💡 현재 툴 상태", ["신품", "사용중", "재연마 필요", "폐기완료"])
    qty = st.number_input("🔢 가공 수량 (개)", min_value=0, value=150)
    
    if st.button("🚀 설정된 값으로 DB 업데이트"):
        if collection is None:
            st.error("❌ 현재 데이터베이스에 연결되어 있지 않아 저장할 수 없습니다.")
        else:
            new_row = {
                "툴ID": target_id, 
                "툴종류": "#200전착" if "20" in target_id else "#400레진", 
                "상태": tool_status, 
                "입고날짜": str(in_date), 
                "장착기계": machine_num, 
                "가공제품": product_name, 
                "가공수량": qty
            }
            
            try:
                collection.update_one(
                    {"툴ID": target_id},
                    {"$set": new_row},
                    upsert=True
                )
                st.success(f"✅ {target_id} 툴 정보가 데이터베이스에 실시간 저장되었습니다!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ 데이터베이스 저장 실패: {e}")

# --- 오른쪽: 대망의 검색 및 데이터 시트 현황 조회 ---
with col2:
    st.subheader("🔍 실시간 데이터베이스 검색 및 필터")
    
    # 1. 상단 검색창 구성 (가로로 배치)
    search_cols = st.columns(3)
    
    with search_cols[0]:
        search_keyword = st.text_input("🔎 만능 텍스트 검색 (ID, 기계 등)", value="")
        
    with search_cols[1]:
        filter_status = st.selectbox("🎯 툴 상태 필터", ["전체 보기", "신품", "사용중", "재연마 필요", "폐기완료"])
        
    with search_cols[2]:
        filter_machine = st.selectbox("🤖 기계별 필터", ["전체 보기", "#1호기", "#2호기", "#3호기", "미장착"])

    # 2. [검색 로직 작동] 항상 실시간으로 읽어온 current_df를 기반으로 가공
    if not current_df.empty:
        filtered_df = current_df.copy()
        
        if search_keyword:
            filtered_df = filtered_df[
                filtered_df["툴ID"].str.contains(search_keyword, na=False) | 
                filtered_df["장착기계"].str.contains(search_keyword, na=False) |
                filtered_df["가공제품"].str.contains(search_keyword, na=False)
            ]
            
        if filter_status != "전체 보기":
            filtered_df = filtered_df[filtered_df["상태"] == filter_status]
            
        if filter_machine != "전체 보기":
            filtered_df = filtered_df[filtered_df["장착기계"] == filter_machine]

        # 3. 최종 필터링된 결과 테이블 출력
        st.write(f"📊 검색된 툴 개수: **{len(filtered_df)}**개")
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ 현재 불러올 수 있는 데이터가 없습니다. DB 연결 상태를 확인해 주세요.")
    
    st.info("💡 실시간 동기화 활성화 중: 핸드폰이나 PC 어느 쪽에서 수정하든 최대 5초 이내에 양쪽 화면이 모두 자동 동기화됩니다.")

