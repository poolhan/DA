# --- LDA Inference for General Books ---
from gensim.models.ldamodel import LdaModel
from gensim.corpora import Dictionary
import pandas as pd

# Load trained LDA model and dictionary
lda_model = LdaModel.load("bestseller_lda.model")
dictionary = Dictionary.load("bestseller_dictionary.dict")

# Load general books keyword data
df_general = pd.read_parquet("mecab keyword(일반).parquet")
# 문자열일 경우 토큰 리스트로 변환
df_general['keywords'] = df_general['keywords'].apply(lambda x: x.split() if isinstance(x, str) else x)
# Create BOW representations and infer LDA topic vectors
corpus_general = [dictionary.doc2bow(keywords) for keywords in df_general['keywords']]
lda_vectors = []
for bow in corpus_general:
    topic_dist = lda_model.get_document_topics(bow, minimum_probability=0.0)
    # Ensure vector indices align with topic IDs (0 … K‑1)
    dense_vector = [0.0] * lda_model.num_topics
    for tid, prob in topic_dist:
        dense_vector[tid] = prob
    lda_vectors.append(dense_vector)


# Create DataFrame from inferred topic vectors and save the result

df_lda_vectors = pd.DataFrame(lda_vectors, columns=[f"topic_{i}" for i in range(lda_model.num_topics)])
df_lda_vectors["isbn"] = df_general["isbn"].values
# ------------------------------------------------------------------------
df_lda_vectors.to_parquet("general_gensim_lda_vectors.parquet", index=False)
print("✅ 일반도서 LDA 벡터 저장 완료: general_gensim_lda_vectors.parquet")

# --- pyLDAvis 시각화 for General Books ---
import pyLDAvis.gensim_models
import pyLDAvis
print("📊 일반도서 전체 pyLDAvis 시각화 HTML 생성 중...")
vis_general = pyLDAvis.gensim_models.prepare(lda_model, corpus_general, dictionary)
pyLDAvis.save_html(vis_general, 'general_lda_vis.html')
print("✅ 시각화 저장 완료: general_lda_vis.html (브라우저에서 확인)")

# Extract topic coordinates (x, y) from pyLDAvis output
vis_dict = pyLDAvis.prepared_data_to_dict(vis_general)
mds_data = pd.DataFrame(vis_dict['mdsDat'])
mds_data['topic'] = mds_data['Topic'].astype(int) - 1  # Topic index starts from 0

# Merge prediction and label info for highlighting
df_meta = pd.read_csv("y_pred_update.csv")  # Assumes it contains 'isbn', 'y_pred', 'label' columns
df_vectors = pd.read_parquet("general_gensim_lda_vectors.parquet")  # Contains topic vectors and isbn

# Assign each document to the most probable topic
df_vectors['dominant_topic'] = df_vectors[[col for col in df_vectors.columns if col.startswith('topic_')]].idxmax(axis=1).str.replace("topic_", "").astype(int)

df_merged = df_vectors.merge(df_meta, on="isbn", how="left")

# Count how many documents fall into each topic by label
topic_distribution = df_merged.groupby(['dominant_topic', 'label']).size().unstack(fill_value=0)
topic_distribution = topic_distribution.reset_index().rename(columns={"dominant_topic": "topic"})

# Merge counts into mds_data
mds_data = mds_data.merge(topic_distribution, on="topic", how="left")
mds_data = mds_data.fillna(0)

# Save for inspection
mds_data.to_csv("topic_coordinates_with_labels.csv", index=False)
print("📁 저장 완료: topic_coordinates_with_labels.csv (토픽 위치와 예측값 정보 포함)")

y_pred = pd.read_csv("y_pred_update.csv")
# --- CSV에 있는 ISBN으로 필터링 ---
y_pred = pd.read_csv("y_pred_update.csv")
df_filtered = df_general[df_general["isbn"].isin(y_pred["isbn"])].copy()

# --- 단어 빈도수 카운트 및 출력 ---
from collections import Counter
import itertools

all_tokens = list(itertools.chain.from_iterable(df_filtered['keywords']))
word_freq = Counter(all_tokens)

print("📊 등장 단어 수:", len(word_freq))
print("📌 상위 단어:", word_freq.most_common(10))

print(f"✅ 필터링된 ISBN 개수: {len(df_filtered)}개 시각화에 사용됩니다.")

print("📚 사용된 ISBN 목록:\n", df_filtered["isbn"].tolist())

# --- 필터링된 문서 기반 BOW 생성 (원래 dictionary 사용) ---
filtered_corpus = [dictionary.doc2bow(doc) for doc in df_filtered['keywords']]

# --- pyLDAvis 시각화 ---
import pyLDAvis.gensim_models
import pyLDAvis

print("📊 pyLDAvis 시각화 HTML 생성 중...")
vis = pyLDAvis.gensim_models.prepare(lda_model, filtered_corpus, dictionary)
pyLDAvis.save_html(vis, 'filtered_lda_vis.html')
print("✅ 시각화 저장 완료: filtered_lda_vis.html (브라우저에서 확인)")