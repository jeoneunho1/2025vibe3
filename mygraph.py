import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="시도별 자살률 분석", layout="wide")
st.title("📊 대한민국 시도별 자살률 분석")

uploaded_file = st.file_uploader("📂 자살률 통계 파일 업로드 (.xlsx)", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name="데이터", engine="openpyxl")

    # 연도 컬럼 확인 및 정리
    year_cols = [str(col) for col in df.columns if str(col).isdigit()]
    for col in year_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 전체 데이터 중 '계' 성별, 유효 지역만 필터링
    df_total = df[(df["성별"] == "계") & (df["시군구별"].notna())].copy()
    df_total["시도"] = df_total["시군구별"]

    # 사용자 연도 범위 선택
    year_range = st.slider("분석 연도 범위 선택", min_value=1998, max_value=2023, value=(2003, 2023))
    selected_years = [str(y) for y in range(year_range[0], year_range[1] + 1)]

    # 지역 선택
    selected_region = st.selectbox("📍 분석할 시도 선택", options=df_total["시도"].unique())

    # 1. 변화율 계산
    df_total["변화율(%)"] = ((df_total["2023"] - df_total["2003"]) / df_total["2003"]) * 100

    # 3. 2003년 vs 2023년 자살률 랭킹 비교
    st.subheader("📊 2003년 vs 2023년 자살률 랭킹 비교")
    rank_2003 = df_total[["시도", "2003"]].sort_values(by="2003", ascending=False).reset_index(drop=True)
    rank_2023 = df_total[["시도", "2023"]].sort_values(by="2023", ascending=False).reset_index(drop=True)
    col1, col2 = st.columns(2)
    col1.write("📌 2003년 순위")
    col1.dataframe(rank_2003.rename(columns={"2003": "자살률"}), use_container_width=True)
    col2.write("📌 2023년 순위")
    col2.dataframe(rank_2023.rename(columns={"2023": "자살률"}), use_container_width=True)

    # 4. 선택 지역의 연도별 변화율 그래프
    st.subheader(f"📈 {selected_region} 자살률 연도별 변화율 (%)")
    row = df_total[df_total["시도"] == selected_region]
    if not row.empty:
        changes = row[selected_years].pct_change(axis=1).T * 100
        changes.columns = [selected_region]
        st.line_chart(changes)
    else:
        st.warning("선택한 지역 데이터가 없습니다.")

    # 5. 사용자 연도 범위로 전체 평균 추이
    st.subheader("📈 전체 지역 평균 자살률 추이 (선택 연도 범위)")
    avg_data = df_total[selected_years].mean()
    st.line_chart(avg_data)

    # 7. 전국 평균보다 자살률 높은 지역 막대 그래프
    st.subheader("📊 2023년 전국 평균보다 자살률이 높은 지역")
    national_avg = df_total["2023"].mean()
    above_avg = df_total[df_total["2023"] > national_avg]
    fig_above = px.bar(above_avg.sort_values("2023", ascending=False),
                       x="시도", y="2023",
                       title="전국 평균 초과 지역 (2023)",
                       labels={"2023": "자살률"})
    fig_above.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_above)

    # 8. 자살률 최고/최저 지역 자동 표시
    top_region = df_total.loc[df_total["2023"].idxmax(), "시도"]
    bottom_region = df_total.loc[df_total["2023"].idxmin(), "시도"]
    st.success(f"🔺 2023년 자살률 1위 지역: **{top_region}**")
    st.info(f"🔻 2023년 자살률 최저 지역: **{bottom_region}**")

else:
    st.info("자살률 통계 엑셀 파일(.xlsx)을 업로드해주세요.")
