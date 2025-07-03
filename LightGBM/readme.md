preprocessing.csv = 알라딘 메타데이터
사용한 데이터 셋 = preprocessing.cse + lda vector + entropy

lgbm_baseline : 결측치/이상치 확인 및 다양한 파생변수 생성
lgbm_tf : 저자/출판사 tf 컬럼 생성
lgbm_tf+lda : lda 벡터 & entropy merge

training : lr = 0.0001로 변경. 이외 파라미터는 기본값
