import pandas as pd
from missforest import MissForest

# 1. RAW 데이터 파일 경로
raw_file_path = r''

# 2. 최종 저장 경로
final_output_path = r''

# 3. 데이터 불러오기
df = pd.read_csv(raw_file_path)

# 4. MissForest로 'size', 'pageCount', 'weight' 결측치 처리
df_size = df[['size', 'pageCount', 'weight']]
imputer = MissForest()
df_size_imputed = imputer.fit_transform(df_size)
df_size_imputed = pd.DataFrame(df_size_imputed, columns=['size', 'pageCount', 'weight'])

# 5. 원본 데이터프레임에 size 칼럼 업데이트 (반올림 후 int형)
df['size'] = df_size_imputed['size'].round().astype(int)

# 6. publishDate 칼럼을 날짜 타입으로 변환
df['publishDate'] = pd.to_datetime(df['publishDate'], errors='coerce')

# 7. 기준 날짜 설정 및 날짜 차이 계산 (age_days 컬럼 생성)
reference_date = pd.to_datetime('2025-05-14')
df['age_days'] = (reference_date - df['publishDate']).dt.days

# 8. 최종 결과 CSV 파일로 저장
df.to_csv(final_output_path, index=False)

print("전처리 완료 및 최종 CSV 저장 완료:", final_output_path)