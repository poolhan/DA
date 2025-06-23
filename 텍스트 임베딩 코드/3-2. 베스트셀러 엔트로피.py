import pandas as pd
import numpy as np

# CSV 파일 경로 (필요 시 경로 수정)
csv_path = "general_gensim_lda_vectors.csv"

# 데이터 불러오기
df = pd.read_csv(csv_path)

# 토픽 열들만 추출
topic_columns = [col for col in df.columns if col.startswith("topic_")]

# 엔트로피 계산 함수 정의
def calculate_entropy(row):
    probs = row[topic_columns].astype(float).values
    probs = probs[probs > 0]  # log(0) 방지
    return -np.sum(probs * np.log2(probs))

# 각 문서에 대해 엔트로피 계산
df["entropy"] = df.apply(calculate_entropy, axis=1)

# 결과 저장 (선택사항)
df.to_csv("book_with_entropy.csv", index=False)

# 결과 미리보기
print(df[["isbn", "entropy"]].head())

# 엔트로피 평균 계산
mean_entropy = df["entropy"].mean()

# 결과 출력
print(f"📊 베스트셀러 평균 엔트로피: {mean_entropy:.4f}")