from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer
# 📘 Gensim 기반 LDA 모델링
import pandas as pd

# 데이터 로드
df_raw = pd.read_parquet("mecab keyword.parquet")

from gensim.corpora import Dictionary
from gensim.models.ldamodel import LdaModel



# 키워드를 토큰 리스트로 변환
df_raw["keywords"] = df_raw["keywords"].str.split()

#
# 🔍 최적의 k값(토픽 수)을 찾으려면 coherence score 또는 perplexity 기반 반복 실험이 필요함
# 예: 여러 k값에 대해 coherence score를 비교하고 가장 높은 k 선택




# 사용자 지정 불용어 자동 적용
try:
    with open("custom_stopwords.txt", "r") as f:
        custom_stopwords = set(line.strip() for line in f if line.strip())
    df_raw["keywords"] = df_raw["keywords"].apply(lambda tokens: [t for t in tokens if t not in custom_stopwords])
    print(f"🧹 사용자 정의 불용어 {len(custom_stopwords)}개 적용 완료")
except FileNotFoundError:
    print("⚠️ custom_stopwords.txt 파일이 없어 불용어 제거를 건너뜁니다.")

# Dictionary 및 Corpus 생성
dictionary = Dictionary(df_raw["keywords"].tolist())
# 문서 수 기준 단어 필터링: 너무 드물거나 흔한 단어 제거
dictionary.filter_extremes(no_below=5, no_above=0.7)
corpus = [dictionary.doc2bow(tokens) for tokens in df_raw["keywords"]]

lda_gensim = LdaModel(
    corpus=corpus,
    id2word=dictionary,
    num_topics=6,  # 사용할 토픽 수
    random_state=42,
    passes=20,
    iterations=400,
    alpha='auto',  # 문서별 토픽 분포 동적 최적화
    eta=0.01       # 토픽별 단어 집중도 조절
)

# === 각 문서의 토픽 분포 벡터 추출 ===
topic_dist = [lda_gensim.get_document_topics(doc, minimum_probability=0.0) for doc in corpus]
topic_vectors = []
for dist in topic_dist:
    vec = [0.0] * lda_gensim.num_topics
    for topic_id, prob in dist:
        vec[topic_id] = prob
    topic_vectors.append(vec)

# === 빈도 + 분산 기반 불용어 후보 추출 (리스트 출력용) ===
import numpy as np
from collections import Counter

all_tokens = [token for tokens in df_raw["keywords"] for token in tokens]
token_counts = Counter(all_tokens)
token_freq_df = pd.DataFrame(token_counts.items(), columns=["token", "frequency"])

topic_columns = [f"topic_{i}" for i in range(lda_gensim.num_topics)]
topic_array = np.array(topic_vectors)
vocab = list(token_freq_df["token"])

token_topic_dist = {token: [0]*lda_gensim.num_topics for token in vocab}
for doc_idx, tokens in enumerate(df_raw["keywords"]):
    for token in tokens:
        if token in token_topic_dist:
            for t_idx, val in enumerate(topic_array[doc_idx]):
                token_topic_dist[token][t_idx] += val

topic_dist_df = pd.DataFrame.from_dict(token_topic_dist, orient="index", columns=topic_columns)
topic_dist_df = topic_dist_df.div(topic_dist_df.sum(axis=1), axis=0).fillna(0)
topic_dist_df["std_dev"] = topic_dist_df.std(axis=1)
topic_dist_df["token"] = topic_dist_df.index

token_stats_df = pd.merge(token_freq_df, topic_dist_df[["token", "std_dev"]], on="token")
freq_thresh = token_stats_df["frequency"].quantile(0.9)
std_thresh = token_stats_df["std_dev"].quantile(0.4)

token_stats_df["type"] = "보류"
token_stats_df.loc[(token_stats_df["frequency"] >= freq_thresh) & (token_stats_df["std_dev"] <= std_thresh), "type"] = "주제어 후보"
token_stats_df.loc[(token_stats_df["frequency"] >= freq_thresh) & (token_stats_df["std_dev"] > std_thresh), "type"] = "불용어 후보"

print("\n📋 분산+빈도 기반 불용어 후보:")
for word in token_stats_df[token_stats_df["type"] == "불용어 후보"]["token"].tolist():
    print(f"- {word}")




# 토픽별 주요 단어 출력
print("\n📌 Gensim LDA 주요 토픽:")
for i, topic in lda_gensim.print_topics(num_words=10):
    print(f"Topic {i}: {topic}")

# --- Save top‑20 keywords per topic to CSV ---
import csv
csv_path = "topic_top20_keywords.csv"
with open(csv_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["topic_id", "top20_keywords"])
    for t in range(lda_gensim.num_topics):
        words = [w for w, _ in lda_gensim.show_topic(t, topn=100)]
        writer.writerow([t, " ".join(words)])
print(f"📁 토픽별 상위 20개 키워드 저장 완료: {csv_path}")

# 각 토픽별 대표 문서 3개씩 출력
print("\n📌 토픽별 대표 문서:")
import numpy as np

topic_dist = [lda_gensim.get_document_topics(doc, minimum_probability=0.0) for doc in corpus]
topic_vectors = []
for dist in topic_dist:
    vec = [0.0] * lda_gensim.num_topics
    for topic_id, prob in dist:
        vec[topic_id] = prob
    topic_vectors.append(vec)

topic_doc_map = {i: [] for i in range(lda_gensim.num_topics)}

# 📊 각 토픽에 속한 문서 수 확인
topic_doc_count = [0] * lda_gensim.num_topics
for vec in topic_vectors:
    dominant_topic = np.argmax(vec)
    topic_doc_count[dominant_topic] += 1
print("\n📊 각 토픽에 속한 문서 수:")
for topic_id, count in enumerate(topic_doc_count):
    print(f"Topic {topic_id}: {count}개 문서")

for doc_idx, doc in enumerate(topic_vectors):
    dominant_topic = np.argmax(doc)
    topic_doc_map[dominant_topic].append((doc_idx, doc[dominant_topic]))


# 📁 토픽별 대표 문서 저장
with open("topic_representative_docs.txt", "w", encoding="utf-8") as f:
    for topic_id, doc_scores in topic_doc_map.items():
        f.write(f"\n🔷 Topic {topic_id + 1} 대표 문서:\n")
        import random
        top_docs = sorted(doc_scores, key=lambda x: x[1], reverse=True)[:15]
        for doc_idx, score in top_docs:
            isbn = df_raw.iloc[doc_idx]['isbn']
            f.write(f"- ISBN {isbn} (score: {score:.4f})\n")
            f.write(f"  → 토큰: {' '.join(df_raw.iloc[doc_idx]['keywords'])}\n")
print("📁 토픽별 대표 문서 저장 완료: topic_representative_docs.txt")

# 📁 토픽별 대표 ISBN만 저장
with open("topic_representative_isbns.txt", "w", encoding="utf-8") as f:
    for topic_id, doc_scores in topic_doc_map.items():
        f.write(f"Topic {topic_id + 1}:\n")
        top_docs = sorted(doc_scores, key=lambda x: x[1], reverse=True)[:15]
        for doc_idx, _ in top_docs:
            isbn = df_raw.iloc[doc_idx]['isbn']
            f.write(f"{isbn}\n")
print("📁 토픽별 대표 ISBN 저장 완료: topic_representative_isbns.txt")


# 📊 pyLDAvis 기반 LDA 시각화 및 HTML 저장
if __name__ == "__main__":
    import pyLDAvis.gensim_models
    import pyLDAvis

    print("📊 pyLDAvis 시각화 HTML 생성 중...")
    vis = pyLDAvis.gensim_models.prepare(lda_gensim, corpus, dictionary)

    # 토픽 번호를 0부터 시작하도록 pyLDAvis 내부 데이터 수정
    vis_data = vis.to_dict()
    vis_data["mdsDat"]["topics"] = [i - 1 for i in vis_data["mdsDat"]["topics"]]
    vis_data["mdsDat"]["names"] = [str(i) for i in range(len(vis_data["mdsDat"]["topics"]))]
    vis = pyLDAvis.PreparedData(
        mds_df=vis_data["mdsDat"],
        tinfo=vis_data["tinfo"],
        token_table=vis_data["token.table"],
        R=vis_data["R"]
    )
    pyLDAvis.save_html(vis, 'lda_gensim_vis.html')
    print("✅ 시각화 저장 완료: lda_gensim_vis.html (브라우저에서 열어보세요)")



# 📁 Gensim LDA 벡터 저장
df_vectors = pd.DataFrame(topic_vectors, columns=[f"topic_{i}" for i in range(lda_gensim.num_topics)])
df_vectors["isbn"] = df_raw["isbn"].values
df_vectors.to_parquet("book_gensim_lda_vectors.parquet", index=False)
print("✅ Gensim LDA 벡터 저장 완료: book_gensim_lda_vectors.parquet")

# 📁 불용어 후보 저장
stopword_candidates = token_stats_df[token_stats_df["type"] == "불용어 후보"]["token"].tolist()
with open("stopword_candidates.txt", "w", encoding="utf-8") as f:
    for word in stopword_candidates:
        f.write(f"{word}\n")
print("📁 불용어 후보 저장 완료: stopword_candidates.txt")

# 🔒 학습된 베스트셀러 LDA 모델과 사전 저장
lda_gensim.save("bestseller_lda.model")
dictionary.save("bestseller_dictionary.dict")
print("✅ LDA 모델과 Dictionary 저장 완료: bestseller_lda.model, bestseller_dictionary.dict")


