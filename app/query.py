from pypika import PostgreSQLQuery, Criterion
from search_python_client.search import SearchClient
from flask import current_app as app

from app.table import Gene, Transcript, Translation

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
    def __init__(self, table, cols, filters = None, limit = None, distinct = False) -> None:
        catalog = app.config["CATALOG"]
        schema = app.config["SCHEMA"]
        if table == 'gene':
            t = Gene
        elif table == 'transcript':
            t = Transcript
        else:
            t = Translation
        self.table = t(schema=(catalog, schema))
        if isinstance(cols, str):
            self.cols = [cols]
        else:
            self.cols = cols
        if isinstance(filters, str):
            self.filters = [filters]
        self.filters = filters
        self.limit = limit
        self.distinct = distinct

    ## Build SQL statement
    def build_base_query(self):
        """ Create SQL statement """
        query = PostgreSQLQuery.from_(self.table).select(*(self.table[col] for col in self.cols))
        ## Add WHERE
        if self.filters is not None:
            for f in self.filters:
                query = self.add_filter(f, query)
        ## Add LIMIT
        if self.limit is not None:
            query = query.limit(self.limit)
        ## Add DISTINCT
        if self.distinct:
            query = query.distinct()
        return query

    def add_filter(self, f, query):
        """ Add WHERE to query """
        t = self.table
        ## filter is a list of dictionary
        conds = []
        for element in f:
            for key, value in element.items():
                condition_field = getattr(t, key)
                conds.append(condition_field == value)
        ## WHERE OR
        condition = Criterion.any(conds)
        return query.where(condition)