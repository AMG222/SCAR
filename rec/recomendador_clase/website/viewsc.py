from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import User, Note, Movie, UserType, Rating
from .Recomendador import convert_genre
from .auth import tostring, mean
from . import db
import json
from urllib.request import urlopen
from .Recomendador import recomendC, quickSort
import math
neighbor_max=50
rat_min = 0.7
viewsc = Blueprint('viewsc', __name__)
def only_five(pref):
    a = [0.0]*18
    col_pref = pref
    for t in range(0,5):
        value = max(col_pref)
        index_val = col_pref.index(value)
        a[index_val] = value
        col_pref[index_val] = 0
    return a
@viewsc.route('/colaborative', methods=['GET', 'POST'])
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
                col_g = current_user.number_col_g.split(',')[:-1]
                for gen in genres.split(', '):
                    g = convert_genre(gen.replace(',',''))
                    print("preferences. " + str(col_pref[g]))
                    print("number. " + str(col_pref_num[g]))
                    preferences[g] = (float(preferences[g])*int(numbers[g]) + 100*float(rate)/5.0) / (int(numbers[g])+1)
                    col_pref[g] = (float(col_pref[g])*int(col_pref_num[g]) + 100*float(rate)/5.0) / (int(col_pref_num[g])+1)
                    numbers[g] = int(numbers[g]) + 1
                    col_pref_num[g] = int(col_pref_num[g]) + 1
                    col_g[g] = int(col_g[g]) + 1
                current_user.demographic_preferences = tostring(preferences)
                UserType.query.get(current_user.type).preferences = tostring(preferences)
                UserType.query.get(current_user.type).number = tostring(numbers)
                current_user.number_col_g=tostring(col_g)
                current_user.colaborative_preferences=tostring(col_pref)
                db.session.commit()
        elif button != None and button == 'recalculate':
            for user in User.query:
                if user.id%1000==0:
                    print("lleva +1000")
                r = 0.0
                pera=[]
                auxx = user.colaborative_preferences.split(',')[:-1]
                col_prefx = [float(x) for x in auxx]
                col_prefx = only_five(col_prefx)
                x = mean(col_prefx)
                print(current_user.age)
                pe=[]
                ra=[]
                sx = 0
                for j in range(0,18):
                    sx+=col_prefx[j]*col_prefx[j]
                sx = math.sqrt(sx/18 - x*x)
                if sx != 0:
                    aux = range(1, 6041)
                    for j in aux:
                        if j!=user.id:
                            userj = User.query.get(j)
                            auxy = userj.colaborative_preferences.split(',')[:-1]
                            col_prefy = [float(y) for y in auxy]
                            col_prefy = only_five(col_prefy)
                            y = mean(col_prefy)
                            sy = 0
                            for k in range(0,18):
                                sy+=col_prefy[k]*col_prefy[k]
                            sy = math.sqrt(sy/18 - y*y)
                            if sy != 0:
                                for k in range(0,18):
                                    r += ((col_prefy[k]-y)/sy)*((col_prefx[k]-x)/sx)
                                r = r/17
                            pe.append(j)
                            ra.append(r)
                            pera.append([r,j])
                else:
                    for j in range(0,18):
                        pera.append([0.0, j])
                aux = []
                aux2 = []
                quickSort(ra, pe, 0, len(ra)-1)
                for j in range(0,len(ra)):
                    if len(aux) > neighbor_max:
                        break
                    if ra[j] >= rat_min:
                        aux.append(ra[j])
                        aux2.append(pe[j])
                user.neighbor_number = len(aux)
                user.ids_neighbors=tostring(aux2)
                user.neighbors_affinity=tostring(aux)
            db.session.commit()
                        
    if current_user.neighbor_number == 0:
        r = 0.0
        pera=[]
        pe=[]
        ra=[]
        auxx = current_user.colaborative_preferences.split(',')[:-1]
        col_prefx = [float(x) for x in auxx]
        col_prefx = only_five(col_prefx)
        x = mean(col_prefx)
        sx = 0
        for j in range(0,18):
            sx+=col_prefx[j]*col_prefx[j]
        sx = math.sqrt(sx/18 - x*x)
        if sx != 0:
            aux = range(1, 6041)
            for j in aux:
                if j!=current_user.id:
                    userj = User.query.get(j)
                    auxy = userj.colaborative_preferences.split(',')[:-1]
                    col_prefy = [float(y) for y in auxy]
                    col_prefy = only_five(col_prefy)
                    y = mean(col_prefy)
                    sy = 0
                    for k in range(0,18):
                        sy+=col_prefy[k]*col_prefy[k]
                    sy = math.sqrt(sy/18 - y*y)
                    if sy != 0:
                        for k in range(0,18):
                            r += ((col_prefy[k]-y)/sy)*((col_prefx[k]-x)/sx)
                        r = r/17
                    pe.append(j)
                    ra.append(r)
                    pera.append([r,j])
        else:
            for j in range(0,18):
                pera.append([0.0, j])
        aux = []
        aux2 = []
        quickSort(pe, ra, 0, len(pera)-1)
        for j in range(0,len(ra)):
            if len(aux) > neighbor_max:
                break
            if ra[j] >= rat_min:
                aux.append(ra[j])
                aux2.append(pe[j])
        user = User.query.get(current_user.id)
        user.neighbor_number = len(aux)
        user.ids_neighbors=tostring(aux2)
        user.neighbors_affinity=tostring(aux)
        db.session.commit()

    url1 = "https://api.themoviedb.org/3/movie/"
    url2 = "?api_key=5f27af8c07807d6305034ceafad8581a"
    movies = []
    films, ratios = recomendC(10, current_user)
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
