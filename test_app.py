# -*- coding: utf-8 -*-
"""AppTest: 포스터(키 없을 때 폴백)·줄거리·멀티장르 추천이 오류 없이 도는지 검증"""
from streamlit.testing.v1 import AppTest

print("== 1. 초기 로딩 ==")
at = AppTest.from_file("app.py", default_timeout=40).run()
assert not at.exception, f"초기 예외: {at.exception}"
print("   예외 없음 ✅ / 탭", len(at.tabs), "/ 메트릭", [m.value for m in at.metric])

print("\n== 2. 분위기(로맨틱) + 평점순 추천 ==")
at.selectbox("sb_mood").set_value("로맨틱").run()
at.selectbox("sb_sort").set_value("평점순").run()
[b for b in at.button if "추천 받기" in b.label][0].click().run()
assert not at.exception, f"추천 예외: {at.exception}"
fav_btns = [b for b in at.button if b.key and b.key.startswith("fav_")]
print("   추천 카드 수:", len(fav_btns), "(포스터는 키 없어 이모지 폴백)")
assert len(fav_btns) > 0

print("\n== 3. 찜 → 메트릭 즉시 갱신 ==")
fav_btns[0].click().run()
assert not at.exception
m = [x for x in at.metric if "찜" in x.label][0]
print("   찜 후:", m.value); assert m.value == "1편"

print("\n== 4. 장르 직접 + 검색 ==")
at2 = AppTest.from_file("app.py", default_timeout=40).run()
at2.radio("rd_mode").set_value("🎬 장르 직접 고르기").run()
at2.multiselect("ms_genre").set_value(["SF", "판타지"]).run()
[b for b in at2.button if "추천 받기" in b.label][0].click().run()
assert not at2.exception
at2.text_input("ti_search").set_value("matrix").run()
assert not at2.exception
print("   장르모드·검색 OK ✅")

print("\n== 5. 빈 결과/장르 0개 방어 ==")
at3 = AppTest.from_file("app.py", default_timeout=40).run()
at3.radio("rd_mode").set_value("🎬 장르 직접 고르기").run()
at3.multiselect("ms_genre").set_value([]).run()
[b for b in at3.button if "추천 받기" in b.label][0].click().run()
assert not at3.exception
print("   장르 0개 방어 OK ✅ / warning:", [w.value for w in at3.sidebar.warning])

print("\n🎉 모든 검증 통과!")
