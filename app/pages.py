from flask import Blueprint, render_template, request, redirect, url_for
import ast

from app.query import DataConnectConnection, BuildSQLQuery
from app.forms import TableForm, ColumnForm, FilterForm

app = Blueprint("pages", __name__)

def data_connect_query(table_type, production_name, cols):
    """ Query table gene, transcript or translation for given species and columns """
    ## Build SQL statement
    q = BuildSQLQuery(table=table_type, cols=cols)
    table = q.table
    q = q.build_base_query().where(table.species == production_name)
    stmt = q.get_sql()
    ## Get results iterator -- format is {'column_name' : 'value'} for each row
    table_data_iterator = DataConnectConnection().query(stmt)
    return table_data_iterator

@app.route('/', methods=['GET', 'POST'])
def home():
    """" Select table and species """
    form = TableForm()
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

    form = ColumnForm()
    ## Fill form choices
    form.columns.choices = DataConnectConnection().info(table_name=table_type)
    if form.validate_on_submit():
        cols = form.columns.data
        for i in cols:
            if i == 'biotype':
                return redirect(url_for('pages.generate_filter', table=table_type, filter_col=i, cols=cols, species=species))
        table_data_iterator = data_connect_query(table_type=table_type,
                                                production_name=species,
                                                cols=cols)
        return render_template("pages/data.html", cols=cols, data=table_data_iterator)
    return render_template('pages/select_column.html', form=form)

def create_labels(data_iterator):
    li = []
    for element in data_iterator:
        for val in element.values():
            li.append((element.copy(), val))
    return li

@app.route("/filters", methods=['GET', 'POST'])
def generate_filter():
    """ Create filters """
    table_type = request.args.get('table')
    filter_col = request.args.getlist('filter_col')
    species = request.args.get('species')
    cols = request.args.getlist('cols')

    form = FilterForm()
    ## Fill form choices
    stmt = BuildSQLQuery(table=table_type, cols=filter_col, filters=[{"species": species}], distinct=True).build_base_query()
    results = DataConnectConnection().query(stmt.get_sql())
    form.filter.choices = create_labels(results)

    if form.validate_on_submit():
        filters = [ast.literal_eval(x) for x in form.filter.data]
        filters.append({"species": species})
        stmt = BuildSQLQuery(table=table_type, cols=cols, filters=filters).build_base_query()
        results = DataConnectConnection().query(stmt.get_sql())
        return render_template("pages/data.html", cols=cols, data=results)

    return render_template('pages/select_filter.html', form=form)