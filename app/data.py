from pypika import PostgreSQLQuery
from search_python_client.search import SearchClient

from flask import current_app as app

class DataConnectConnection():
    def __init__(self) -> None:
        self.base_url = app.config["DATA_CONNECT_URL"]
        self.search_client = SearchClient(base_url=self.base_url)

    def query(self, stmt):
        table_data_iterator = self.search_client.search_table(stmt)
        return table_data_iterator

class BuildSQLQuery():
    def __init__(self, table, cols) -> None:
        catalog = app.config["CATALOG"]
        schema = app.config["SCHEMA"]
        self.table = table(schema=(catalog, schema))
        self.cols = cols
    
    def build_base_query(self):
        query = PostgreSQLQuery.from_(self.table).select(*(self.table[col] for col in self.cols))
        return query
