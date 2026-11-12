from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="펭귄 데이터 탐험", page_icon="🐧", layout="wide")
st.title("🐧 펭귄 데이터 탐험")
st.caption("Palmer Penguins · 남극 펭귄의 서식지와 신체 특성을 비교해 보세요.")

LABELS = {
    "species": "종", "island": "서식지", "sex": "성별",
    "bill_length_mm": "부리 길이 (mm)", "bill_depth_mm": "부리 깊이 (mm)",
    "flipper_length_mm": "날개 길이 (mm)", "body_mass_g": "몸무게 (g)",
}
MEASUREMENTS = list(LABELS)[3:]
SPECIES = ["Adelie", "Chinstrap", "Gentoo"]
COLORS = ["#0284C7", "#EA580C", "#7C3AED"]


@st.cache_data(max_entries=1)
def load_penguins():
    return pd.read_csv(Path(__file__).resolve().parents[1] / "data" / "penguins.csv")


penguins = load_penguins()
penguins["sex"] = penguins["sex"].map({"Male": "수컷", "Female": "암컷"}).fillna("미상")
with st.sidebar:
    st.header("탐색 필터")
    species = st.multiselect("펭귄 종", SPECIES, default=SPECIES)
    islands = sorted(penguins["island"].unique())
    island = st.multiselect("서식지", islands, default=islands)
    sex = st.multiselect("성별", ["수컷", "암컷", "미상"], default=["수컷", "암컷", "미상"])
    st.caption("성별을 확인하지 못한 개체는 ‘미상’으로 표시합니다.")

filtered = penguins[
    penguins["species"].isin(species)
    & penguins["island"].isin(island)
    & penguins["sex"].isin(sex)
].copy()
st.caption(f"전체 {len(penguins):,}마리 중 {len(filtered):,}마리 선택 · 모든 차트와 표에 필터가 적용됩니다.")
if filtered.empty:
    st.info("조건에 맞는 펭귄이 없습니다. 왼쪽 필터를 다시 선택해 주세요.")
    st.stop()

with st.container(horizontal=True):
    st.metric("선택한 펭귄", f"{len(filtered):,}마리", border=True)
    st.metric("펭귄 종", f"{filtered['species'].nunique()}종", border=True)
    mass = filtered["body_mass_g"].mean()
    flipper = filtered["flipper_length_mm"].mean()
    st.metric("평균 몸무게", f"{mass / 1000:.2f} kg" if pd.notna(mass) else "자료 없음", border=True)
    st.metric("평균 날개 길이", f"{flipper:.1f} mm" if pd.notna(flipper) else "자료 없음", border=True)

color = alt.Color("species:N", title="종", scale=alt.Scale(domain=SPECIES, range=COLORS))
left, right = st.columns([2, 1])
with left, st.container(border=True):
    st.subheader("신체 특성의 관계")
    x_col, y_col = st.columns(2)
    x = x_col.selectbox("가로축", MEASUREMENTS, format_func=LABELS.get)
    y = y_col.selectbox("세로축", MEASUREMENTS, index=1, format_func=LABELS.get)
    scatter_data = filtered.dropna(subset=[x, y])
    if scatter_data.empty:
        st.info("선택한 두 특성을 모두 측정한 개체가 없습니다.")
    else:
        chart = alt.Chart(scatter_data).mark_circle(size=75, opacity=0.7).encode(
            x=alt.X(f"{x}:Q", title=LABELS[x], scale=alt.Scale(zero=False)),
            y=alt.Y(f"{y}:Q", title=LABELS[y], scale=alt.Scale(zero=False)), color=color,
            tooltip=[alt.Tooltip("species:N", title="종"), alt.Tooltip("island:N", title="서식지"),
                     alt.Tooltip("sex:N", title="성별")]
            + [alt.Tooltip(f"{c}:Q", title=LABELS[c]) for c in dict.fromkeys([x, y])],
        ).properties(height=340).interactive()
        st.altair_chart(chart, alt="종별 펭귄의 신체 특성 산점도")
    st.caption(f"점 위에 마우스를 올려 자세히 확인하세요. 선택 축의 결측값 {len(filtered) - len(scatter_data)}마리는 차트에서 제외됩니다.")

with right, st.container(border=True):
    st.subheader("종별 개체 수")
    counts = filtered.groupby("species").size().reset_index(name="count")
    bars = alt.Chart(counts).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
        x=alt.X("species:N", title="종", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("count:Q", title="개체 수 (마리)", axis=alt.Axis(tickMinStep=1)),
        color=alt.Color("species:N", scale=alt.Scale(domain=SPECIES, range=COLORS), legend=None),
        tooltip=[alt.Tooltip("species:N", title="종"), alt.Tooltip("count:Q", title="개체 수")],
    ).properties(height=420)
    st.altair_chart(bars, alt="필터에 해당하는 종별 펭귄 개체 수")

with st.container(border=True):
    st.subheader("종별 신체 특성 비교")
    measurement = st.selectbox("비교할 특성", MEASUREMENTS, index=3, format_func=LABELS.get)
    measured = filtered.dropna(subset=[measurement])
    if measured.empty:
        st.info("선택한 특성의 측정값이 없습니다.")
    else:
        box = alt.Chart(measured).mark_boxplot(extent=1.5, size=45).encode(
            x=alt.X("species:N", title="종", axis=alt.Axis(labelAngle=0)),
            y=alt.Y(f"{measurement}:Q", title=LABELS[measurement], scale=alt.Scale(zero=False)),
            color=color,
        ).properties(height=280)
        st.altair_chart(box, alt="종별 신체 측정값의 중앙값과 분포 비교")
    st.caption("상자는 중간 50%의 분포, 상자 안 선은 중앙값입니다. 결측값은 특성별로 제외합니다.")
    summary = filtered.groupby("species").agg(
        개체수=("species", "size"), 측정수=(measurement, "count"),
        평균=(measurement, "mean"), 중앙값=(measurement, "median"),
        최솟값=(measurement, "min"), 최댓값=(measurement, "max"),
    ).round(1).reset_index().rename(columns={"species": "종"})
    st.dataframe(summary, hide_index=True, alt="종별 개체 수와 선택한 특성의 요약 통계")

st.subheader("선택한 데이터")
st.caption("측정하지 않은 값은 빈칸으로 남깁니다. 평균은 해당 특성의 측정값이 있는 개체만 사용합니다.")
st.dataframe(filtered.rename(columns=LABELS), hide_index=True, alt="현재 필터에 해당하는 펭귄 데이터")
st.download_button(
    "선택한 데이터 CSV 다운로드",
    data=filtered.rename(columns=LABELS).to_csv(index=False).encode("utf-8-sig"),
    file_name="penguins_filtered.csv", mime="text/csv", icon=":material/download:",
)
st.caption("데이터: Palmer Penguins · seaborn의 penguins 데이터셋 (344개 관측값). 로컬에 저장된 원본을 사용합니다.")
