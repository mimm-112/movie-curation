# 🎬 오늘 뭐 볼까? — 영화 큐레이션 앱

분위기를 고르면 어울리는 장르를 추천해 주고, 그 장르에서 **포스터·줄거리와 함께** 영화를 큐레이션해 주는 Streamlit 웹앱입니다.
약 1만 편(1960~2015)의 영화 데이터를 기반으로 동작합니다.

---

## ✨ 주요 기능

- **분위기 기반 추천** — 힐링 / 신나는 / 긴장감 / 먹먹함 / 로맨틱 / 강렬함 / 몽환적 / 여운 중 하나를 고르면, 어울리는 장르를 추천하고 그 장르의 영화를 골라줍니다.
- **여러 장르 매칭** — 영화 한 편의 여러 장르를 함께 고려하고, 분위기의 '핵심 장르'에 가중치를 줘서 더 정확하게 추천합니다.
- **포스터 + 줄거리 표시** — 각 추천 영화의 포스터(TMDB)와 줄거리를 함께 보여줍니다.
- **장르 직접 선택** 모드, **인기순 / 평점순** 정렬, 최소 평점·연도·편수 조절
- **찜 목록** — 마음에 드는 영화 저장/관리 (`session_state`)
- **데이터 둘러보기** — 장르별 분포, 평점 분포 차트, 제목 검색

---

## 🧩 사용한 기능 (수업 완성 체크리스트)

| 항목 | 구현 내용 |
|---|---|
| 위젯 2개 이상 | `radio` · `selectbox` · `slider`(3) · `multiselect` · `text_input` · `button` |
| 레이아웃 1개 이상 | `sidebar` + `tabs`(3개) + `columns` |
| session_state | 추천 결과 · 찜 목록 · 추천 설명 기억 |
| 이모지 · 색 꾸미기 | 장르별 이모지, 장르 칩, 포스터 카드, `balloons` · `toast` |
| 오류 없이 끝까지 | 빈 결과 / 장르 0개 / 포스터 실패 방어, 위젯별 고유 `key` |

---

## 🗂️ 파일 구성

```
streamlit_curating/
├── app.py                       # 메인 앱 (실행 파일)
├── movies.csv                   # 영화 데이터 (app.py와 같은 폴더에 있어야 함)
├── requirements.txt             # 배포용 라이브러리 목록
├── prepare_data.py              # movies.csv 재생성용 (선택)
├── test_app.py                  # 동작 검증용 (선택)
└── .streamlit/
    └── secrets.toml.example     # TMDB API 키 설정 예시 (포스터용)
```

> 배포 시 꼭 필요한 파일: `app.py` · `movies.csv` · `requirements.txt`
> (포스터를 쓰려면 아래 'TMDB API 키' 설정 추가)

---

## 🖼️ 포스터 보기 (TMDB API 키 · 무료, 선택)

포스터 이미지는 TMDB에서 실시간으로 불러옵니다. **키가 없어도 앱은 정상 작동**하며, 이 경우 포스터 자리에 이모지가 표시됩니다.

1. [themoviedb.org](https://www.themoviedb.org) 가입 → 설정 → API → **API Key (v3 auth)** 발급 (무료)
2. **로컬에서 쓸 때**: `.streamlit/secrets.toml.example` 을 복사해 `.streamlit/secrets.toml` 로 이름을 바꾸고 키를 붙여넣기
   ```toml
   TMDB_API_KEY = "발급받은_키"
   ```
3. **배포에서 쓸 때(Streamlit Cloud)**: 앱 대시보드 → **Settings → Secrets** 에 같은 줄을 붙여넣기
4. ⚠️ `secrets.toml` 은 GitHub에 올리지 마세요 (이미 `.gitignore`에 포함되어 있습니다).

---

## 📊 데이터 출처

- **원본 데이터셋**: The Movie Database(**TMDB**) 기반 공개 영화 메타데이터 약 1만 편 (1960~2015)
- **수집처(다운로드)**: [yinghaoz1/tmdb-movie-dataset-analysis](https://github.com/yinghaoz1/tmdb-movie-dataset-analysis) (GitHub, `tmdb-movies.csv`)
  - 이 데이터는 TMDB에서 수집되었으며, Udacity 데이터 분석 과정에서도 널리 쓰이는 공개 데이터셋입니다.
- **포함 정보**: 제목 · 여러 장르 · 줄거리(overview) · 평점(vote_average) · 투표수 · 감독 · 러닝타임 · TMDB id 등
- **포스터 이미지**: TMDB API를 통해 실시간 제공

### 가공 내용 (이 프로젝트에서 직접 수행)
- 영어 장르(파이프 구분) → 한글 라벨 변환 (예: `Science Fiction` → `SF`)
- 장르별 이모지 추가, 필요한 컬럼만 선택, 투표수 기준 정렬
- 전체 과정은 `prepare_data.py`에 재현 가능하게 작성됨

### 📌 라이선스 / 출처 표기
이 앱은 **TMDB API를 사용**하지만 TMDB가 보증하거나 인증한 서비스는 아닙니다.
> This product uses the TMDB API but is not endorsed or certified by TMDB.

출처 *"TMDB 기반 공개 영화 데이터셋 · 포스터 © TMDB"* 
줄거리(overview)는 영어로 제공됩니다.

---

## 🚀 실행 방법 (로컬)

```bash
cd streamlit_curating
pip install -r requirements.txt
streamlit run app.py
```

브라우저에서 자동으로 열리며, 보통 `http://localhost:8501` 에서 확인할 수 있습니다.

---

## ☁️ 배포 방법 (Streamlit Community Cloud)

1. `app.py` · `movies.csv` · `requirements.txt` 를 GitHub 저장소에 업로드
2. [share.streamlit.io](https://share.streamlit.io) 접속 → GitHub 연결
3. 저장소와 메인 파일(`app.py`)을 지정하고 **Deploy**
4. (포스터를 쓸 경우) **Settings → Secrets** 에 `TMDB_API_KEY` 추가
5. 생성된 URL을 친구에게 공유 🎉

---

## 🛠️ 기술 스택

- **Python** · **Streamlit**(웹앱) · **pandas**(데이터) · **requests**(TMDB API 호출)

(`requirements.txt`: `streamlit==1.58.0`, `pandas==3.0.2`, `requests==2.33.1`)

---

## 📝 만든 사람

Asia AI 부트캠프 미니 프로젝트 · Streamlit 분석/큐레이션 트랙
