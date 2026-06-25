# -*- coding: utf-8 -*-
"""
🎬 오늘 뭐 볼까? — 분위기로 장르를 찾고, 그 장르에서 영화를 큐레이션
포스터(TMDB)·줄거리·여러 장르를 활용한 Streamlit 영화 추천 앱 (약 1만 편)
"""
import os
import streamlit as st
import pandas as pd
import requests

# ──────────────────────────────────────────────
# 1) 페이지 설정 + 꾸미기
# ──────────────────────────────────────────────
st.set_page_config(page_title="오늘 뭐 볼까?", page_icon="🎬", layout="wide")

st.markdown(
    """
    <style>
    .genre-chip { display:inline-block; background:#2d5a8c; color:#fff; border-radius:999px;
                  padding:4px 14px; margin:3px; font-size:14px; font-weight:600; }
    .poster-ph { background:linear-gradient(135deg,#1e3a5f,#2d5a8c); border-radius:12px;
                 height:210px; display:flex; align-items:center; justify-content:center;
                 font-size:64px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# 분위기 → 어울리는 장르 (맨 앞이 '핵심 장르' → 가중치 부여)
MOOD_TO_GENRES = {
    "힐링": ["가족", "애니메이션", "코미디", "음악"],
    "신나는": ["액션", "모험", "코미디", "SF"],
    "긴장감": ["스릴러", "공포", "미스터리", "범죄"],
    "먹먹함": ["드라마", "로맨스", "가족"],
    "로맨틱": ["로맨스", "코미디", "드라마"],
    "강렬함": ["범죄", "액션", "스릴러", "전쟁"],
    "몽환적": ["SF", "판타지", "애니메이션", "미스터리"],
    "여운": ["드라마", "역사", "전쟁"],
}
MOOD_EMOJI = {"힐링": "☁️", "신나는": "🎉", "긴장감": "😱", "먹먹함": "🥲",
              "로맨틱": "💕", "강렬함": "🔥", "몽환적": "🌌", "여운": "🍃"}

# ──────────────────────────────────────────────
# 2) 데이터 로딩
# ──────────────────────────────────────────────
@st.cache_data
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(base, "movies.csv"), encoding="utf-8-sig")
    df["_set"] = df["장르들"].apply(lambda s: set(str(s).split(",")))
    return df

df = load_data()

# ──────────────────────────────────────────────
# 3) 포스터 가져오기 (TMDB 무료 API · 키 없으면 자동으로 건너뜀)
# ──────────────────────────────────────────────
def _api_key():
    try:
        if "TMDB_API_KEY" in st.secrets:
            return st.secrets["TMDB_API_KEY"]
    except Exception:
        pass
    return os.environ.get("TMDB_API_KEY", "")

@st.cache_data(show_spinner=False, ttl=86400)
def get_poster_url(tmdb_id):
    key = _api_key()
    if not key or pd.isna(tmdb_id):
        return None
    try:
        r = requests.get(f"https://api.themoviedb.org/3/movie/{int(tmdb_id)}",
                         params={"api_key": key}, timeout=4)
        if r.status_code == 200:
            path = r.json().get("poster_path")
            if path:
                return f"https://image.tmdb.org/t/p/w342{path}"
    except Exception:
        pass
    return None

# ──────────────────────────────────────────────
# 4) session_state
# ──────────────────────────────────────────────
if "recommendations" not in st.session_state:
    st.session_state.recommendations = None
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "info" not in st.session_state:
    st.session_state.info = None

# ──────────────────────────────────────────────
# 5) 추천 로직 (여러 장르 매칭 + 핵심 장르 가중치)
# ──────────────────────────────────────────────
def recommend(data, target, min_score, year_range, sort_by, top_n):
    if not target:
        return []
    tset, primary = set(target), target[0]
    d = data[(data["평점"] >= min_score) &
             data["연도"].between(year_range[0], year_range[1])].copy()
    d["match"] = d["_set"].apply(lambda gs: len(gs & tset) + (2 if primary in gs else 0))
    d = d[d["match"] > 0]
    cols = ["match", "투표수"] if sort_by == "인기순" else ["match", "평점"]
    return d.sort_values(cols, ascending=False).head(top_n).index.tolist()

# ──────────────────────────────────────────────
# 6) 사이드바 = 설문
# ──────────────────────────────────────────────
st.sidebar.title("🎯 오늘의 취향 설문")

all_genres = sorted(set(g for s in df["_set"] for g in s))

mode = st.sidebar.radio("어떻게 고를까요?",
                        ["🎭 분위기로 시작", "🎬 장르 직접 고르기"], key="rd_mode")

if mode == "🎭 분위기로 시작":
    mood = st.sidebar.selectbox("오늘 원하는 분위기는?", list(MOOD_TO_GENRES.keys()),
                                format_func=lambda m: f"{MOOD_EMOJI[m]} {m}", key="sb_mood")
    target_genres = MOOD_TO_GENRES[mood]
    st.sidebar.caption(f"→ 어울리는 장르: {' · '.join(target_genres)}")
    chosen_label = f"{MOOD_EMOJI[mood]} {mood}"
else:
    target_genres = st.sidebar.multiselect("장르 선택 (여러 개 OK)", all_genres,
                                           default=["액션", "코미디"], key="ms_genre")
    chosen_label = " · ".join(target_genres) if target_genres else "(선택 없음)"

sort_by = st.sidebar.selectbox("정렬 기준", ["인기순", "평점순"], key="sb_sort")
min_score = st.sidebar.slider("최소 평점", 5.0, 9.0, 6.5, 0.1, key="sl_score")
year_range = st.sidebar.slider("개봉 연도", 1960, 2015, (1995, 2015), key="sl_year")
top_n = st.sidebar.slider("추천 편수", 3, 12, 6, key="sl_topn")

st.sidebar.divider()
go = st.sidebar.button("🍿 영화 추천 받기", type="primary")

if go:
    if not target_genres:
        st.sidebar.warning("장르를 1개 이상 골라주세요!")
    else:
        idxs = recommend(df, target_genres, min_score, year_range, sort_by, top_n)
        st.session_state.recommendations = idxs
        st.session_state.info = {"mode": mode, "label": chosen_label,
                                 "genres": target_genres, "sort": sort_by}
        if idxs:
            st.balloons()

# ──────────────────────────────────────────────
# 7) 메인 화면
# ──────────────────────────────────────────────
st.title("🎬 오늘 뭐 볼까?")
st.write("분위기를 고르면 어울리는 장르를 찾아주고, 그 장르에서 포스터·줄거리와 함께 영화를 추천해드려요.")

if target_genres:
    pool = df[df["_set"].apply(lambda gs: bool(gs & set(target_genres)))]
else:
    pool = df.iloc[0:0]
c1, c2, c3, c4 = st.columns(4)
c1.metric("전체 영화", f"{len(df):,}편")
c2.metric("선택 장르 영화", f"{len(pool):,}편")
c3.metric("평균 평점", f"{df['평점'].mean():.1f}")
c4.metric("내 찜 목록", f"{len(st.session_state.favorites)}편")

if not _api_key():
    st.caption("ℹ️ 포스터를 보려면 TMDB API 키가 필요해요(무료). 키가 없으면 이모지로 대신 표시됩니다. — README 참고")

st.divider()
tab1, tab2, tab3 = st.tabs(["🎯 오늘의 추천", "📊 데이터 둘러보기", "💖 내 찜 목록"])

# --- 탭 1: 추천 ---
with tab1:
    idxs = st.session_state.recommendations
    if idxs is None:
        st.info("👈 왼쪽에서 분위기(또는 장르)를 고르고 **'영화 추천 받기'** 를 눌러보세요!")
    elif len(idxs) == 0:
        st.warning("😢 조건에 맞는 영화가 없어요. 평점을 낮추거나 연도 범위를 넓혀보세요!")
    else:
        info = st.session_state.info
        if info["mode"] == "🎭 분위기로 시작":
            chips = "".join(f"<span class='genre-chip'>{g}</span>" for g in info["genres"])
            st.markdown(f"#### 💡 **{info['label']}** 분위기엔 이런 장르가 어울려요")
            st.markdown(chips, unsafe_allow_html=True)
            st.caption(f"그중에서 **{info['sort']}** 으로 골랐어요 🎉")
        else:
            st.success(f"**{info['label']}** 장르를 **{info['sort']}** 으로 골랐어요 🎉")
        st.write("")

        for rank, idx in enumerate(idxs, start=1):
            row = df.loc[idx]
            with st.container(border=True):
                ci, ct = st.columns([1, 4])
                with ci:
                    url = get_poster_url(row["tmdb_id"])
                    if url:
                        st.image(url)
                    else:
                        st.markdown(f"<div class='poster-ph'>{row['이모지']}</div>",
                                    unsafe_allow_html=True)
                with ct:
                    st.markdown(f"**{rank}. {row['제목']} ({row['연도']})** {row['이모지']}")
                    st.caption(f"⭐ {row['평점']} · 👍 {int(row['투표수']):,} · "
                               f"{row['장르들']} · {row['러닝타임']}분 · 감독 {row['감독']}")
                    st.write(row["줄거리"])
                    if st.button("💖 찜하기", key=f"fav_{idx}"):
                        if idx not in st.session_state.favorites:
                            st.session_state.favorites.append(idx)
                            st.toast(f"'{row['제목']}'을(를) 찜했어요!", icon="💖")
                            st.rerun()
                        else:
                            st.toast("이미 찜한 영화예요!", icon="✅")

# --- 탭 2: 데이터 둘러보기 ---
with tab2:
    st.subheader("대표 장르별 영화 수")
    st.bar_chart(df["대표장르"].value_counts())

    st.subheader("평점 분포")
    bins = pd.cut(df["평점"], bins=[0, 4, 5, 6, 7, 8, 9, 10]).value_counts().sort_index()
    bins.index = bins.index.astype(str)
    st.bar_chart(bins)

    st.subheader("영화 검색")
    q = st.text_input("제목으로 검색 (영문)", key="ti_search")
    view = df[df["제목"].str.contains(q, case=False, na=False)] if q else df
    st.caption(f"{len(view):,}편")
    st.dataframe(view[["이모지", "제목", "연도", "장르들", "평점", "투표수", "러닝타임", "감독"]].head(300),
                 hide_index=True)

# --- 탭 3: 찜 목록 ---
with tab3:
    favs = st.session_state.favorites
    if not favs:
        st.info("아직 찜한 영화가 없어요. 추천 탭에서 마음에 드는 영화를 찜해보세요 💖")
    else:
        st.write(f"총 **{len(favs)}편**을 찜했어요!")
        for idx in favs:
            row = df.loc[idx]
            ca, cb = st.columns([5, 1])
            ca.markdown(f"{row['이모지']} **{row['제목']}** ({row['연도']}) — ⭐ {row['평점']} · {row['장르들']}")
            if cb.button("삭제", key=f"del_{idx}"):
                st.session_state.favorites.remove(idx)
                st.rerun()
        st.divider()
        if st.button("🗑️ 찜 목록 비우기"):
            st.session_state.favorites = []
            st.rerun()

st.divider()
st.caption("🎬 오늘 뭐 볼까? · Streamlit 영화 큐레이션 · TMDB 데이터 약 1만 편 (1960–2015) · 포스터 © TMDB")
