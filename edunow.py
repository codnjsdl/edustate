import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

st.markdown(
    """
<style>
body {
    background-color: #EBF5FB !important;
}
[data-testid="stAppViewContainer"] {
    background-color: #E0E4F5;
}
.big-title {
    font-size: 32px;
    font-weight: bold;
    color: #2C3E50;
    margin-bottom: 0.2em;
}
button[kind="formSubmit"] {
    width: 100% !important;
    height: 3em !important;
    font-size: 1.1em !important;
    font-weight: 600;
    background-color: #1f77b4 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    transition: 0.3s;
}
button[kind="formSubmit"]:hover {
    background-color: #145a96 !important;
}
</style>
""",
    unsafe_allow_html=True,
)


# 엑셀 읽기
@st.cache_data
def load_data():
    file = pd.ExcelFile("25년 1h 핵심역량강화교육 수료 현황.xlsx")
    history_df = file.parse("수료현황")
    person_df = file.parse("개인별_이수필요")
    return history_df, person_df


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


st.set_page_config(page_title="교육 수강 현황 조회", layout="wide")
df, person_df = load_data()
target_courses, completed_courses_df = load_target_courses()

# 사이드바
with st.sidebar:
    selected = option_menu(
        menu_title="",
        options=["수강 현황 조회", "교육 목록"],
        icons=["search", "book"],
        default_index=0,
    )

# 탭1
if selected == "수강 현황 조회":
    st.markdown(
        '<div class="big-title">2025년 핵심역량강화교육 수강 현황 조회</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "사번과 성명을 입력하면 2025년 본인의 교육 이력과 이수 여부를 확인할 수 있습니다.  \n문의사항은 **피플&컬처팀 이채원 대리**에게 문의 바랍니다."
    )
    st.markdown("---")

    with st.form("조회폼"):
        col1, col2 = st.columns(2)
        with col1:
            emp_id = st.text_input("**사번**", "")
        with col2:
            emp_name = st.text_input("**성명**", "")
        submitted = st.form_submit_button("조회", use_container_width=True)

        if submitted:
            if not emp_id and not emp_name:
                st.warning("※ 사번과 성명을 모두 입력해 주세요.")
            elif not emp_id:
                st.warning("※ 사번을 입력해 주세요.")
            elif not emp_name:
                st.warning("※ 성명을 입력해 주세요.")
            elif not emp_id.isdigit():
                st.warning("※ 사번은 숫자만 입력해 주세요.")

    st.markdown("---")

    if submitted and emp_id and emp_name:
        edu_df = df[
            (df["사번"].astype(str) == emp_id.strip())
            & (df["성명"] == emp_name.strip())
        ]
        person_info = person_df[
            (person_df["사번"].astype(str) == emp_id.strip())
            & (person_df["성명"] == emp_name.strip())
        ]

        if edu_df.empty and person_info.empty:
            st.warning("해당 사번과 성명으로 등록된 정보가 없습니다.")
        else:
            has_position = False
            info = None
            if not person_info.empty:
                info = person_info.iloc[0]
                has_position = (
                    pd.notna(info.get("직책")) and str(info["직책"]).strip() != ""
                )

                # 직책 O 안내 문구만
                if has_position:
                    st.info(
                        f"📢 **{info['성명']}님은 {info['직책']}입니다. {info['직책']}의 경우, 교육 이수 대상자에 해당되지 않습니다.**"
                    )
                else:
                    st.markdown(f"### **{info['성명']}**님의 기본 정보")
                    st.markdown(f"- **직위명:**  **{info['직위명']}**")
                    st.markdown(f"- **직위연차:**  **{info['직급년차']}년차**")
                    st.markdown("---")

            # 교육 필터링 및 수료 개수 계산
            edu_df["교육구분"] = edu_df["교육구분"].fillna("공통교육")
            edu_df = edu_df[edu_df["교육과정명"].isin(target_courses)]

            필수_수료 = edu_df["교육구분"].value_counts().get("필수교육", 0)
            공통_수료 = len(edu_df) - 필수_수료

            st.markdown("### 수료 교육 현황")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"- **필수 교육:** **{필수_수료}개**")
            with col2:
                st.markdown(f"- **공통 교육:** **{공통_수료}개**")

            # 직책 X 필요 개수 계산
            if not has_position and info is not None:
                필수_기준 = int(info.get("필수", 0))
                공통_기준 = int(info.get("공통", 0))

                필수_차이 = 필수_수료 - 필수_기준
                공통_차이 = 공통_수료 - 공통_기준

                if 필수_차이 < 0:
                    st.error(
                        f"🔔 필수 교육 `{abs(필수_차이)}`개 추가 수강이 필요합니다."
                    )
                else:
                    st.success("필수 교육을 모두 수료하셨습니다.")

                if 공통_차이 < 0:
                    st.error(
                        f"🔔 공통 교육 `{abs(공통_차이)}`개 추가 수강이 필요합니다."
                    )
                else:
                    st.success("공통 교육을 모두 수료하셨습니다.")

            # 상세 수료 이력 테이블
            st.markdown("---")
            st.markdown("### 상세 교육 이력")

            show_df = edu_df[
                ["교육과정명", "교육구분", "교육시작일", "교육종료일"]
            ].copy()

            # 날짜 포맷 통일
            show_df["교육시작일"] = pd.to_datetime(show_df["교육시작일"]).dt.strftime(
                "%Y-%m-%d"
            )
            show_df["교육종료일"] = pd.to_datetime(show_df["교육종료일"]).dt.strftime(
                "%Y-%m-%d"
            )

            # 정렬 및 인덱스
            show_df = show_df.sort_values(by="교육시작일").reset_index(drop=True)
            show_df.index = show_df.index + 1

            # ✅ 필수교육/기타교육 색상 하이라이트 함수
            def highlight_row(row):
                color = "#FFF4EA" if row["교육구분"] == "필수교육" else "#F9F9F9"
                return [f"background-color: {color}" for _ in row]

            st.dataframe(
                show_df.style.apply(highlight_row, axis=1).set_properties(
                    **{"text-align": "center"}
                ),
                use_container_width=True,
            )


# 탭 2
elif selected == "교육 목록":
    st.markdown(
        '<div class="big-title">2025년 개강 교육 목록</div>',
        unsafe_allow_html=True,
    )
    st.markdown("2025년 현재까지 개강된 핵심역량강화교육 목록을 확인할 수 있습니다.")
    st.markdown("---")

    display_df = (
        completed_courses_df[["과정명", "일정", "추천 대상", "구분"]]
        .dropna(subset=["과정명"])
        .reset_index(drop=True)
    )

    display_df = display_df.sort_values(by="일정").reset_index(drop=True)
    display_df.index = display_df.index + 1

    def all_edu_highlight_row(row):
        color = "#FFF4EA" if row["구분"] == "필수" else "#F9F9F9"
        return [f"background-color: {color}" for _ in row]

    st.dataframe(
        display_df.style.apply(all_edu_highlight_row, axis=1).set_properties(
            **{"text-align": "center"}
        ),
        use_container_width=True,
    )
