from flask import Blueprint, render_template

from app.data import DataConnectConnection, BuildSQLQuery
from app.table import Gene, Transcript, Translation
from app.forms import TableForm

app = Blueprint("pages", __name__)

def data_connect_query(table_type, production_name, cols):
    """ Query table gene, transcript or translation for given species and columns """
    ## Get table class
    if table_type == 'gene':
        t = Gene
    elif table_type == 'transcript':
        t = Transcript
    else:
        t = Translation
    ## Build SQL statement
    q = BuildSQLQuery(table=t, cols=cols)
    table = q.table
    q = q.build_base_query().where(table.species == production_name).where(table.region_name == '1').limit(5)
    stmt = q.get_sql()
    ## Get results iterator -- format is {'column_name' : 'value'} for each row
    table_data_iterator = DataConnectConnection().query(stmt)
    return table_data_iterator

@app.route('/', methods=['GET', 'POST'])
def generate_query():
    """" Show query results for selected table and species """
    form = TableForm()

    cols = ["stable_id", "region_name","start","end"]

    if form.validate_on_submit():
        table_type = form.table.data
        species = form.species.data
        table_data_iterator = data_connect_query(table_type=table_type, production_name=species, cols=cols)
        return render_template("pages/data.html", cols=cols, data=table_data_iterator)
    return render_template('pages/selector.html', form=form)