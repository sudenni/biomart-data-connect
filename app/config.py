class Config:
    SECRET_KEY = 'secret-key'
    DATA_CONNECT_URL = 'http://localhost:8089/'
    CATALOG = 'hive'
    SCHEMA = 'testing_partitions'
    FILTERS = ['biotype', 'region_name']
