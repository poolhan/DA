import pandas as pd
import pymysql
import numpy as np

# CSV 파일 읽기, 베스트셀러와 일반도서 각각의 클렌징 데이터 파일을 읽어옴. 해당 부분만 바꿔서 코드 실행.
df = pd.read_csv(Best_cleansing_data_file.csv')

# DB 연결
conn = pymysql.connect(
    host='',
    user='',
    password='',
    database='',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

# 2. 필요한 컬럼만 선택 (area는 없고 size만 있음)
df = df[['isbn', 'price', 'pageCount', 'size', 'weight', 'book_url']]

# 타입 변환 (NaN은 고려 안함함)
df['isbn'] = pd.to_numeric(df['isbn'], errors='coerce')
df['price'] = pd.to_numeric(df['price'], errors='coerce')
df['pageCount'] = pd.to_numeric(df['pageCount'], errors='coerce')
df['size'] = pd.to_numeric(df['size'], errors='coerce')
df['weight'] = pd.to_numeric(df['weight'], errors='coerce')
df['book_url'] = df['book_url'].astype(str).str[:1000]

df = df.replace({np.nan: None})


# 6. INSERT 쿼리 
insert_query = """
    INSERT INTO BooklistInfo (isbn, price, pageCount, size, weight, book_url)
    VALUES (%s, %s, %s, %s, %s, %s)
"""

# 6. 실행
with conn:
    with conn.cursor() as cursor:
        cursor.executemany(insert_query, df.values.tolist())
    conn.commit()


print(f" {len(df)}건의 데이터가 BestlistInfo 테이블에 삽입되었습니다.")