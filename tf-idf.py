import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA

# 파일 로드
df_raw = pd.read_parquet("df_raw_with_keywords.parquet")

# 사용자 정의 불용어 필터링
try:
    with open("custom_stopwords.txt", "r") as f:
        stopwords = set(line.strip() for line in f if line.strip())
    df_raw["keywords"] = df_raw["keywords"].apply(
        lambda tokens: [t for t in tokens.split() if t not in stopwords]
    )
    df_raw["keywords"] = df_raw["keywords"].apply(lambda tokens: " ".join(tokens))
    print(f"🧹 사용자 정의 불용어 {len(stopwords)}개 적용 완료")
except FileNotFoundError:
    print("⚠️ custom_stopwords.txt 파일이 없어 불용어 제거를 건너뜁니다.")

# TF-IDF 벡터화
print("📌 향상된 TF-IDF 점수 계산 중...")
tfidf = TfidfVectorizer(min_df=10, max_df=0.7)
X = tfidf.fit_transform(df_raw["keywords"])
print("TF-IDF 행렬:", X.shape)

# TF-IDF 행렬 저장
feature_names = tfidf.get_feature_names_out()
df_tfidf = pd.DataFrame(X.toarray(), columns=feature_names)
df_tfidf["isbn"] = df_raw["isbn"].values
df_tfidf.to_parquet("book_tfidf_vectors.parquet", index=False)
print("✅ 저장 완료: book_tfidf_vectors.parquet")

# PCA 적용
pca = PCA(n_components=0.95, random_state=42)
X_pca = pca.fit_transform(X.toarray())
print("선택된 주성분 수:", pca.n_components_)
print("설명 분산 비율:", pca.explained_variance_ratio_)

# DataFrame 변환 및 ISBN 포함
df_pca = pd.DataFrame(X_pca, columns=[f"PC{i+1}" for i in range(pca.n_components_)])
df_pca["isbn"] = df_raw["isbn"].values

# 저장
df_pca.to_parquet("book_keywords_pca.parquet", index=False)
print("✅ 저장 완료: book_keywords_pca.parquet")