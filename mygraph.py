import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="시도별 자살률 분석", layout="wide")
st.title("📊 대한민국 시도별 자살률 분석")

uploaded_file = st.file_uploader("📂 자살률 통계 파일 업로드 (.xlsx)", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name="데이터", engine="openpyxl")

    # 연도 컬럼 확인 및 문자열로 변환
    year_cols = [str(col) for col in df.columns if str(col).isdigit()]

    # 숫자형으로 변환
    for col in year_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 📈 시도별 성별 추이
    st.subheader("📈 시도별 성별 자살률 추이")
    region_options = df["시군구별"].dropna().unique()
    selected_region = st.selectbox("📍 시도 선택", options=region_options)

    gender_filtered = df[(df["시군구별"] == selected_region) & (df["성별"].isin(["남자", "여자", "계"]))]
    trend_df = gender_filtered[year_cols].copy()
    trend_df.index = gender_filtered["성별"].values
    trend_df = trend_df.transpose()

    fig = go.Figure()
    for gender in trend_df.columns:
        fig.add_trace(go.Scatter(x=trend_df.index, y=trend_df[gender],
                                 mode="lines+markers", name=gender))
    fig.update_layout(title=f"{selected_region} 성별 자살률 추이 (1998~2023)",
                      xaxis_title="연도", yaxis_title="자살률 (명/10만명)")
    st.plotly_chart(fig)

    # 📊 시군구 자살률 막대 그래프
    st.subheader("📊 특정 연도 시군구 자살률 순위")
    selected_year = st.selectbox("연도 선택", options=year_cols[::-1], index=0)

    df_total = df[(df["성별"] == "계") & (df["시군구별"].notna())].copy()
    df_total["시도"] = df_total["시군구별"]
    bar_data = df_total[["시도", selected_year]].copy()
    bar_data.rename(columns={selected_year: "자살률"}, inplace=True)

    fig_bar = px.bar(bar_data.sort_values("자살률", ascending=False),
                     x="시도", y="자살률",
                     title=f"{selected_year}년 시군구별 자살률 순위",
                     labels={"자살률": "자살률 (명/10만명)", "시도": "시도"})
    fig_bar.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_bar)

    # 📉 자살률 감소 추이 (2003 → 2023)
    st.subheader("📉 자살률 감소량 순위 (2003 → 2023)")
    df_total["감소량"] = df_total["2003"] - df_total["2023"]
    decrease_df = df_total[["시도", "감소량"]].dropna().sort_values(by="감소량", ascending=False)

    fig_decrease = px.bar(decrease_df,
                          x="시도", y="감소량",
                          title="2003 → 2023 자살률 감소량 상위 지역",
                          labels={"감소량": "자살률 감소량"})
    fig_decrease.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_decrease)

    # 🔍 전국 평균과 비교
    st.subheader("🔍 전국 평균 자살률과 비교")
    national_avg = df_total[year_cols].mean(numeric_only=True)

    selected_row = df_total[df_total["시도"] == selected_region]
    if not selected_row.empty:
        selected_values = selected_row.iloc[0][year_cols].values
        comparison_data = pd.DataFrame({
            "연도": year_cols,
            "전국 평균": national_avg.values,
            selected_region: selected_values
        })
        comparison_data = comparison_data.set_index("연도")
        st.line_chart(comparison_data)
    else:
        st.warning("선택한 지역 데이터가 없습니다.")

else:
    st.info("먼저 자살률 통계 엑셀 파일을 업로드해주세요. (.xlsx)")
