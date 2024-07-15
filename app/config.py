class Config:
    SECRET_KEY = 'secret-key'
    DATA_CONNECT_URL = 'http://localhost:8089/'
    CATALOG = 'hive'
    SCHEMA = 'biomart'
    FILTERS = ['biotype', 'region_name']
