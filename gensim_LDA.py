# 📘 Gensim 기반 LDA 모델링
import pandas as pd

# 데이터 로드
df_raw = pd.read_parquet("df_raw_with_keywords.parquet")

from gensim.corpora import Dictionary
from gensim.models.ldamodel import LdaModel


# 키워드를 토큰 리스트로 변환
df_raw["keywords"] = df_raw["keywords"].str.split()


from collections import Counter

# 상위 200개 자주 등장하는 단어 출력 (수동 불용어 필터링 참고용)
all_tokens = [token for tokens in df_raw["keywords"] for token in tokens]
token_counts = Counter(all_tokens)
top_200_tokens = token_counts.most_common(200)

print("\n📌 상위 200개 자주 등장 단어:")
for word, count in top_200_tokens:
    print(f"{word}: {count}")

# 상위 고빈도 단어 저장 (수동 편집 후 불용어 적용)
with open("top200_frequent_words.txt", "w") as f:
    for word, count in top_200_tokens:
        f.write(f"{word}\n")

print("📁 top200_frequent_words.txt 저장 완료 (불용어로 쓸 단어 수동 편집 후 custom_stopwords.txt로 저장하세요)")

# custom_stopwords.txt가 이미 존재하지 않을 경우에만 생성
import os
if not os.path.exists("custom_stopwords.txt"):
    with open("custom_stopwords.txt", "w") as f:
        for word, _ in top_200_tokens:
            f.write(f"{word}\n")
    print("📁 custom_stopwords.txt 초기 생성 완료 (불용어 수정 가능)")
else:
    print("📁 custom_stopwords.txt가 이미 존재하므로 덮어쓰지 않습니다.")

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
dictionary.filter_extremes(no_below=10, no_above=0.7)
corpus = [dictionary.doc2bow(tokens) for tokens in df_raw["keywords"]]

#
# 🔍 최적의 k값(토픽 수)을 찾으려면 coherence score 또는 perplexity 기반 반복 실험이 필요함
# 예: 여러 k값에 대해 coherence score를 비교하고 가장 높은 k 선택

lda_gensim = LdaModel(
    corpus=corpus,
    id2word=dictionary,
    num_topics=5,
    random_state=42,
    passes=20,
    iterations=400,
    alpha='auto',  # 문서별 토픽 분포 동적 최적화
    eta=0.05       # 토픽별 단어 집중도 조절
)

# 토픽별 주요 단어 출력
print("\n📌 Gensim LDA 주요 토픽:")
for i, topic in lda_gensim.print_topics(num_words=10):
    print(f"Topic {i}: {topic}")

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
for doc_idx, doc in enumerate(topic_vectors):
    dominant_topic = np.argmax(doc)
    topic_doc_map[dominant_topic].append((doc_idx, doc[dominant_topic]))


# 📁 토픽별 대표 문서 저장
with open("topic_representative_docs.txt", "w", encoding="utf-8") as f:
    for topic_id, doc_scores in topic_doc_map.items():
        f.write(f"\n🔷 Topic {topic_id} 대표 문서:\n")
        for doc_idx, score in sorted(doc_scores, key=lambda x: -x[1])[:3]:
            f.write(f"- 문서 {doc_idx} (score: {score:.4f})\n")
            f.write(f"  → 토큰: {' '.join(df_raw.iloc[doc_idx]['keywords'])}\n")
print("📁 토픽별 대표 문서 저장 완료: topic_representative_docs.txt")


# 📊 pyLDAvis 기반 LDA 시각화 및 HTML 저장
if __name__ == "__main__":
    import pyLDAvis.gensim_models
    import pyLDAvis

    print("📊 pyLDAvis 시각화 HTML 생성 중...")
    vis = pyLDAvis.gensim_models.prepare(lda_gensim, corpus, dictionary)
    pyLDAvis.save_html(vis, 'lda_gensim_vis.html')
    print("✅ 시각화 저장 완료: lda_gensim_vis.html (브라우저에서 열어보세요)")


# 📁 Gensim LDA 벡터 저장

df_vectors = pd.DataFrame(topic_vectors, columns=[f"topic_{i}" for i in range(lda_gensim.num_topics)])
df_vectors["isbn"] = df_raw["isbn"].values
df_vectors.to_parquet("book_gensim_lda_vectors.parquet", index=False)
print("✅ Gensim LDA 벡터 저장 완료: book_gensim_lda_vectors.parquet")
