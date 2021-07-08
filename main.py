from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import os
from typing import Callable
# API_KEY = "27523b19af93b18ea5acc2b3aa8da4c1"
api_key = os.environ.get("API_KEY")

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
# database
class MySQL(SQLAlchemy):
    Column: Callable
    Float: Callable
    String:Callable
    Integer:Callable

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///film_list.db'
db = MySQL(app)
class Film(db.Model):
    id = db.Column(db.Integer,unique = True, primary_key = True)
    title = db.Column(db.String(100), unique = False, nullable = False)
    year = db.Column(db.Integer, unique = False, nullable = False)
    description = db.Column(db.String(300),unique = True, nullable = False)
    rating = db.Column(db.Float,unique = False, nullable = False)
    ranking = db.Column(db.Integer,unique = False, nullable = False)
    review = db.Column(db.String(600),unique = False, nullable = False)
    img_url = db.Column(db.String(100),unique = True, nullable = False)
db.create_all()

# form
class MyForm(FlaskForm):
    rating = StringField(label = "Your rating out of 10 eg: 7.5", validators = [DataRequired(message = "Cannot leave entry empty")])
    review = StringField(label = "Your Review",validators = [DataRequired(message = "Cannot leave entry empty")])
    submit = SubmitField(label = "Done")

class AddForm(FlaskForm):
    movie_name = StringField(label = 'Movie Title',validators = [DataRequired(message = 'Enter the name of the film')])
    add_button = SubmitField(label = "Add Movie")

@app.route("/")
def home():
    details = db.session.query(Film).all()
    # update
    ordered_films = Film.query.order_by(Film.rating.desc()).all()
    i = 1
    for film in ordered_films:
        film.ranking = i
        i += 1
    db.session.commit()

    # ---------
    return render_template("index.html", list = details)

@app.route("/add",methods = ['POST','GET'])
def add():
    add_movie = AddForm()
    if add_movie.validate_on_submit():
        movie_name = add_movie.movie_name.data
        return redirect(url_for('select',name = movie_name))
    return render_template("add.html",form = add_movie)

@app.route("/edit/<int:film_id>",methods = ['POST','GET'])
def edit(film_id):
    forms = MyForm()
    film_to_update = Film.query.filter_by(id = film_id).first()
    film_title = film_to_update.title

    if forms.validate_on_submit():
        new_rating = forms.rating.data
        new_review = forms.review.data
        film_to_update.review = new_review
        film_to_update.rating = new_rating
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html",form = forms, title = film_title)


@app.route("/<int:film_id>")
def delete(film_id):
    film_to_delete = Film.query.get(film_id)
    db.session.delete(film_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/select/<name>')
def select(name):
    response = requests.get (f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&language=en-US&query={name}&page=1&include_adult=true')
    data = (response.json ())['results']
    return render_template("select.html",data_list = data)

@app.route('/create/<id>')
def create(id):
    response = requests.get(f'https://api.themoviedb.org/3/movie/{id}?api_key=27523b19af93b18ea5acc2b3aa8da4c1&query')
    data = response.json()
    title = data["original_title"]
    overview = data["overview"]
    poster_path = data["poster_path"]
    year_of_release = data["release_date"][:4]
    film = Film(title = title,
                year = int(year_of_release),
                description = overview,
                rating = 1,
                ranking = id,
                review = title,
                img_url = f"https://image.tmdb.org/t/p/w500/{poster_path}")
    db.session.add(film)
    db.session.commit()
    film_info = Film.query.filter_by(title = title).first()
    new_film_id = film_info.id
    return redirect(url_for('edit',film_id = new_film_id))

if __name__ == '__main__':
    app.run(debug=True)
