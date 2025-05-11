import pandas as pd
import pymysql
import numpy as np

# CSV 파일 읽기, BestReviewStats나 BookReviewStats 각각에 해당하는 부분만 바꿔서 삽입.
df = pd.read_csv('/Best_cleansing_data_file.csv')

# DB 연결
conn = pymysql.connect(
    host='',
    user='',
    password='',
    database='',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

# 2. 필요한 컬럼만 선택
df = df[['isbn', 'rating', 'shortReviewCount', 'fullReviewCount', 'records']]

# 3. 타입 변환 (NaN 유지)
df['isbn'] = pd.to_numeric(df['isbn'], errors='coerce')
df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
df['shortReviewCount'] = pd.to_numeric(df['shortReviewCount'], errors='coerce')
df['fullReviewCount'] = pd.to_numeric(df['fullReviewCount'], errors='coerce')
df['records'] = df['records'].astype(str).str[:1000]  

df = df.replace({np.nan: None})


# 6. INSERT 쿼리
insert_query = """
    INSERT INTO BestReviewStats (isbn, rating, shortReviewCount, fullReviewCount, records)
    VALUES (%s, %s, %s, %s, %s)
"""

# 7. 실행
with conn:
    with conn.cursor() as cursor:
        cursor.executemany(insert_query, df.values.tolist())
    conn.commit()

print(f" {len(df)}건의 데이터가 BestReviewStats 테이블에 삽입되었습니다.")