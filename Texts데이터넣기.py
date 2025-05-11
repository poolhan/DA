import pandas as pd
import pymysql
import numpy as np

# CSV 파일 읽기, BestTexts나 BookTexts 해당 부분만 변경하여 실행.
df = pd.read_csv('Best_cleansing_data_file.csv')

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
df = df[['isbn', 'bookDescription', 'bookExcerpt']]

# 3. 타입 변환
df['isbn'] = pd.to_numeric(df['isbn'], errors='coerce')

#  4. NaN → None 먼저
df = df.replace({np.nan: None})

#  5. 문자열 변환 (None은 그대로 유지)
df['bookDescription'] = df['bookDescription'].apply(lambda x: str(x) if x is not None else None)
df['bookExcerpt'] = df['bookExcerpt'].apply(lambda x: str(x) if x is not None else None)

# 6. INSERT 쿼리
insert_query = """
    INSERT INTO BestTexts (isbn, bookDescription, bookExcerpt)
    VALUES (%s, %s, %s)
"""

# 7. 실행
with conn:
    with conn.cursor() as cursor:
        cursor.executemany(insert_query, df.values.tolist())
    conn.commit()

print(f" {len(df)}건의 데이터가 BookTexts 테이블에 삽입되었습니다.")