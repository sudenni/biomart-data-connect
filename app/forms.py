from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired

class TableForm(FlaskForm):
    table = SelectField('Select table', 
                        validators=[DataRequired()], 
                        choices=[('gene', 'Gene'), ('transcript', 'Transcript'), ('translation', 'Translation')])
    species = SelectField('Select species',
                          validate_choice=[DataRequired()],
                          choices = ['bos_taurus', 'homo_sapiens', 'mus_musculus'])
    submit = SubmitField('Query table')