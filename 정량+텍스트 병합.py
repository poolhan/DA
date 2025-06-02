import pandas as pd

# 1. 파일 경로
rf_path = r"경로/RF전처리데이터셋.csv"
lda_path = r"경로/통합lda.csv"
save_path = r"경로/rf_lda_merged.csv"

# 2. CSV 불러오기
rf_df = pd.read_csv(rf_path)
lda_df = pd.read_csv(lda_path)

# 3. isbn 기준 병합
merged_df = pd.merge(rf_df, lda_df, on='isbn', how='inner')

# 4. 결과 저장
merged_df.to_csv(save_path, index=False)

print("✅ 병합 완료! 저장된 파일:", save_path)
