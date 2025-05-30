import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score

# 1. 병합된 데이터 로드
df = pd.read_csv("C:/Users/taeyo/OneDrive/바탕 화면/DA final/rf_pca_lda_merged.csv")

# 2. 제거할 텍스트형 메타데이터 컬럼 정의
drop_cols = ['isbn', 'title', 'author_name', 'publisher_name', 
             'records', 'bookDescription', 'bookExcerpt', 'publishDate']

# 3. X, y 분리
X = df.drop(columns=drop_cols, errors='ignore')
y = X.pop('label')

# ✅ 4. 학습/테스트 데이터 8:2 분할
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# 5. 모델 학습
rf = RandomForestClassifier(random_state=42)
rf.fit(X_train, y_train)

# 6. 예측 및 평가
y_pred = rf.predict(X_test)
y_proba = rf.predict_proba(X_test)[:, 1]

report = classification_report(y_test, y_pred, output_dict=True)
roc_auc = roc_auc_score(y_test, y_proba)

# 7. 결과 출력
print("✅ [8:2 분할 - 정량 + PCA + LDA 모델 성능 평가 결과]")
print(f"Accuracy  : {report['accuracy']:.4f}")
print(f"Precision : {report['1']['precision']:.4f}")
print(f"Recall    : {report['1']['recall']:.4f}")
print(f"F1-score  : {report['1']['f1-score']:.4f}")
print(f"ROC AUC   : {roc_auc:.4f}")