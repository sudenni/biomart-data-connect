from flask import Blueprint, render_template, request, redirect, url_for, Response, session
from flask import current_app as app_config
import ast
import json
from collections import defaultdict

from app.query import DataConnectConnection, BuildSQLQuery
from app.forms import TableForm, ColumnForm, FilterForm, FilterTableForm

app = Blueprint("pages", __name__)

def intersect(lst1, lst2):
    """ Return intersection of lists """
    return list(set(lst1) & set(lst2))

def get_species():
    """ List of species in database """
    stmt = BuildSQLQuery(table='transcript',
                                cols='species',
                                distinct=True).build_base_query()
    results = DataConnectConnection().query(stmt.get_sql())
    li = []
    for element in results:
        for val in element.values():
            li.append(val)
    return li

@app.route('/_autocomplete', methods=['GET'])
def autocomplete():
    """ Autocompletion for species """
    species_autocomp = get_species()
    return Response(json.dumps(species_autocomp), mimetype='application/json')

@app.route('/', methods=['GET', 'POST'])
def home():
    """" Select table and species """
    form = TableForm(request.form)
    if form.validate_on_submit():
        table_type = form.table.data
        species = form.species.data
        return redirect(url_for('pages.generate_query', table=table_type, species=species))
    return render_template('pages/select_table_species.html', form=form)

@app.route("/columns", methods=['GET', 'POST'])
def generate_query():
    """ Select columns and show results """
    table_type = request.args.get('table', '')
    species = request.args.get('species', '')

    # Check if columns are already stored in session
    store_col = ''.join([table_type, '_columns'])
    if store_col in session:
        get_cols = session[store_col]
    else:
        # Execute the query once to get the columns
        get_cols = DataConnectConnection().info(table_name=table_type)
        # Store the columns in session to avoid re-querying
        session[store_col] = get_cols
    ## Fill form choices
    form = ColumnForm()
    form.columns.choices = get_cols
    
    ## Make Compara columns available when query on Gene
    if table_type == "gene":
        form.columns_compara.choices = DataConnectConnection().info(table_name="compara")
    else:
        del form.columns_compara

    if form.validate_on_submit():
        if form.columns_compara is not None:
            cols_compara_data = form.columns_compara.data
        else:
            cols_compara_data = None

        print(cols_compara_data)
        filter_col = intersect(form.columns.data, app_config.config["FILTERS"])
        return redirect(url_for('pages.generate_filter', 
                                table=table_type, 
                                filter_col=filter_col, 
                                cols=form.columns.data, 
                                cols_compara=cols_compara_data,
                                species=species))
    return render_template('pages/select_column.html', form=form)

def create_labels(data_iterator):
    """ Create list of tuple ({'column', 'value'}, 'value') for filters """
    li = []
    for element in data_iterator:
        for val in element.values():
            li.append((element, val))
    li.sort(key=lambda tup: tup[1])
    return li

@app.route("/filters", methods=['GET', 'POST'])
def generate_filter():
    """ Create filters """
    table_type = request.args.get('table')
    filter_col = request.args.getlist('filter_col')
    species = request.args.get('species', '')
    cols = request.args.getlist('cols')

    ## Compara columns
    cols_compara = request.args.getlist('cols_compara', '')

    form = FilterTableForm()
    if filter_col is None:
        del form.filter_list
    ## Fill form choices
    else:
        for col in filter_col:
            filter_for_species = f'{col}_{species}'
            if filter_for_species in session:
                get_filters = session[filter_for_species]
            else:
                stmt = BuildSQLQuery(table=table_type,
                                cols=col,
                                filters={"species" : species},
                                distinct=True).build_base_query()
                results = DataConnectConnection().query(stmt.get_sql())
                get_filters = create_labels(results)
                session[filter_for_species] = get_filters
    
            filt = FilterForm()
            form.filter_list.append_entry(filt)
            form.filter_list[-1].filter.choices = get_filters

    if form.validate_on_submit():
        ## Filter on selected values
        ## Create dict like {'column1' : ['v1', 'v2'], 'column2' : ['vA', 'vB', 'vC']}
        d = defaultdict(list)
        for item in form.filter_list:
            ## Get form filter data back as dict
            dicts = [ast.literal_eval(x) for x in item.filter.data]
            ## Key with list of values
            for dict in dicts:
                for key, value in dict.items():
                    d[key].append(value)
        ## Filter on species
        d['species'].append(species)
        ## Query
        # Join with Compara
        if cols_compara is not None:
            stmt = BuildSQLQuery(table=table_type, cols=cols, filters=d, limit=form.limit.data, cols_compara=cols_compara, species_compara=species).build_base_query()
            cols.extend(cols_compara)
        else:
            stmt = BuildSQLQuery(table=table_type, cols=cols, filters=d, limit=form.limit.data).build_base_query()
        results = DataConnectConnection().query(stmt.get_sql())

        return render_template("pages/data.html", cols=cols, data=results)
    return render_template('pages/select_filter.html', form=form, filters=filter_col)


## API
@app.route('/api/species', methods=['GET'])
def api_species():
    species = get_species()
    species.sort()
    return species

@app.route('/api/tables', methods=['GET'])
def api_tables():
    tables = DataConnectConnection().tables()
    return tables

@app.route('/api/tables/<table>', methods=['GET'])
def api_columns(table):
    columns = DataConnectConnection().info(table_name=table)
    return columns

def get_attribute(data, attribute):
    return data.get(attribute) or None

@app.route('/api/query/<table>', methods=['GET'])
def api_query(table):
    if request.is_json:
        data = request.get_json()
        columns = get_attribute(data, 'columns')
        filters = get_attribute(data, 'filters')
        limit = get_attribute(data, 'limit')

        stmt = BuildSQLQuery(table=table, cols=columns, filters=filters, limit=limit).build_base_query()
        results = DataConnectConnection().query(stmt.get_sql())

        return list(results)