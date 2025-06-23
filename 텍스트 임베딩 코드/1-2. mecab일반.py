import pandas as pd
import re
import os
import pickle
from sqlalchemy import create_engine
from eunjeon import Mecab

isbn_df = pd.read_csv("data.csv")
filtered_df = isbn_df[isbn_df["label"] == 0]
isbn_list = isbn_df["isbn"].dropna().unique().tolist()
isbn_tuple = ",".join(f"'{isbn}'" for isbn in isbn_list)

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
query = f"""
SELECT isbn, bookExcerpt, 'general' as label
FROM BookTexts
WHERE isbn IN ({isbn_tuple}) 
  AND bookExcerpt IS NOT NULL
  AND isbn NOT IN (SELECT isbn FROM finalDB.BestTexts)
"""
df_raw = pd.read_sql(query, engine)
# 삭제된 ISBN 확인
df_query_result_isbn = df_raw["isbn"].unique().tolist()
removed_isbns = [isbn for isbn in isbn_list if isbn not in df_query_result_isbn]
print(f"📌 data.csv에는 있지만 쿼리 결과에 포함되지 않은 ISBN 수: {len(removed_isbns)}")
print(removed_isbns[:10])  # 상위 10개만 출력
df_raw["bookExcerpt"] = df_raw.bookExcerpt.fillna("")
df_raw["full_text"] = df_raw.bookExcerpt
df_raw["label"] = df_raw["label"].astype("category")



# 숫자만 있는 문서 제거
def is_numeric_text(text):
    return bool(re.fullmatch(r"[0-9\s\.,\-–:;]*", text.strip()))

df_raw["is_number_only"] = df_raw["full_text"].apply(is_numeric_text)
df_raw = df_raw[~df_raw["is_number_only"]]
df_raw = df_raw[df_raw["full_text"].str.len() > 10]

mecab = Mecab(dicpath="/opt/homebrew/etc/mecabrc")

# 불용어 불러오기
with open("stopwords-ko.txt", encoding="utf-8") as f:
    stopwords = set(f.read().splitlines())

# 명사 추출 함수
def extract_keywords_mecab(text):
    nouns = mecab.nouns(text)
    filtered = [word for word in nouns if len(word) > 1 and word not in stopwords]
    return " ".join(filtered) if filtered else " "

df_raw["keywords"] = df_raw["full_text"].apply(extract_keywords_mecab)

df_raw.to_parquet("mecab keyword(일반).parquet", index=False)
print("✅ 저장 완료: df_raw_with_keywords(명사).parquet")
