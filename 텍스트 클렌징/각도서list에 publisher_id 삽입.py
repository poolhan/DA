#finalDB.Bestlist나 Booklist테이블의 각 도서의 isbn에 대응하는 publisher_id(출판사 번호)를 삽입하는 코드드 

import pandas as pd
from sqlalchemy import create_engine

# 1. DB 연결 정보 설정
user = 'your_username'
password = 'your_password'
host = 'localhost'
port = 3306
source_db = ''
target_db = ''

# 2. MySQL 연결 엔진 생성
engine_source = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{source_db}')
engine_target = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{target_db}')

# 3. DA.Bestraw 테이블에서 isbn과 publisher 불러오기
query_bestraw = "SELECT isbn, publisher FROM DA.Bestraw;"
df_bestraw = pd.read_sql(query_bestraw, engine_source)

# 4. finalDB.Publishers 테이블에서 publisher_name과 publisher_id 불러오기
query_publishers = "SELECT publisher_id, publisher_name FROM finalDB.Publishers;"
df_publishers = pd.read_sql(query_publishers, engine_target)

# 5. publisher_name을 기준으로 publisher_id를 찾아서 isbn에 대응하는 publisher_id 부여
df_bestraw['publisher_id'] = df_bestraw['publisher'].map(df_publishers.set_index('publisher_name')['publisher_id'])

# 6. MySQL의 finalDB.Bestlist 테이블에 publisher_id 삽입
with engine_target.connect() as conn:
    for index, row in df_bestraw.iterrows():
        isbn = row['isbn']
        publisher_id = row['publisher_id']
        
        # 7. SQL UPDATE 쿼리 작성 (isbn에 해당하는 레코드의 publisher_id를 업데이트)
        update_query = f"""
        UPDATE finalDB.Bestlist
        SET publisher_id = {publisher_id}
        WHERE isbn = '{isbn}';
        """
        
        # 8. 쿼리 실행
        conn.execute(update_query)

print("finalDB.Bestlist 테이블에 publisher_id 업데이트 완료.")