import pandas as pd

# Parquet 파일 불러오기
df = pd.read_parquet('book_gensim_lda_vectors.parquet')

# CSV 파일로 저장
df.to_csv('book_gensim_lda_vectors.csv', index=False, encoding='utf-8-sig')