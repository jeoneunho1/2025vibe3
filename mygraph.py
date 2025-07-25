import streamlit as st
import pandas as pd
import plotly.express as px

# 엑셀 파일 업로드
uploaded_file = st.file_uploader("📂 자살률 통계 파일 업로드 (.xlsx)", type="xlsx")

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    df = xls.parse("데이터")

    # 시도별, 성별=계 필터링
    df_filtered = df[(df["성별"] == "계") & (df["시군구별"].notna())].copy()
    df_filtered["시도"] = df_filtered["시군구별"]

    # 연도 선택
    selected_year = st.selectbox("📅 연도 선택", options=[str(y) for y in range(1998, 2024)], index=25)
    map_data = df_filtered[["시도", selected_year]].copy()
    map_data.rename(columns={selected_year: "자살률"}, inplace=True)

    # 바 차트 시각화
    st.subheader(f"📊 {selected_year}년 시도별 자살률")
    fig = px.bar(map_data.sort_values("자살률", ascending=False),
                 x="시도", y="자살률",
                 labels={"자살률": "자살률 (명/10만명)", "시도": "시도"},
                 title=f"{selected_year}년 시도별 자살률 (인구 10만 명당)")
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig)

    # 꺾은선 그래프
    st.subheader("📈 특정 시도 자살률 추이")
    selected_sido = st.selectbox("시도 선택", options=df_filtered["시도"].unique())
    line_df = df_filtered[df_filtered["시도"] == selected_sido].iloc[0, 2:-1].astype(float)
    st.line_chart(line_df)

