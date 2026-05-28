import streamlit as st
import pandas as pd

st.set_page_config(page_title="툴 관리 시스템 달력 테스트", layout="centered")

st.title("📱 툴 정보 수정 및 달력 시스템 테스트")
st.write("4PART 현장에서 스마트폰으로 지정해주세요")

st.markdown("---")

# 가상의 툴 고유번호 선택
st.subheader("🆔 선택된 툴: `4P260529-200161` (#200전착)")

# --- 달력창 시스템 구현 (st.date_input) ---

# 1. 입고일 설정 (기본값은 오늘 날짜, 달력으로 수정 가능)
in_date = st.date_input(
    "📅 1. 입고 날짜 수정", 
    value=pd.Timestamp.now().date(),
    help="클릭하면 달력이 나타납니다. 과거 날짜로 변경해 보세요."
)

# 2. 장착일 설정
mount_date = st.date_input(
    "🛠️ 2. 기계 장착 날짜 수정", 
    value=pd.Timestamp.now().date()
)

# 3. 폐기일 설정 (기본값은 비워두거나 오늘 날짜로 세팅 가능)
discard_date = st.date_input(
    "🗑️ 3. 폐기 날짜 등록 (필요시 수정)", 
    value=pd.Timestamp.now().date()
)

st.markdown("---")

# --- 다른 정보 입력칸도 잘 작동하는지 확인 ---
st.subheader("📝 기타 정보 입력")
machine_num = st.text_input("🤖 장착 기계 번호", value="#3호기")
product_name = st.text_input("📦 가공 제품명", value="스마트폰 하우징A")
tool_status = st.selectbox("💡 현재 툴 상태", ["신품", "사용중", "재연마 필요", "폐기완료"], index=1)

# 확인 버튼
if st.button("🚀 설정된 값으로 데이터베이스 저장 시뮬레이션"):
    st.success("🎉 아래의 날짜 정보가 완벽하게 인식되었습니다!")
    st.write(f"• 선택된 입고일: **{in_date}**")
    st.write(f"• 선택된 장착일: **{mount_date}**")
    st.write(f"• 선택된 폐기일: **{discard_date}**")
    st.write(f"• 매칭된 기계/제품: {machine_num} / {product_name} ({tool_status})")
