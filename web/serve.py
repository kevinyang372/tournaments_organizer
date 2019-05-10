from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from .forms import RegistrationForm, MatchForm
import random
import os

app = Flask(__name__)

# Initialize the application
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
db = SQLAlchemy(app)

# Define data tables
class Competitor(db.Model):
    __tablename__ = 'competitor'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    status = db.Column(db.String(5))

class Round(db.Model):
    __tablename__ = 'round'
    id = db.Column(db.Integer, primary_key=True)
    competitor_1 = db.Column(db.Integer, db.ForeignKey('competitor.id'))
    competitor_2 = db.Column(db.Integer, db.ForeignKey('competitor.id'))
    competitor_1_score = db.Column(db.Integer)
    competitor_2_score = db.Column(db.Integer)

db.create_all()
db.session.commit()

# Index page
@app.route('/')
def index():
    return render_template('index.html')

# Registering new competitors
@app.route('/add_competitors', methods=["GET", "POST"])
def add_competitors():
    competitors_num = Competitor.query.count()
    form = RegistrationForm()

    if form.validate_on_submit():
        new_competitor = Competitor(name = form.name.data, status = 'in')
        db.session.add(new_competitor)
        db.session.commit()

        flash(f'Sucessfully added the competitor {form.name.data}!', 'success')
        return redirect(url_for('add_competitors'))

    return render_template('add_competitors.html', competitors_num=competitors_num, form=form)

# Next Round
@app.route('/round')
def round():
    form = MatchForm()
    match_list = []
    
    competitors = Competitor.query.filter_by(status="in").all()

    # Shuffles the list to make the order random
    shuffled_list = [t for t in competitors]
    random.shuffle(shuffled_list)

    for i in range(len(shuffled_list)):
        if i % 2 == 0:
            match_list.append([shuffled_list[i]])
        else:
            match_list[-1].append(shuffled_list[i])

    return render_template('round.html', match_list = match_list, form = form)

# Set the match result
@app.route('/submit_match_result/<int:competitor_1>/<int:competitor_2>', methods=["POST"])
def submit_match_result(competitor_1, competitor_2):
    form = MatchForm()

    if form.validate_on_submit():
        s1 = int(form.competitor1.data)
        s2 = int(form.competitor2.data)

        new_round = Round(competitor_1 = competitor_1, competitor_2 = competitor_2, competitor_1_score = s1, competitor_2_score = s2)

        if s1 > s2:
            competitor = Competitor.query.filter_by(id = competitor_2).first()
        else:
            competitor = Competitor.query.filter_by(id = competitor_1).first()

        # Eliminate the loser
        competitor.status = "out"

        db.session.add(new_round)
        db.session.commit()

    # This needs future improvement
    return 'Successfully Logged'

# Summary Page
@app.route('/round_summary')
def round_summary():
    all_rounds = Round.query.all()

    summary = []
    for i in all_rounds:
        summary.append({'competitor_1': Competitor.query.filter_by(id = i.competitor_1).first().name, 'competitor_2': Competitor.query.filter_by(id = i.competitor_2).first().name, 'competitor_1_score': i.competitor_1_score, 'competitor_2_score': i.competitor_2_score})

    return render_template('round_summary.html', all_rounds = summary)


if __name__ == '__main__':
    app.run()
