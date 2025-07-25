import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="시도별 자살률 분석", layout="wide")
st.title("📊 대한민국 시도별 자살률 분석 (1998~2023)")

uploaded_file = st.file_uploader("📂 자살률 통계 파일 업로드 (.xlsx)", type="xlsx")

if uploaded_file:
    # 엑셀 데이터 읽기
    df = pd.read_excel(uploaded_file, sheet_name="데이터", engine="openpyxl")

    # 📍 시도 선택
    region_options = df["시군구별"].dropna().unique()
    selected_region = st.selectbox("📍 시도 선택", options=region_options, index=0)

    # 📈 꺾은선 그래프 - 남자/여자/계
    st.subheader(f"📈 {selected_region}의 성별 자살률 추이")

    filtered = df[(df["시군구별"] == selected_region) & (df["성별"].isin(["남자", "여자", "계"]))]
    year_cols = [col for col in filtered.columns if str(col).isdigit()]
    trend = filtered[year_cols]
    trend.index = filtered["성별"].values
    trend = trend.transpose()  # 연도별로 전치

    fig_line = go.Figure()
    for gender in trend.columns:
        fig_line.add_trace(go.Scatter(x=trend.index, y=trend[gender],
                                      mode="lines+markers", name=gender))

    fig_line.update_layout(title=f"{selected_region} 성별 자살률 추이 (1998~2023)",
                           xaxis_title="연도", yaxis_title="자살률 (명/10만명)",
                           legend_title="성별")

    st.plotly_chart(fig_line)

    # 📊 막대 그래프 - 전체 시도 자살률 비교
    st.subheader("📊 연도별 시도 자살률 비교")
    year_list = [str(y) for y in range(1998, 2024)]
    selected_year = st.selectbox("📅 자살률 비교할 연도 선택", options=year_list[::-1], index=0)

    df_filtered = df[(df["성별"] == "계") & (df["시군구별"].notna())].copy()
    df_filtered["시도"] = df_filtered["시군구별"]
    map_data = df_filtered[["시도", selected_year]].copy()
    map_data.rename(columns={selected_year: "자살률"}, inplace=True)

    fig_bar = px.bar(map_data.sort_values("자살률", ascending=False),
                     x="시도", y="자살률",
                     labels={"자살률": "자살률 (명/10만명)", "시도": "시도"},
                     title=f"{selected_year}년 시도별 자살률 (인구 10만 명당)")
    fig_bar.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_bar)

else:
    st.info("자살률 통계 엑셀 파일을 업로드해주세요.")
