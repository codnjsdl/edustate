import streamlit as st
import pandas as pd

# ✅ CSS 스타일
st.markdown(
    """
<style>
.big-title {
    font-size: 36px;
    font-weight: bold;
    color: #2C3E50;
    margin-bottom: 0.2em;
}
.sub-title {
    font-size: 28px;
    font-weight: bold;
    color: #555;
    margin-bottom: 0.7em;
}
.form-box {
    background-color: #F8F9FA;
    padding: 20px 25px;
    border-radius: 10px;
    border: 1px solid #ddd;
    margin-bottom: 30px;
}
.result-box {
    background-color: #ECF3FC;
    padding: 15px 20px;
    border-radius: 8px;
    border: 1px solid #BBDFFB;
    margin-bottom: 30px;
}
</style>
""",
    unsafe_allow_html=True,
)


# ✅ 데이터 로딩 함수
@st.cache_data
def load_data():
    return pd.read_excel("25년 핵심역량강화교육 수료 현황.xlsx")


@st.cache_data
def load_target_courses():
    course_list_df = pd.read_csv("25년 핵심역량강화교육 목록.csv")
    completed_df = course_list_df[
        (course_list_df["상태"].str.strip() == "완료")
        & (course_list_df["일정"].notna())
        & (course_list_df["일정"].astype(str).str.strip() != "")
    ]
    course_names = set(completed_df["과정명"].dropna().str.strip())
    return course_names, completed_df.reset_index(drop=True)


# ✅ 초기 설정 및 데이터 로딩
st.set_page_config(page_title="교육 수강 현황 조회", layout="centered")
df = load_data()
target_courses, completed_courses_df = load_target_courses()

# ✅ 타이틀 영역
st.markdown('<div class="big-title">📖 수강 현황 조회</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">2025년 상반기 핵심역량교육 수강 이력 조회 시스템</div>',
    unsafe_allow_html=True,
)
st.markdown(
    "사번과 성명을 입력하면 본인의 교육 이력을 확인할 수 있습니다. 해당 시스템은 **핵심역량교육에 한해서만** 조회가 가능합니다."
)
st.markdown("---")

# ✅ 입력 폼 박스
with st.container():
    with st.form("조회폼"):
        col1, col2 = st.columns(2)
        with col1:
            emp_id = st.text_input("🔑 사번", "")
        with col2:
            emp_name = st.text_input("👤 성명", "")
        submitted = st.form_submit_button("조회하기")
    st.markdown("---")


# ✅ 조회 처리
if submitted and emp_id and emp_name:
    filtered_df = df[
        (df["사번"].astype(str) == emp_id.strip()) & (df["성명"] == emp_name.strip())
    ]

    if filtered_df.empty:
        st.warning("해당 사번과 성명으로 등록된 교육 이력이 없습니다.")
    else:
        filtered_df["교육구분"] = filtered_df["교육구분"].fillna("기타")
        filtered_df = filtered_df[filtered_df["교육과정명"].isin(target_courses)]

        edu_counts = filtered_df["교육구분"].value_counts()
        필수 = edu_counts.get("필수교육", 0)
        기타 = len(filtered_df) - 필수

        # ✅ 결과 박스
        with st.container():
            st.markdown(f"### ✅ **{emp_name}**님의 수료 교육 현황")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"🌏 **필수 교육 :** `{필수}` 개")
            with col2:
                st.markdown(f"🌕 **기타 교육 :** `{기타}` 개")
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("---")

        # ✅ 상세 이력 테이블
        st.markdown("### 📄 상세 교육 이력")
        show_df = filtered_df[["교육과정명", "교육구분"]].reset_index(drop=True)
        show_df.index = show_df.index + 1

        def highlight_row(row):
            color = "#EAF3FF" if row["교육구분"] == "필수교육" else "#F9F9F9"
            return [f"background-color: {color}" for _ in row]

        st.dataframe(
            show_df.style.apply(highlight_row, axis=1).set_properties(
                **{"text-align": "center"}
            ),
            use_container_width=True,
        )

        # ✅ 전체 개강 과정 목록
        st.markdown("---")
        st.markdown("### 📢 2025년 상반기 개강된 교육 과정 목록")

        display_df = (
            completed_courses_df[["과정명", "추천 대상", "구분"]]
            .dropna(subset=["과정명"])
            .reset_index(drop=True)
        )
        display_df.index = display_df.index + 1

        st.dataframe(
            display_df.style.set_properties(**{"text-align": "center"}),
            use_container_width=True,
        )
