import pandas as pd
import re
from sqlalchemy import create_engine

# 1. DB 접속 정보 설정
user = ''
password = ''
host = ''
port = 
source_db = ''

engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{source_db}')
engine_target = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{target_db}')

# 2. SQL 쿼리
query_bestsellers = "SELECT DISTINCT b.author_url,a.author FROM DA.Bestraw as a join DA.bestsellers as b on a.author=b.author ;"
query_book = "SELECT DISTINCT b.author_url,a.author FROM DA.Bookraw as a join DA.book as b on a.author=b.author ;" 

# 3. 데이터 로드
df_best = pd.read_sql(query_bestsellers, engine)
df_book = pd.read_sql(query_book, engine)

# 4. 정제 함수 (슬래시 기준 첫 번째만 추출)
def extract_first_author(author_str):
    if pd.isna(author_str):
        return None
    author_str = author_str.strip()
    
    # "외 3", "외3명", "외 3인" 등 공동저자 패턴 제거
    author_str = re.split(r'\s*외\s*\d+[명인]?\s*', author_str)[0].strip()
    
    # 슬래시(/) 또는 쉼표(,) 기준 첫 번째 이름 추출
    for delimiter in ['/', ',']:
        if delimiter in author_str:
            author_str = author_str.split(delimiter)[0].strip()
    
    return author_str

def extract_first_url(url_str):
    if pd.isna(url_str):
        return None
    urls = [u for u in url_str.split('https://') if u.strip()]
    return 'https://' + urls[0].strip() if urls else None

# 5. 정제 적용
def clean_dataframe(df):
    df_clean = pd.DataFrame()
    df_clean['author_name'] = df['author'].apply(extract_first_author)
    df_clean['author_url'] = df['author_url'].apply(extract_first_url)
    return df_clean

df1_clean = clean_dataframe(df_best)
df2_clean = clean_dataframe(df_book)

# 6. 병합 후 중복 제거
df_all = pd.concat([df1_clean, df2_clean], ignore_index=True)
df_all['author_name'] = df_all['author_name'].astype(str).str.strip()
df_all['author_url'] = df_all['author_url'].astype(str).str.strip().str.rstrip('/')
df_all = df_all.dropna(subset=['author_name', 'author_url'])  # NaN 제거
df_all = df_all.drop_duplicates(subset=['author_name', 'author_url']).reset_index(drop=True)

# 7. author_id 부여
df_all.insert(0, 'author_id', df_all.index + 1)

# 8. 테이블에 INSERT (if_exists='replace'로 덮어쓰기 또는 'append'로 추가 가능)
df_all.to_sql(
    name='Authors',
    con=engine_target,
    if_exists='replace',  # 또는 'append'
    index=False,
    dtype={
        'author_id': 'INT',
        'author_name': 'VARCHAR(255)',
        'author_url': 'VARCHAR(500)'
    }
)

print("finalDB.Authors 테이블에 데이터 INSERT 완료.")