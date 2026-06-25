# -*- coding: utf-8 -*-
"""
movies.csv 만들기 (재현/확장용)
TMDB 공개 데이터셋(약 1만 편, 1960~2015 · CC0 계열)을 내려받아
여러 장르를 한글로 바꾸고 줄거리·평점·TMDB id 등을 정리해 movies.csv 로 저장합니다.
실행:  python prepare_data.py
"""
import pandas as pd

SRC = "https://raw.githubusercontent.com/yinghaoz1/tmdb-movie-dataset-analysis/master/tmdb-movies.csv"

df = pd.read_csv(SRC)
df = df.dropna(subset=["original_title", "genres", "overview", "vote_average"]).copy()

# 영어 TMDB 장르 → 한글
G = {
    "Action": "액션", "Adventure": "모험", "Science Fiction": "SF", "Thriller": "스릴러",
    "Fantasy": "판타지", "Crime": "범죄", "Drama": "드라마", "Comedy": "코미디",
    "Romance": "로맨스", "Family": "가족", "Animation": "애니메이션", "Horror": "공포",
    "Mystery": "미스터리", "War": "전쟁", "History": "역사", "Music": "음악",
    "Documentary": "다큐", "Western": "서부극", "TV Movie": "TV영화", "Foreign": "외국어",
}
EMOJI = {
    "액션": "💥", "모험": "🧭", "SF": "🚀", "스릴러": "😱", "판타지": "🐉", "범죄": "🕵️",
    "드라마": "🎭", "코미디": "😂", "로맨스": "💕", "가족": "👨‍👩‍👧", "애니메이션": "🎨",
    "공포": "👻", "미스터리": "🔍", "전쟁": "🎖️", "역사": "🏛️", "음악": "🎸",
    "다큐": "🎥", "서부극": "🤠", "TV영화": "📺", "외국어": "🌐",
}

def to_kr_genres(s):
    out = []
    for g in str(s).split("|"):
        if g in G and G[g] not in out:
            out.append(G[g])
    return ",".join(out)

df["장르들"] = df["genres"].apply(to_kr_genres)
df = df[df["장르들"] != ""]
df["대표장르"] = df["장르들"].apply(lambda s: s.split(",")[0])
df["이모지"] = df["대표장르"].map(EMOJI)
df["감독"] = df["director"].fillna("-").apply(lambda s: str(s).split("|")[0])
df["runtime"] = df["runtime"].replace(0, df["runtime"].median()).fillna(df["runtime"].median()).astype(int)

out = (df[["original_title", "release_year", "vote_average", "vote_count", "runtime",
           "감독", "overview", "장르들", "대표장르", "이모지", "id"]]
       .rename(columns={"original_title": "제목", "release_year": "연도", "vote_average": "평점",
                        "vote_count": "투표수", "runtime": "러닝타임", "overview": "줄거리",
                        "id": "tmdb_id"})
       .sort_values("투표수", ascending=False)
       .reset_index(drop=True))
out.to_csv("movies.csv", index=False, encoding="utf-8-sig")
print(f"movies.csv 저장: {len(out):,}편")
