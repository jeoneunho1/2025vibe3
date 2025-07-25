import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="시도별 자살률 분석", layout="wide")
st.title("📊 대한민국 시도별 자살률 분석 대시보드")

# 기본 파일명 지정
DEFAULT_FILE = "인구십만명당_자살률_시도_시_군_구__20250725140130.xlsx"

# 파일 업로드 + 기본 파일 처리
uploaded_file = st.file_uploader("📂 자살률 통계 파일 업로드 (.xlsx)", type="xlsx")
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, sheet_name="데이터", engine="openpyxl")
elif os.path.exists(DEFAULT_FILE):
    st.info("📄 기본 데이터를 사용 중입니다.")
    df = pd.read_excel(DEFAULT_FILE, sheet_name="데이터", engine="openpyxl")
else:
    st.warning("❌ 파일이 없어요! 업로드하거나 기본 파일을 같은 폴더에 넣어주세요.")
    st.stop()

# 연도 컬럼 식별 및 정리
year_cols = [str(col) for col in df.columns if str(col).isdigit()]
for col in year_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# '계' 기준 시도 집계
df_total = df[(df["성별"] == "계") & (df["시군구별"].notna())].copy()
df_total["시도"] = df_total["시군구별"]

# 연도 범위 선택
year_range = st.slider("📆 분석 연도 범위 선택", 1998, 2023, (2003, 2023))
selected_years = [str(y) for y in range(year_range[0], year_range[1] + 1)]

# 지역 선택
selected_region = st.selectbox("🏙️ 분석할 시도 선택", df_total["시도"].unique())

# 변화율 계산
df_total["변화율(%)"] = ((df_total["2023"] - df_total["2003"]) / df_total["2003"]) * 100

# 랭킹 비교
st.subheader("📊 2003년 vs 2023년 자살률 순위 비교")
col1, col2 = st.columns(2)
col1.dataframe(df_total[["시도", "2003"]].sort_values("2003", ascending=False).reset_index(drop=True), use_container_width=True)
col2.dataframe(df_total[["시도", "2023"]].sort_values("2023", ascending=False).reset_index(drop=True), use_container_width=True)

# 선택 지역 연도별 변화율
st.subheader(f"📈 {selected_region} 자살률 연도별 변화율 (%)")
selected_row = df_total[df_total["시도"] == selected_region]
if not selected_row.empty:
    changes = selected_row[selected_years].pct_change(axis=1).T * 100
    changes.columns = [selected_region]
    st.line_chart(changes)
else:
    st.warning("해당 지역 데이터가 없습니다.")

# 전체 평균 추이
st.subheader("📈 전국 평균 자살률 추이")
avg_data = df_total[selected_years].mean()
st.line_chart(avg_data)

# 전국 평균 변화율
st.subheader("📉 전국 평균 자살률 변화율 (%)")
avg_growth = df_total[year_cols].mean().pct_change() * 100
st.line_chart(avg_growth)

# 평균 초과 지역
st.subheader("📊 2023년 전국 평균보다 높은 지역")
national_avg = df_total["2023"].mean()
above_avg = df_total[df_total["2023"] > national_avg]
fig_above = px.bar(above_avg.sort_values("2023", ascending=False),
                   x="시도", y="2023",
                   title="2023년 전국 평균 초과 지역",
                   labels={"2023": "자살률"})
fig_above.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_above)

# 최고 / 최저 지역
top_region = df_total.loc[df_total["2023"].idxmax(), "시도"]
bottom_region = df_total.loc[df_total["2023"].idxmin(), "시도"]
st.success(f"🔺 2023년 자살률 1위 지역: **{top_region}**")
st.info(f"🔻 2023년 자살률 최저 지역: **{bottom_region}**")

# 🚻 성별 자살률 비교 (시군구 단위로 평균)
st.subheader(f"🚻 {selected_region} 성별 자살률 비교")

# 해당 시도에 포함된 시군구 추출
sub_regions = df[df["시군구별"].str.startswith(selected_region) & df["성별"].isin(["남자", "여자"])]

# 성별 평균 계산
gender_avg = sub_regions.groupby("성별")[year_cols].mean()

if not gender_avg.empty:
    st.line_chart(gender_avg.T)
else:
    st.warning("해당 시도 내 성별 데이터가 부족합니다.")
