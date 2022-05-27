from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Movie, Rating, UserType
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from os import walk
from .Recomendador import defineType,convert_age, convert_genre, convert_occupation, quickSort
import math
auth = Blueprint('auth', __name__)
#**************FIL NOIRE SALE MUY POCO PERO ESTA MUY BIEN VALORADO por tanto se recomienda mucho
def tostring(l):
    aux = ""
    for p in l:
        aux+=str(p)+','
    return aux
def mean(l):
    return sum(l)/len(l)
@auth.route('/login', methods=['GET', 'POST'])
def login():
    #Fill database
    """
    users = []
    users = [None]*6041
    movies = [None]*3953
    tipos = []
    ctipos = []
    f = open("ml-1m/users.dat", "r")
    for person in f:
        aux = [0.0]*18
        aux2 = [0.0]*18
        data = person.split("::")
        #Tipo=4, number viewed=5, viewed=6, demograficpreferences=7, colaborativepreferences=8, neighbor_number=9, ids_neighbors=10,neighbors_affinity=11
        users[int(data[0])]=[data[0], data[1], int(data[2]), int(data[3]), defineType(data[1],int(data[2]),int(data[3])), 0, "", aux, aux2, 0, [], [], []]
        new_user = User(id=int(data[0]), username="movielens"+data[0], sex=data[1], age=data[2], occupation=int(data[3]), type=defineType(data[1],int(data[2]),int(data[3])), number_viewed = 0, viewed_movies="", demographic_preferences="", 
        colaborative_preferences="",neighbor_number=0,ids_neighbors="",neighbors_affinity="", number_col_g="",
        password=generate_password_hash(
                "movielens", method='sha256'))
        db.session.add(new_user)
    db.session.commit()
    print("created user database")
    f = open("ml-1m/movies.dat", "r").readlines()
    h = open("ml-1m/links.csv", "r").readlines()
    link = {}
    for film in h:
        values = film.split(',')
        if values[2].replace('\n', '')!='':
            link[int(values[0])] = int(values[2].replace('\n', ''))
    for film in range(0,len(f)):
        data = f[film].split("::")
        movies[int(data[0])] = [data[0], data[1], data[2]]
        if int(data[0]) not in link:
            new_movie = Movie(id = int(data[0]), link = 0, title=data[1], genres=data[2])
        else:
            new_movie = Movie(id = int(data[0]), link = link[int(data[0])], title=data[1], genres=data[2])
        db.session.add(new_movie)
    db.session.commit()
    
    print("created movie database")
    for i in range(0, 17):
        tipo = [0.0]*18
        ctipo = [0]*18
        tipos.append(tipo)
        ctipos.append(ctipo)
        new_user_type = UserType(id = i, number = 0, preferences = "")
        db.session.add(new_user_type)
    db.session.commit()
    f = open("ml-1m/ratings.dat", "r")
    users_gv=[None]*6041
    for i in range(1,6041):
        aux = [0]*18
        users_gv[i]=aux
    z=0
    for valoration in f:
        data = valoration.split("::")
        users[int(data[0])][5] += 1
        users[int(data[0])][6]+=str(movies[int(data[1])][0])+','
        for gen in movies[int(data[1])][2].split('|'):
            g = convert_genre(gen.replace('\n',''))
            tipo = users[int(data[0])][4]
            if g==0 and tipo==0:
                z+=1
            tipos[tipo][g] += float(data[2])/5.0
            ctipos[tipo][g] += 1
            #Colaborative
            users[int(data[0])][8][g] += float(data[2])/5.0
            users_gv[int(data[0])][g] += 1
        #rat = Rating(username=int(data[0]), movie=int(data[1]), val=int(data[2]))
        #db.session.add(rat)
    db.session.commit()
    print("end valorations")
    tipos_a = []

    for i in range(0, 17):
        au = []
        for j in range(0,18):
            au.append(100*tipos[i][j]/ctipos[i][j])
        tipos_a.append(au)
    x=1
    for i in User.query:
        i.number_viewed = users[x][5]
        i.viewed_movies = users[x][6]
        i.demographic_preferences=tostring(tipos_a[users[x][4]])
        x+=1
    x=0
    for i in UserType.query:
        i.preferences=tostring(tipos_a[x])
        i.number=tostring(ctipos[x])
        x+=1
    db.session.commit()
    print("begin colaborative")
    #fill user colaborative prefrences only 6
    colab_preferen = []
    colab_preferen.append(None)
    for i in range(1, 6041):
        a=[0.0]*18
        for j in range(0,18):
            if users_gv[i][j] == 0:
                a[j] = 0.0
            else:
                a[j]=100*users[i][8][j]/users_gv[i][j]
        col_pref=a
        colab_preferen.append(a)
        for t in range(0,5):
            value = max(col_pref)
            index_val = col_pref.index(value)
            a[index_val] = value
            col_pref[index_val] = 0
        users[i][8] = a
    number_users_tract = 6041
    #Calculate neighbors
    neighbor_max=50
    rat_min = 0.7
    import time
    for i in range(1, number_users_tract):
        user = User.query.get(users[i][0])
        user.colaborative_preferences=tostring(colab_preferen[i])
        init = time.time()
        r = 0.0
        pear=[]
        pe=[]
        ra=[]
        col_prefx = users[i][8]
        x = mean(users[i][8])
        sx = 0
        for j in range(0,18):
            sx+=col_prefx[j]*col_prefx[j]
        sx = math.sqrt(sx/18 - x*x)
        if sx != 0:
            aux = range(1, number_users_tract)
            for j in aux:
                if j!=i:
                    col_prefy = users[j][8]
                    y = mean(users[j][8])
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
                    pear.append([r,j])
        else:
            for j in range(0,18):
                pear.append([0.0, j])
        aux = []
        aux2 = []
        quickSort(ra, pe, 0, len(ra)-1)
        for j in range(0,len(ra)):
            if len(aux) > neighbor_max:
                break
            if ra[j] >= rat_min:
                aux.append(ra[j])
                aux2.append(pe[j])
        users[i][9] = len(aux)
        users[i][10] = aux2
        users[i][11] = aux
        user.neighbor_number = users[i][9]
        user.number_col_g = tostring(users_gv[i])
        user.ids_neighbors=tostring(aux2)
        user.neighbors_affinity=tostring(aux)
    db.session.commit()
    """
    print("--------filled database--------")
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.choose'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Username does not exist.', category='error')
    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        pref=[]
        username = request.form.get('username')
        try:
            sex = request.form.get('sex')
            age = convert_age(int(request.form.get('age')))
            occupation = convert_occupation(request.form.get('occupation'))
            password1 = request.form.get('password1')
            password2 = request.form.get('password2')
        except:
            flash('Personal data not filled', category='error')
        try:
            pref = [float(request.form.get('action')), float(request.form.get('adventure')), float(request.form.get('animation')), float(request.form.get('animation')), 
            float(request.form.get('childrens')), float(request.form.get('comedy')), float(request.form.get('documentary')), float(request.form.get('drama')), 
            float(request.form.get('fantasy')), float(request.form.get('filmnoir')), float(request.form.get('horror')), float(request.form.get('musical')), 
            float(request.form.get('mystery')), float(request.form.get('romance')), float(request.form.get('scifi')), float(request.form.get('thriller')), 
            float(request.form.get('war')), float(request.form.get('western'))]
        except:
            flash('Genres preferences not filled', category='error')
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists.', category='error')
        elif len(username) < 4:
            flash('Username must be greater than 3 characters.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            if pref == []:
                flash('Genres preferences not filled', category='error')
                return render_template("sign_up.html", user=current_user)
            new_user = User(username=username, sex=sex, age=age, type=defineType(sex,age,occupation), occupation=occupation, number_viewed = 0, viewed_movies="", demographic_preferences="", 
            colaborative_preferences=tostring(pref),neighbor_number=0,ids_neighbors="",neighbors_affinity="", number_col_g="",
            password=generate_password_hash(
                password1, method='sha256'))
            type_us = UserType.query.get(new_user.type)
            new_user.demographic_preferences = type_us.preferences
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.choose'))

    return render_template("sign_up.html", user=current_user)