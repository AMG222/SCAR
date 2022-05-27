from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import User, Note, Movie, UserType, Rating
from . import db
import json
from .Recomendador import recomendD, convert_genre
from urllib.request import urlopen
viewsd = Blueprint('viewsd', __name__)
def tostring(l):
    aux = ""
    for p in l:
        aux+=str(p)+','
    return aux
@viewsd.route('/demographic', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        search = request.form.get("search")
        if search != '':
            url1 = "https://api.themoviedb.org/3/movie/"
            url2 = "?api_key=5f27af8c07807d6305034ceafad8581a"
            search
            print(search)
            movies = []
            res = []
            for movie in Movie.query:
                if search.lower() in movie.title.lower(): 
                    res.append(Movie.query.filter_by(title=movie.title).first())
            print(res)
            for movie in res:
                aux = []
                aux.append(movie.title)
                if movie.link == 0:
                    aux.append("https://icon-library.com/images/movie-icon-png/movie-icon-png-2.jpg")
                    aux.append("No description")
                else:
                    response = urlopen(url1 + str(movie.link) + url2)
                    string = response.read().decode('utf-8')
                    json_obj = json.loads(string)
                    if json_obj['poster_path'] == None:
                        aux.append("https://icon-library.com/images/movie-icon-png/movie-icon-png-2.jpg")
                    else:
                        aux.append("https://image.tmdb.org/t/p/w500" + json_obj['poster_path'])
                    if json_obj['overview'] == None:
                        aux.append("No description")
                    else:
                        aux.append(json_obj['overview'])
                gen = ""
                for i in movie.genres.split('|'):
                    gen+=i + ', '
                aux.append(gen[:-2])
                aux.append(movie.id)
                movies.append(aux)
            print(movies)
            bloque=[]
            for i in range(0,len(movies)):
                bloque.append("rates-" + str(i))
            bloque2=[]
            for i in range(0,len(movies)):
                bloque2.append("genres" + str(i))
            bloque3=[]
            for i in range(0,len(movies)):
                bloque3.append("movie_id" + str(i))
            return render_template("search.html", user=current_user, movies = movies, block=bloque, block2=bloque2, block3=bloque3, size=len(movies))
        
        button = request.form.get("button")
        if button != None and button[0:4] == 'rate':
            id = request.form["movie_id"+button[-1]]
            print(id)
            rate = request.form.get(button)
            if rate == None:
                rate = 0
            print(rate)
            genres = request.form["genres"+button[-1]]
            print(genres)
            if id not in current_user.viewed_movies.split(',')[:-1]:
                current_user.number_viewed += 1
                current_user.viewed_movies += id + ','
                preferences = UserType.query.get(current_user.type).preferences.split(',')[:-1]
                numbers = UserType.query.get(current_user.type).number.split(',')[:-1]
                col_pref = current_user.colaborative_preferences.split(',')[:-1]
                col_pref_num = current_user.number_col_g.split(',')[:-1]
                for gen in genres.split(', '):
                    g = convert_genre(gen.replace(',',''))
                    preferences[g] = (float(preferences[g])*int(numbers[g]) + 100*float(rate)/5.0) / (int(numbers[g])+1)
                    col_pref[g] = (float(col_pref[g])*int(col_pref_num[g]) + 100*float(rate)/5.0) / (int(col_pref_num[g])+1)
                    numbers[g] = int(numbers[g]) + 1
                    col_pref_num[g] = int(col_pref_num[g]) + 1
                current_user.demographic_preferences = tostring(preferences)
                UserType.query.get(current_user.type).preferences = tostring(preferences)
                UserType.query.get(current_user.type).number = tostring(numbers)
                db.session.commit()
        elif button != None and button == 'recalculate':
            for user in User.query:
                user.demographic_preferences = UserType.query.get(user.type).preferences
            db.session.commit()
    url1 = "https://api.themoviedb.org/3/movie/"
    url2 = "?api_key=5f27af8c07807d6305034ceafad8581a"
    movies = []
    films, ratios = recomendD(10, Movie.query, current_user)
    x=0
    for movie in films:
        aux = []
        aux.append(movie.title)
        if movie.link == 0:
            aux.append("https://icon-library.com/images/movie-icon-png/movie-icon-png-2.jpg")
            aux.append("No description")
        else:
            response = urlopen(url1 + str(movie.link) + url2)
            string = response.read().decode('utf-8')
            json_obj = json.loads(string)
            if json_obj['poster_path'] == None:
                aux.append("https://icon-library.com/images/movie-icon-png/movie-icon-png-2.jpg")
            else:
                aux.append("https://image.tmdb.org/t/p/w500" + json_obj['poster_path'])
            if json_obj['overview'] == None:
                aux.append("No description")
            else:
                aux.append(json_obj['overview'])
        gen = ""
        for i in movie.genres.split('|'):
            gen+=i + ', '
        aux.append(gen[:-2])
        aux.append(movie.id)
        aux.append(ratios[x])
        movies.append(aux)
        x+=1
    block=[]
    for i in range(0,len(movies)):
        block.append("rates-" + str(i))
    block2=[]
    for i in range(0,len(movies)):
        block2.append("genres" + str(i))
        block3=[]
    for i in range(0,len(movies)):
        block3.append("movie_id" + str(i))
    return render_template("home.html", user=current_user, movies = movies, block=block, block2=block2, block3=block3, size=len(movies))
