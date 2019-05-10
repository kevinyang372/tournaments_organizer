from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import Length

class RegistrationForm(FlaskForm):
    name = StringField('Username', validators=[Length(min=1, max=25)])
    submit = SubmitField("Register")

class MatchForm(FlaskForm):
    competitor1 = IntegerField('Competitor One\'s Score')
    competitor2 = IntegerField('Competitor Two\'s Score')
    submit = SubmitField("Send Score")