# Cleanedbestsellers.csv나 Cleanedbook.csv 파일에서 isbn과 author_id를 가져와서 Bestlist의 각 isbn에 대응하는 author_id 삽입입

import pandas as pd
from sqlalchemy import create_engine

# 1. DB 연결 정보 설정
user = ''
password = ''
host = ''
port = 3306
db_name = ''

# 2. MySQL 연결 엔진 생성
engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}')

# 3. Cleanedbestsellers.csv 파일 읽기
df = pd.read_csv('Cleanedbestsellers.csv')

# 4. 데이터베이스에서 isbn 값에 해당하는 author_id 가져오기
# CSV의 isbn과 author_id 값을 사용하여 Bestlist 테이블에 업데이트

with engine.connect() as conn:
    for index, row in df.iterrows():
        isbn = row['isbn']
        author_id = row['author_id']
        
        # 5. SQL UPDATE 쿼리 작성 (isbn에 해당하는 레코드의 author_id를 업데이트)
        update_query = f"""
        UPDATE Bestlist
        SET author_id = {author_id}
        WHERE isbn = '{isbn}';
        """
        
        # 6. 쿼리 실행
        conn.execute(update_query)

print("finalDB.Bestlist 테이블에 author_id 업데이트 완료.")