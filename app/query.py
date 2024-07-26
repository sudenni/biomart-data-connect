from pypika import PostgreSQLQuery, Criterion, Table
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
    
    def tables(self):
        """ Retrieve available tables """
        tables_iterator = self.search_client.get_table_list()
        tables = list(tables_iterator)
        table_names = [t['name'].split('.')[-1] for t in tables]
        return table_names


class BuildSQLQuery():
    def __init__(self, table, cols, filters = None, limit = None, distinct = False) -> None:
        catalog = app.config["CATALOG"]
        schema = app.config["SCHEMA"]

        t = Table(table, schema=(catalog, schema))
        self.table = t
        if isinstance(cols, str):
            self.cols = [cols]
        else:
            self.cols = cols
        self.filters = filters
        self.limit = limit
        self.distinct = distinct

    ## Build SQL statement
    def build_base_query(self):
        """ Create SQL statement """
        query = PostgreSQLQuery.from_(self.table).select(*(self.table[col] for col in self.cols))
        ## Add WHERE
        if self.filters is not None:
            for i in self.filters:
                query = self.add_filter(query, i)
        ## Add LIMIT
        if self.limit is not None:
            query = query.limit(self.limit)
        ## Add DISTINCT
        if self.distinct:
            query = query.distinct()
        return query

    def add_filter(self, query, key):
        """ Add WHERE to query """
        t = self.table
        conds = []
        ## filters is a dict with values as a list
        condition_field = getattr(t, key)
        value = self.filters[key]
        if isinstance(value, str):
            conds.append(condition_field == value)
        else:
            for val in value:
                conds.append(condition_field == val)
        ## WHERE OR
        condition = Criterion.any(conds)
        return query.where(condition)