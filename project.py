
import streamlit as st
import pandas as pd

st.set_page_config(page_title="종합 툴 관리 대시보드", layout="wide")

st.title("🏭 다이아몬드 툴 종합 관리 대시보드 (검색/필터 기능)")
st.write("데이터가 쌓였을 때 사무실과 현장에서 어떻게 검색하고 관리하는지 확인해 보세요.")

st.markdown("---")

# --- 임시로 쌓여있는 데이터베이스 가상 데이터 (실험용) ---
if "tool_db" not in st.session_state:
    st.session_state.tool_db = pd.DataFrame([
        {"툴ID": "4P260529-200161", "툴종류": "#200전착", "상태": "사용중", "입고날짜": "2026-05-29", "장착기계": "#3호기", "가공제품": "하우징A", "가공수량": 150},
        {"툴ID": "4P260529-200162", "툴종류": "#200전착", "상태": "재연마 필요", "입고날짜": "2026-05-29", "장착기계": "#2호기", "가공제품": "하우징B", "가공수량": 420},
        {"툴ID": "4P260530-200163", "툴종류": "#200전착", "상태": "폐기완료", "입고날짜": "2026-05-30", "장착기계": "#1호기", "가공제품": "커버C", "가공수량": 850},
        {"툴ID": "4P260601-300001", "툴종류": "#400레진", "상태": "신품", "입고날짜": "2026-06-01", "장착기계": "미장착", "가공제품": "없음", "가공수량": 0},
        {"툴ID": "4P260602-200164", "툴종류": "#200전착", "상태": "사용중", "입고날짜": "2026-06-02", "장착기계": "#3호기", "가공제품": "하우징A", "가공수량": 95},
    ])

# 화면을 왼쪽(입력창)과 오른쪽(검색 및 테이블)으로 나눕니다.
col1, col2 = st.columns([1, 2])

# --- 왼쪽: 현장 정보 입력 및 수정 칸 ---
with col1:
    st.subheader("📥 툴 정보 등록/수정")
    target_id = st.text_input("🆔 대상 툴 고유번호 입력", value="4P260529-200161")
    
    # 아까 검증한 똑똑한 달력창들
    in_date = st.date_input("📅 입고 날짜", value=pd.Timestamp.now().date())
    mount_date = st.date_input("🛠️ 기계 장착 날짜", value=pd.Timestamp.now().date())
    
    machine_num = st.text_input("🤖 장착 기계 번호", value="#3호기")
    product_name = st.text_input("📦 가공 제품명", value="스마트폰 하우징A")
    tool_status = st.selectbox("💡 현재 툴 상태", ["신품", "사용중", "재연마 필요", "폐기완료"])
    qty = st.number_input("🔢 가공 수량 (개)", min_value=0, value=150)
    
    if st.button("🚀 설정된 값으로 DB 업데이트"):
        # 임시 데이터베이스에 사용자가 입력한 값 수정/추가 반영
        new_row = {
            "툴ID": target_id, "툴종류": "#200전착" if "20" in target_id else "#400레진", 
            "상태": tool_status, "입고날짜": str(in_date), "장착기계": machine_num, 
            "가공제품": product_name, "가공수량": qty
        }
        # 중복 ID가 있으면 지우고 새로 덮어쓰기
        st.session_state.tool_db = st.session_state.tool_db[st.session_state.tool_db["툴ID"] != target_id]
        st.session_state.tool_db = pd.concat([st.session_state.tool_db, pd.DataFrame([new_row])], ignore_index=True)
        st.success(f"✅ {target_id} 툴 정보가 데이터베이스에 저장되었습니다!")
        st.rerun()

# --- 오른쪽: 대망의 검색 및 데이터 시트 현황 조회 ---
with col2:
    st.subheader("🔍 실시간 데이터베이스 검색 및 필터")
    
    # 1. 상단 검색창 구성 (가로로 배치)
    search_cols = st.columns(3)
    
    with search_cols[0]:
        # 고유번호나 기계번호 등 아무 글자나 쳐서 검색하는 칸
        search_keyword = st.text_input("🔎 만능 텍스트 검색 (ID, 기계 등)", value="")
        
    with search_cols[1]:
        # 특정 상태만 필터링하는 선택창
        filter_status = st.selectbox("🎯 툴 상태 필터", ["전체 보기", "신품", "사용중", "재연마 필요", "폐기완료"])
        
    with search_cols[2]:
        # 특정 기계만 필터링하는 선택창
        filter_machine = st.selectbox("🤖 기계별 필터", ["전체 보기", "#1호기", "#2호기", "#3호기", "미장착"])

    # 2. [검색 로직 작동] 사용자가 입력한 조건에 맞게 데이터를 걸러냅니다.
    filtered_df = st.session_state.tool_db.copy()
    
    # 텍스트 검색창에 글자가 들어가 있으면 필터링
    if search_keyword:
        filtered_df = filtered_df[
            filtered_df["툴ID"].str.contains(search_keyword) | 
            filtered_df["장착기계"].str.contains(search_keyword) |
            filtered_df["가공제품"].str.contains(search_keyword)
        ]
        
    # 상태 필터가 선택되어 있으면 필터링
    if filter_status != "전체 보기":
        filtered_df = filtered_df[filtered_df["상태"] == filter_status]
        
    # 기계 필터가 선택되어 있으면 필터링
    if filter_machine != "전체 보기":
        filtered_df = filtered_df[filtered_df["장착기계"] == filter_machine]

    # 3. 최종 필터링된 결과 테이블 출력
    st.write(f"📊 검색된 툴 개수: **{len(filtered_df)}**개")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    
    # 간단한 현장 통계 안내 정보
    st.info("💡 팁: 현장에서 스마트폰으로 61번 QR코드를 찍으면, 왼쪽 입력창의 고유번호 칸에 번호가 자동으로 입력되면서 해당 데이터가 바로 검색창에 뜨게 결합될 예정입니다.")
