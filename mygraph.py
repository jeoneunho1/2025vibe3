import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="시도별 자살률 분석", layout="wide")
st.title("📊 대한민국 시도별 자살률 분석 (1998~2023)")

# 엑셀 파일 업로드
uploaded_file = st.file_uploader("📂 자살률 통계 파일 업로드 (.xlsx)", type="xlsx")

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file, engine="openpyxl")
    df = xls.parse("데이터")

    # 유효한 연도 리스트 추출 (숫자형 컬럼만)
    year_cols = [str(c) for c in df.columns if isinstance(c, int) or str(c).isdigit()]
    
    # 📌 시도 선택
    st.subheader("📈 특정 시도 자살률 추이 (남/여/계 비교)")
    selected_sido = st.selectbox("시도 선택", options=df["시군구별"].dropna().unique())

    # 선택된 시도의 남/여/계 행 필터링
    line_df = df[(df["시군구별"] == selected_sido) & (df["성별"].isin(["계", "남자", "여자"]))]

    # 연도별 값만 추출하고 전치
    trend_df = line_df[year_cols].transpose()
    trend_df.columns = line_df["성별"].values
    trend_df.index = trend_df.index.astype(int)  # 연도 정수형

    # Plotly 그래프
    st.line_chart(trend_df)

    # 연도 선택 → 바 차트 시각화
    st.subheader("📊 연도별 시도 자살률 비교")
    selected_year = st.selectbox("📅 자살률 비교할 연도 선택", options=year_cols[::-1], index=0)

    df_filtered = df[(df["성별"] == "계") & (df["시군구별"].notna())].copy()
    df_filtered["시도"] = df_filtered["시군구별"]
    map_data = df_filtered[["시도", selected_year]].copy()
    map_data.rename(columns={selected_year: "자살률"}, inplace=True)

    fig = px.bar(map_data.sort_values("자살률", ascending=False),
                 x="시도", y="자살률",
                 labels={"자살률": "자살률 (명/10만명)", "시도": "시도"},
                 title=f"{selected_year}년 시도별 자살률 (인구 10만 명당)")
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig)

else:
    st.warning("왼쪽 사이드바에서 자살률 통계 엑셀 파일을 업로드해주세요.")
