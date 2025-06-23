import pandas as pd

# Parquet 파일 불러오기
df = pd.read_parquet('cotard_keywords_lda_vectors.parquet')

# CSV 파일로 저장
df.to_csv('cotard_keywords_lda_vectors.csv', index=False, encoding='utf-8-sig')