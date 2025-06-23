import pandas as pd

# CSV 파일 불러오기
df = pd.read_csv('df_raw_with_keywords.csv')

# ISBN 컬럼에서 중복된 값 찾기
duplicated_isbn = df[df.duplicated(subset='isbn', keep=False)]

# 중복된 ISBN 고유 목록
unique_duplicated = duplicated_isbn['isbn'].dropna().astype(str).unique()

# 결과 출력
print(f"중복된 ISBN 개수: {len(unique_duplicated)}")
print("중복된 ISBN 목록:")
for isbn in unique_duplicated:
    print(isbn)