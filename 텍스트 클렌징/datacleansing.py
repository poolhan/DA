import pandas as pd
import re
from sqlalchemy import create_engine

# 1. DB 연결 설정
user = ''
password = ''
host = ''
port = ''
database = ''

engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")

# 2. 원시 데이터 불러오기
df_best = pd.read_sql('SELECT * FROM Bestraw', con=engine)
df_book = pd.read_sql('SELECT * FROM Bookraw', con=engine)

# 3. 공통 cleansing 함수 정의

def clean_author(author_str):
    if pd.isnull(author_str): return None
    return str(author_str).split(',')[0].strip()

def clean_price(price_str):
    try:
        if '→' in price_str:
            price_str = price_str.split('→')[0].strip()
        return int(str(price_str).replace('원', '').replace(',', '').strip())
    except:
        return None

def clean_size(size_str):  # ← 기존 'extract_area'를 size 컬럼에 직접 적용
    if pd.isna(size_str):
        return None
    try:
        size_clean = re.sub(r'\(.*?\)', '', str(size_str))
        size_clean = size_clean.replace('mm', '').strip()
        width_str, height_str = size_clean.split('*')
        width = int(width_str.strip())
        height = int(height_str.strip())
        return width * height
    except:
        return None

def clean_weight(weight_str):
    if pd.isnull(weight_str): return None
    return int(str(weight_str).replace('g', '').strip())

def clean_record(record_str):
    try:
        if pd.isna(record_str):
            return None
        return record_str.split('Sales Point')[0].strip('|').strip()
    except:
        return None

def clean_description(text):
    if pd.isnull(text): return None
    cleaned = str(text).replace('\n', ' ').replace('+', ' ')
    return ' '.join(cleaned.split())

def clean_excerpt(text):
    try:
        if pd.isnull(text):
            return None
        # 영어 페이지 표기 제거
        text = re.sub(r'\(?[Pp]\.?\s?\d+([\-~]\d+)?\)?', '', text)
        # 한글 페이지 범위 제거 ("50~60쪽", "122-125쪽")
        text = re.sub(r'\d+[~\-]\d+쪽', '', text)
        # 한글 단일 페이지 제거 ("128쪽")
        text = re.sub(r'\d+쪽', '', text)
        # "P. 「작품명」 중에서" 제거
        text = re.sub(r'[Pp]\.?\s*[「『].*?[」』]\s*중에서', '', text)
        # 부가 정보 제거
        text = re.sub(r'접기|\.{2,}중|\[.*?\]', '', text)
        # 닉네임/서명 제거
        text = re.sub(r'-\s*[가-힣\w]+', '', text)
        # 공백 정리
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    except:
        return None

# 4. Cleansing 적용
def apply_cleansing(df):
    df['author'] = df['author'].apply(clean_author)
    df['price'] = df['price'].apply(clean_price)
    df['size'] = df['size'].apply(clean_size)               # ← 바로 size 덮어쓰기
    df['weight'] = df['weight'].apply(clean_weight)
    df['records'] = df['records'].apply(clean_record)
    df['bookDescription'] = df['bookDescription'].apply(clean_description)
    df['bookExcerpt'] = df['bookExcerpt'].apply(clean_excerpt)
    return df

df_best_clean = apply_cleansing(df_best.copy())
df_book_clean = apply_cleansing(df_book.copy())

# 5. CSV 파일로 저장
df_best_clean.to_csv('Best_cleansing_data_file.csv', index=False, encoding='utf-8-sig')
df_book_clean.to_csv('Book_cleansing_data_file.csv', index=False, encoding='utf-8-sig')
