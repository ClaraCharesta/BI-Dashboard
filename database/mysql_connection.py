from sqlalchemy import create_engine

def get_engine():
    engine = create_engine("mysql+pymysql://root:@localhost/bi_kematian")
    return engine