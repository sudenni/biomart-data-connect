from flask_wtf import FlaskForm
from wtforms import widgets, SelectField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class TableForm(FlaskForm):
    table = SelectField('Table',
                        validators=[DataRequired()],
                        choices=[('gene', 'Gene'), ('transcript', 'Transcript'), ('translation', 'Translation')])

    species = SelectField('Species',
                          validate_choice=[DataRequired()],
                          choices = ['bos_taurus', 'homo_sapiens', 'mus_musculus'])

    submit = SubmitField('Query table')

class ColumnForm(FlaskForm):
    columns = MultiCheckboxField('Select columns', validators=[DataRequired()],
                          choices = [])

    submit = SubmitField('Query table')

class FilterForm(FlaskForm):
    filter = MultiCheckboxField('Filter',
                         validate_choice=[DataRequired()],
                         choices = [])
    submit = SubmitField('Query table')