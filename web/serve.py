from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from .forms import RegistrationForm, MatchForm, TournamentForm
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
    tournament = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    name = db.Column(db.String(200))
    status = db.Column(db.String(5))

class Round(db.Model):
    __tablename__ = 'round'
    id = db.Column(db.Integer, primary_key=True)
    competitor_1 = db.Column(db.Integer, db.ForeignKey('competitor.id'))
    competitor_2 = db.Column(db.Integer, db.ForeignKey('competitor.id'))
    tournament = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    competitor_1_score = db.Column(db.Integer)
    competitor_2_score = db.Column(db.Integer)
    round_number = db.Column(db.Integer)

class Tournament(db.Model):
    __tablename__ = 'tournament'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))

db.create_all()
db.session.commit()

# Index page
@app.route('/', methods=["GET", "POST"])
def index():
    form = TournamentForm()
    tournament = Tournament.query.all()

    if form.validate_on_submit():
        new_tournament = Tournament(name = form.name.data)
        db.session.add(new_tournament)
        db.session.commit()

        if len(tournament) == 0:
            t_id = 1
        else:
            t_id = tournament[-1].id + 1

        return redirect(url_for('add_competitors', tournament_id = t_id))

    return render_template('index.html', tournaments=tournament, form=form)

# Registering new competitors
@app.route('/add_competitors/<int:tournament_id>', methods=["GET", "POST"])
def add_competitors(tournament_id):
    competitors_num = Competitor.query.filter_by(tournament=tournament_id).count()
    form = RegistrationForm()
    matches = Round.query.filter_by(tournament = tournament_id).all()
    could_register = len(matches) == 0

    if form.validate_on_submit():
        new_competitor = Competitor(name = form.name.data, status = 'in', tournament = tournament_id)
        db.session.add(new_competitor)
        db.session.commit()

        flash(f'Sucessfully added the competitor {form.name.data}!', 'success')
        return redirect(url_for('add_competitors', tournament_id = tournament_id))

    return render_template('add_competitors.html', competitors_num=competitors_num, tournament_id = tournament_id, form=form, could_register = could_register)

# Next Round
@app.route('/round/<int:tournament_id>/<int:round_id>')
def round(tournament_id, round_id):
    form = MatchForm()
    match_list = []
    
    matches = Round.query.filter_by(tournament = tournament_id, round_number = round_id).all()
    could_do_next_round = len(matches) != 0 and len([1 for i in matches if i.competitor_1_score is None and i.competitor_2 is not None]) == 0

    if len(matches) == 0:

        competitors = Competitor.query.filter_by(status="in", tournament = tournament_id).all()

        if len(competitors) == 1:
            match_list = [competitors[0], "final"]
        else:
            # Shuffles the list to make the order random
            shuffled_list = [t for t in competitors]
            random.shuffle(shuffled_list)

            for i in range(len(shuffled_list)):
                if i % 2 == 0:
                    match_list.append([shuffled_list[i]])
                else:
                    match_list[-1].append(shuffled_list[i])
                    match_list[-1].append(True)

                    new_round = Round(competitor_1 = match_list[-1][0].id, competitor_2 = match_list[-1][1].id, round_number = round_id, tournament = tournament_id)
                    db.session.add(new_round)
                    db.session.commit()

            if len(match_list[-1]) == 1:
                new_round = Round(competitor_1 = match_list[-1][0].id, round_number = round_id, tournament = tournament_id)
                db.session.add(new_round)
                db.session.commit()
    else:
        for i in matches:
            if i.competitor_2 is not None:
                c1 = Competitor.query.filter_by(id = i.competitor_1).first()
                c2 = Competitor.query.filter_by(id = i.competitor_2).first()
                complete = i.competitor_1_score is None

                match_list.append([c1, c2, complete])
            else:
                c1 = Competitor.query.filter_by(id = i.competitor_1).first()
                match_list.append([c1])

    return render_template('round.html', tournament_id = tournament_id, round_id = round_id, match_list = match_list, form = form, could_do_next_round = could_do_next_round)

# Set the match result
@app.route('/submit_match_result/<int:tournament_id>/<int:round_id>/<int:competitor_1>/<int:competitor_2>', methods=["POST"])
def submit_match_result(tournament_id, round_id, competitor_1, competitor_2):
    form = MatchForm()

    if form.validate_on_submit():
        s1 = int(form.competitor1.data)
        s2 = int(form.competitor2.data)

        if s1 < 15 and s2 < 15:
            response = {
                'status_code': 500,
                'status': 'Wrong Score Entry. Both lower than 15.'
            }
            return jsonify(response), 500
        elif (s1 > 15 or s2 > 15) and (abs(s2 - s1) != 2):
            response = {
                'status_code': 500,
                'status': 'Wrong Score Entry.'
            }
            return jsonify(response), 500
        elif s1 == 15 and abs(s2 - s1) < 2:
            response = {
                'status_code': 500,
                'status': 'Wrong Score Entry. Match should continue.'
            }
            return jsonify(response), 500

        current_match = Round.query.filter_by(competitor_1 = competitor_1, competitor_2 = competitor_2, round_number=round_id, tournament = tournament_id).first()

        current_match.competitor_1_score = s1
        current_match.competitor_2_score = s2

        if s1 > s2:
            competitor = Competitor.query.filter_by(id = competitor_2).first()
        else:
            competitor = Competitor.query.filter_by(id = competitor_1).first()

        # Eliminate the loser
        competitor.status = "out"

        db.session.commit()

    return redirect(url_for('round', tournament_id = tournament_id, round_id = round_id))

# Summary Page
@app.route('/round_summary/<int:tournament_id>')
def round_summary(tournament_id):
    all_rounds = Round.query.filter_by(tournament = tournament_id).all()

    summary = []
    for i in all_rounds:
        if i.competitor_2 is not None:
            summary.append({'round':i.round_number, 'competitor_1': Competitor.query.filter_by(id = i.competitor_1).first().name, 'competitor_2': Competitor.query.filter_by(id = i.competitor_2).first().name, 'competitor_1_score': i.competitor_1_score, 'competitor_2_score': i.competitor_2_score})
        else:
            summary.append({'round':i.round_number, 'competitor_1': Competitor.query.filter_by(id = i.competitor_1).first().name})

    return render_template('round_summary.html', all_rounds = summary, tournament_id = tournament_id)


if __name__ == '__main__':
    app.run()
