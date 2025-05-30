import pandas as pd
import re
import os
import pickle
from sqlalchemy import create_engine
from kiwipiepy import Kiwi
from k_rake import K_RAKE

# DB 연결
DB_USER = os.getenv("DB_USER", "da")
DB_PASS = os.getenv("DB_PASS", "da1")
DB_HOST = os.getenv("DB_HOST", "134.185.117.240")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "finalDB")

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    pool_pre_ping=True,
)

# DB에서 책 데이터 로드
query = "SELECT isbn, bookExcerpt FROM BookTexts WHERE bookExcerpt IS NOT NULL;"
df_raw = pd.read_sql(query, engine)
df_raw["bookExcerpt"] = df_raw.bookExcerpt.fillna("")
df_raw["full_text"] = df_raw.bookExcerpt

# 숫자만 있는 문서 제거
def is_numeric_text(text):
    return bool(re.fullmatch(r"[0-9\s\.,\-–:;]*", text.strip()))

df_raw["is_number_only"] = df_raw["full_text"].apply(is_numeric_text)
df_raw = df_raw[~df_raw["is_number_only"]]
df_raw = df_raw[df_raw["full_text"].str.len() > 10]

# 형태소 분석기 세팅
kiwi = Kiwi(model_type='sbg')
if os.path.exists("userword"):
    with open("userword", 'rb') as f:
        userword = pickle.load(f)
        for word in userword:
            kiwi.add_user_word(word, tag='NNP', score=30)
else:
    print("⚠️ userword 파일이 존재하지 않아 사용자 단어 등록을 건너뜁니다.")

# 불용어 불러오기
with open("stopwords-ko.txt", encoding="utf-8") as f:
    stopwords = set(f.read().splitlines())

# K_RAKE 키워드 추출
keywords_per_doc = []
print("📌 K_RAKE 기반 키워드 추출 중...")
for doc in df_raw["full_text"]:
    krake = K_RAKE(stopwords=stopwords, tokenizer=kiwi)
    kwds = krake.extract_keywords([doc])
    keywords = [kw for _, kw in kwds if len(kw.split()) <= 5]
    keywords_per_doc.append(" ".join(keywords) if keywords else "빈문서")

df_raw["keywords"] = keywords_per_doc
df_raw = df_raw[df_raw["keywords"] != "빈문서"]

# 결과 저장
df_raw.to_parquet("df_raw_with_keywords.parquet", index=False)
print("✅ 저장 완료: df_raw_with_keywords.parquet")

