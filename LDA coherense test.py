import pandas as pd
from gensim.corpora import Dictionary
from gensim.models import LdaModel, CoherenceModel

# 전처리된 데이터 로드 및 불용어 적용
df_raw = pd.read_parquet("df_raw_with_keywords.parquet")
df_raw["tokens"] = df_raw["keywords"].str.split()

try:
    with open("custom_stopwords.txt", "r") as f:
        stopwords = set(line.strip() for line in f if line.strip())
    df_raw["tokens"] = df_raw["tokens"].apply(lambda tokens: [t for t in tokens if t not in stopwords])
except FileNotFoundError:
    print("⚠️ custom_stopwords.txt 파일이 없어 불용어 제거를 건너뜁니다.")

# 그리드 탐색 파라미터
min_dfs = [2, 5, 10]
max_dfs = [0.5, 0.7, 0.9]
k_values = [5, 7, 10, 15, 20]
results = []

def main():
    for min_df in min_dfs:
        for max_df in max_dfs:
            dictionary = Dictionary(df_raw["tokens"])
            dictionary.filter_extremes(no_below=min_df, no_above=max_df)
            corpus = [dictionary.doc2bow(tokens) for tokens in df_raw["tokens"]]
            if len(dictionary) < 10:
                continue

            for k in k_values:
                lda_model = LdaModel(corpus=corpus, id2word=dictionary, num_topics=k, passes=10, random_state=42)
                cm = CoherenceModel(model=lda_model, texts=df_raw["tokens"], dictionary=dictionary, coherence='c_v')
                coherence = cm.get_coherence()
                results.append((min_df, max_df, k, coherence))
                print(f"✔️ min_df={min_df}, max_df={max_df}, k={k}, coherence={coherence:.4f}")

    # 결과 저장
    df_result = pd.DataFrame(results, columns=["min_df", "max_df", "k", "coherence"])
    df_result.to_csv("coherence_gridsearch_results.csv", index=False)
    print("✅ 결과 저장 완료: coherence_gridsearch_results.csv")


if __name__ == "__main__":
    main()