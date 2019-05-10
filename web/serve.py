from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from .forms import RegistrationForm
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
db = SQLAlchemy(app)


class Competitor(db.Model):
    __tablename__ = 'competitor'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    status = db.Column(db.String(5))

class Round(db.Model):
    __tablename__ = 'round'
    id = db.Column(db.Integer, primary_key=True)
    competitor_1 = db.Column(db.Integer, ForeignKey('competitor.id'))
    competitor_2 = db.Column(db.Integer, ForeignKey('competitor.id'))
    competitor_1_score = db.Column(db.Integer)
    competitor_2_score = db.Column(db.Integer)

db.create_all()
db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_competitors', methods=["GET", "POST"])
def add_competitors():
    competitors_num = Competitor.query.count()
    form = RegistrationForm()
    print('got it')

    if form.validate_on_submit():
        new_competitor = Competitor(name = form.name.data, status = 'in')
        db.session.add(new_competitor)
        db.session.commit()

        flash(f'Sucessfully added the competitor {form.name.data}!', 'success')
        return redirect(url_for('add_competitors'))

    return render_template('add_competitors.html', competitors_num=competitors_num, form=form)

@app.route('/')

if __name__ == '__main__':
    app.run()
