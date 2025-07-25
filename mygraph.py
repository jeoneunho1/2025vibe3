import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="시도별 자살률 분석", layout="wide")
st.title("📊 대한민국 시도별 자살률 분석")

uploaded_file = st.file_uploader("📂 자살률 통계 파일 업로드 (.xlsx)", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name="데이터", engine="openpyxl")

    # 연도 컬럼 추출 및 숫자 변환
    year_cols = [str(col) for col in df.columns if str(col).isdigit()]
    for col in year_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # '계' 기준 분석용 전체 데이터
    df_total = df[(df["성별"] == "계") & (df["시군구별"].notna())].copy()
    df_total["시도"] = df_total["시군구별"]

    # 연도 범위 선택
    year_range = st.slider("📆 분석 연도 범위", 1998, 2023, (2003, 2023))
    selected_years = [str(y) for y in range(year_range[0], year_range[1] + 1)]

    # 지역 선택
    selected_region = st.selectbox("🏙️ 분석할 시도 선택", df_total["시도"].unique())

    # 변화율 계산
    df_total["변화율(%)"] = ((df_total["2023"] - df_total["2003"]) / df_total["2003"]) * 100

    # 📊 2003 vs 2023 랭킹
    st.subheader("📊 2003년 vs 2023년 자살률 순위 비교")
    col1, col2 = st.columns(2)
    col1.dataframe(df_total[["시도", "2003"]].sort_values("2003", ascending=False).reset_index(drop=True), use_container_width=True)
    col2.dataframe(df_total[["시도", "2023"]].sort_values("2023", ascending=False).reset_index(drop=True), use_container_width=True)

    # 📈 선택 지역 연도별 변화율
    st.subheader(f"📈 {selected_region} 자살률 변화율 (%)")
    selected_row = df_total[df_total["시도"] == selected_region]
    if not selected_row.empty:
        changes = selected_row[selected_years].pct_change(axis=1).T * 100
        changes.columns = [selected_region]
        st.line_chart(changes)
    else:
        st.warning("해당 지역 데이터가 없습니다.")

    # 📈 전체 지역 평균 자살률 추이
    st.subheader("📈 전체 평균 자살률 (선택 연도 범위)")
    avg_data = df_total[selected_years].mean()
    st.line_chart(avg_data)

    # 📉 전국 평균 자살률 변화율
    st.subheader("📉 전국 평균 자살률 변화율 (%)")
    avg_growth = df_total[year_cols].mean().pct_change() * 100
    st.line_chart(avg_growth)

    # 📊 전국 평균 초과 지역
    st.subheader("📊 2023년 전국 평균보다 자살률이 높은 지역")
    national_avg = df_total["2023"].mean()
    above_avg = df_total[df_total["2023"] > national_avg]
    fig_above = px.bar(above_avg.sort_values("2023", ascending=False),
                       x="시도", y="2023",
                       title="2023년 전국 평균 초과 지역",
                       labels={"2023": "자살률"})
    fig_above.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_above)

    # 🔺 최고 / 최저 지역
    top_region = df_total.loc[df_total["2023"].idxmax(), "시도"]
    bottom_region = df_total.loc[df_total["2023"].idxmin(), "시도"]
    st.success(f"🔺 2023년 자살률 1위 지역: **{top_region}**")
    st.info(f"🔻 2023년 자살률 최저 지역: **{bottom_region}**")

    # 🚻 성별 자살률 비교 (남자/여자)
    st.subheader(f"🚻 {selected_region} 성별 자살률 비교")
    gender_df = df[(df["시군구별"] == selected_region) & (df["성별"].isin(["남자", "여자"]))]
    if not gender_df.empty:
        chart_df = gender_df[["성별"] + year_cols].set_index("성별").T
        st.line_chart(chart_df)
    else:
        st.warning("성별 데이터가 부족하거나 존재하지 않습니다.")

else:
    st.info("먼저 자살률 통계 엑셀 파일 (.xlsx)을 업로드해주세요.")
