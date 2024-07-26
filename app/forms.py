from flask_wtf import FlaskForm, Form
from wtforms import widgets, SelectField, SelectMultipleField, SubmitField, IntegerField, FieldList, FormField, StringField
from wtforms.validators import DataRequired, Optional

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class TableForm(FlaskForm):
    table = SelectField('Table',
                        validators=[DataRequired()],
                        choices=[('gene', 'Gene'), 
                                 ('transcript', 'Transcript'), 
                                 ('translation', 'Translation'),
                                 ('compara', 'Compara')])

    species = StringField('Species',
                          validators=[DataRequired()],
                          id='species_autocomplete')

    submit = SubmitField('Query table')

class ColumnForm(FlaskForm):
    columns = MultiCheckboxField('Select columns', validators=[DataRequired()],
                          choices = [])

    submit = SubmitField('Query table')

class FilterForm(Form):
    filter = MultiCheckboxField('Filter',
                                validate_choice=False,
                         validators=[Optional()],
                         choices = [], coerce=str)

class FilterTableForm(FlaskForm):
    filter_list = FieldList(FormField(FilterForm))
    limit = IntegerField('Limit', validators=[Optional()], default=5)
    submit = SubmitField('Query table')