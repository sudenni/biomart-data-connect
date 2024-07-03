from pypika import PostgreSQLQuery, Criterion
from search_python_client.search import SearchClient

from flask import current_app as app

class DataConnectConnection():
    def __init__(self) -> None:
        self.base_url = app.config["DATA_CONNECT_URL"]
        self.search_client = SearchClient(base_url=self.base_url)

    def query(self, stmt):
        """ Execute SQL statement """
        table_data_iterator = self.search_client.search_table(stmt)
        return table_data_iterator

    def info(self, table_name):
        """ Retrieve column name from table """
        table = '.'.join([app.config["CATALOG"], app.config["SCHEMA"], table_name])
        table_info = self.search_client.get_table_info(table)
        d = table_info["data_model"]["properties"]
        return list(d.keys())

class BuildSQLQuery():
    def __init__(self, table, cols, filters = None, limit = 5, distinct = False) -> None:
        catalog = app.config["CATALOG"]
        schema = app.config["SCHEMA"]
        self.table = table(schema=(catalog, schema))
        self.cols = cols
        self.filters = filters
        self.limit = limit
        self.distinct = distinct

    def build_base_query(self):
        query = PostgreSQLQuery.from_(self.table).select(*(self.table[col] for col in self.cols))
        if self.filters is not None:
            query = self.add_filter(query)
        if self.limit is not None:
            query = query.limit(self.limit)
        if self.distinct:
            query = query.distinct()
        return query
    
    def add_filter(self, query):
        conds = []
        t = self.table
        for element in self.filters:
            print(element)
            for key, value in element:
                condition_field = getattr(t, key)
                conds.append(condition_field == value)
        # AND
        condition = Criterion.all([x for x in conds])
        return query.where(condition)