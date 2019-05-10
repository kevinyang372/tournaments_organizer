from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Length
# from .serve import Competitor

class RegistrationForm(FlaskForm):
    name = StringField('Username', validators=[Length(min=1, max=25)])
    submit = SubmitField("Register")

    # def validate_username(self, username):
    #     user = Competitor.query.filter_by(name=username.data).first()
    #     if user:
    #         raise ValidationError('That name is taken. Please choose a different one.')