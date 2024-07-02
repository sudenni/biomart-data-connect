from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired

class TableForm(FlaskForm):
    table = SelectField('Table',
                        validators=[DataRequired()],
                        choices=[('gene', 'Gene'), ('transcript', 'Transcript'), ('translation', 'Translation')])

    species = SelectField('Species',
                          validate_choice=[DataRequired()],
                          choices = ['bos_taurus', 'homo_sapiens', 'mus_musculus'])

    submit = SubmitField('Query table')

class ColumnForm(FlaskForm):
    columns = SelectMultipleField('Select columns', validators=[DataRequired()],
                          choices = [])

    submit = SubmitField('Query table')
