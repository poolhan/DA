import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from itertools import product


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

results = []
param_grid = list(product([2, 5, 10, 50, 75, 100], [0.7, 0.9]))

for min_df, max_df in param_grid:
    print(f"\n🔍 TF-IDF 실험: min_df={min_df}, max_df={max_df}")
    tfidf = TfidfVectorizer(min_df=min_df, max_df=max_df)
    X = tfidf.fit_transform(df_raw["keywords"])

    if X.shape[1] < 10:
        print("⚠️ 유효한 feature 수가 적어 건너뜀:", X.shape[1])
        continue

    feature_names = tfidf.get_feature_names_out()
    df_tfidf = pd.DataFrame(X.toarray(), columns=feature_names)
    df_tfidf["isbn"] = df_raw["isbn"].values
    df_tfidf.to_parquet(f"book_tfidf_vectors_df{min_df}_max{int(max_df*100)}.parquet", index=False)

    pca = PCA(n_components=0.95, random_state=42)
    X_pca = pca.fit_transform(X.toarray())
    print("📊 주성분 수:", pca.n_components_)
    print("📈 총 설명 분산 비율:", round(sum(pca.explained_variance_ratio_), 4))

    df_pca = pd.DataFrame(X_pca, columns=[f"PC{i+1}" for i in range(pca.n_components_)])
    df_pca["isbn"] = df_raw["isbn"].values
    df_pca.to_parquet(f"book_keywords_pca_df{min_df}_max{int(max_df*100)}.parquet", index=False)

    results.append({
        "min_df": min_df,
        "max_df": max_df,
        "n_features": X.shape[1],
        "n_components": pca.n_components_,
        "explained_var": round(sum(pca.explained_variance_ratio_), 4)
    })

df_result = pd.DataFrame(results)
df_result.to_csv("tfidf_pca_experiment_results.csv", index=False)
print("\n✅ 실험 결과 저장 완료: tfidf_pca_experiment_results.csv")
