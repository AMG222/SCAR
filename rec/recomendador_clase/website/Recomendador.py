NUM_GEN = 18
NUM_USERS = 6040
NUM_MOVIES = 3952
from .models import User, Movie
import random
def defineType(sex, age, occupation):
    if age == 1 and sex == 'F':
        return 0 #type girl kid
    elif age == 1 and sex == 'M':
        return 1 #type boy kid
    elif (age == 18 or age == 25) and (occupation == 1 or occupation == 4):
        return 2 #young academic/student
    elif occupation == 1 or occupation == 4:
        return 3 #old academic
    elif (age == 18 or age == 25 or age == 35) and (occupation == 2 or occupation == 14 or occupation == 20):
        return 4 #young artist
    elif occupation == 2 or  occupation == 14 or occupation == 20:
        return 5 #old artist
    elif occupation == 3 or occupation == 7 or occupation == 16:
        return 6 #bussines man
    elif occupation == 17 or occupation == 18:
        return 7 #work man
    elif occupation == 6 or occupation == 15:
        return 8 #science man
    elif occupation == 0 or occupation == 19:
        return 9 #not know
    elif occupation == 10:
        return 10 #young student
    elif occupation == 8:
        return 11 #farmer
    elif occupation == 9:
        return 12 #homemeaker
    elif occupation == 11:
        return 13 #lawyer
    elif occupation == 12:
        return 14 #programmer
    elif occupation == 13:
        return 15 #retired
    elif occupation == 5:
        return 16 #retired
def convert_genre(movie):
    aux = {"Action": 0, "Adventure": 1, "Animation": 2, "Children's": 3, "Comedy": 4, "Crime": 5, "Documentary": 6, "Drama": 7, "Fantasy": 8,"Film-Noir": 9,"Horror": 10, "Musical": 11, "Mystery": 12,"Romance": 13, "Sci-Fi": 14,"Thriller": 15, "War": 16,"Western": 17}
    return aux.get(movie)
def convert_age(age):
    if age < 18:
        return 1
    elif age < 25:
        return 18
    elif age < 35:
        return 25
    elif age < 45:
        return 35
    elif age < 50:
        return 45
    elif age < 56:
        return 50
    return 56
def convert_occupation(occupation):
    if occupation == "academic" or occupation == "educator" or occupation == "academic/educator":
        return 1
    if occupation == "artist":
        return 2
    if occupation == "clerical" or occupation == "admin" or occupation == "clerical/admin":
        return 3
    if occupation == "college" or occupation == "grad student" or occupation == "college/grad student":
        return 4
    if occupation == "customer service":
        return 5
    if occupation == "doctor" or occupation == "health care" or occupation == "doctor/health care":
        return 6
    if occupation == "executive" or occupation == "managerial" or occupation == "executive/managerial":
        return 7
    if occupation == "farmer":
        return 8
    if occupation == "homemaker":
        return 9
    if occupation == "K-12 student" or occupation == "student":
        return 10
    if occupation == "lawyer":
        return 11
    if occupation == "programmer":
        return 12
    if occupation == "retired":
        return 13
    if occupation == "sales" or occupation == "marketing" or occupation == "sales/marketing":
        return 14
    if occupation == "scientist":
        return 15
    if occupation == "self-employed" or occupation == "self employed":
        return 16
    if occupation == "technician" or occupation == "engineer" or occupation == "technician/engineer":
        return 17
    if occupation == "tradesman" or occupation == "craftsman" or occupation == "tradesman/craftsman":
        return 18
    if occupation == "unemployed":
        return 19
    if occupation == "writer":
        return 19
def partition(arr1, arr2, low, high):
    i = (low-1)         # index of smaller element
    pivot = arr1[high]     # pivot
 
    for j in range(low, high):
 
        # If current element is smaller than or
        # equal to pivot
        if arr1[j] <= pivot:
 
            # increment index of smaller element
            i = i+1
            arr1[i], arr1[j] = arr1[j], arr1[i]
            arr2[i], arr2[j] = arr2[j], arr2[i]
 
    arr1[i+1], arr1[high] = arr1[high], arr1[i+1]
    arr2[i+1], arr2[high] = arr2[high], arr2[i+1]
    return (i+1)
def quickSort(arr1, arr2, low, high):
    if len(arr1) == 1:
        return [arr1, arr2]
    if low < high:
 
        # pi is partitioning index, arr[p] is now
        # at right place
        pi = partition(arr1, arr2, low, high)
 
        # Separately sort elements before
        # partition and after partition
        quickSort(arr1, arr2, low, pi-1)
        quickSort(arr1, arr2, pi+1, high)
def getRatios(preferences, movies):
    res = []
    for movie in movies:
        aux = 0
        genres =  movie.genres.split('|')
        for gen in genres:
            aux += float(preferences[convert_genre(gen.replace('\n', ''))])
        res.append(aux/len(genres))
    return res
def delViewed(viewed, movies):
    res=[]
    for i in movies:
        if str(i.id) not in viewed and i != None:
            res.append(i)
    return res

#We define the classes, three one for every file
class user:
    movies_viewed = 0
    def __init__(self, sex, age, occupation):
        self.sex = sex
        self.age = age
        self.occupation = occupation
        self.type = defineType(sex, age, occupation) #depending of the age, sex and occupation
        self.demographic_preferences = [0]*NUM_GEN
class movie:
    def __init__(self, title, genres):
        self.title = title
        self.genres = genres
class rating:
    def __init__(self, userID, movieID, rat, timestamp):
        self.userID = userID
        self.movieID = movieID
        self.rat = rat
        self.timestamp = timestamp

#We create the lists of every class
users = [None]*(NUM_USERS+1)
viewed_movies = [[]]*(NUM_USERS+1)
movies = [None]*(NUM_MOVIES+1)
preferences = []

for i in range(0,17):
    aux = []
    for j in range(0,NUM_GEN+1):
        aux.append(0)
    preferences.append(aux)
viewsType = [0]*17
ratings = []

#We create the objects using the data extracted of the files and append it to the respective list
f = open("ml-1m/users.dat", "r")
for person in f:
    data = person.split("::")
    users[int(data[0])] = user(data[1], int(data[2]), int(data[3]))

f = open("ml-1m/movies.dat", "r")
for film in f:
    data = film.split("::")
    genres = []
    for genre in data[2].split('|'):
        genres.append(genre.strip('\n'))
    movies[int(data[0])] = movie(data[1], genres)
f = open("ml-1m/ratings.dat", "r")
for valoration in f:
    data = valoration.split("::")
    ratings.append(rating(int(data[0]), int(data[1]), int(data[2]), int(data[3])))
res = []
for rat in ratings:
    if rat != None:
        users[rat.userID].movies_viewed += 1
        viewed_movies[rat.userID].append(movies[rat.movieID])
        viewsType[users[rat.userID].type] += 1
        for gen in movies[rat.movieID].genres:
            preferences[users[rat.userID].type][convert_genre(gen)] += rat.rat/5
for i in range(0, 17):
    for j in range(0,NUM_GEN):
        preferences[i][j] = 100*preferences[i][j]/viewsType[i]
for i in range(1,NUM_USERS+1):
        users[i].demographic_preferences = preferences[users[i].type]
def recomendD(size, movies, user):    
    films = delViewed(user.viewed_movies.split(',')[:-1], movies)
    ratios = getRatios(user.demographic_preferences.split(',')[:-1], films)
    quickSort(ratios, films, 0, len(ratios)-1)
    print("We recommend you these movies:")
    res = []
    pointer = len(films)-1
    count = 0
    razon = 1/3
    max_baj = 50
    rat=[]
    j = films[0]
    while count < size:
        medium = int(razon*size)
        if count >= medium*1.5:
            rep_gen = 0
            for j in res:
                if j.genres == films[pointer].genres or j.genres in films[pointer].genres:
                    rep_gen+=1
            if rep_gen > medium:
                pointer-=random.randint(0,max_baj)
        elif count >= medium:
            rep_gen = 0
            for j in res:
                if j.genres == films[pointer].genres or j.genres in films[pointer].genres:
                    rep_gen+=1
            if rep_gen > medium:
                pointer-=random.randint(0,max_baj)
        if films[pointer] not in res and films[pointer].genres!=j.genres:
            res.append(films[pointer])
            rat.append(ratios[pointer])
            count+=1
        pointer-=1
    for i in range(0,len(res)):
        print(res[i].title + " | " + res[i].genres[:-1] + " | " + str(rat[i]))
    return (res,rat)
def recomendC(size, user):
    films=[]
    neighbors = user.ids_neighbors.split(',')[:-1]
    for neighbor in neighbors:
        aux_m = User.query.get(neighbor).viewed_movies.split(',')[:-1]
        for mov in aux_m:
            films.append(mov)
    #Delete viewed
    aux=[]
    for i in films:
        if i != None and str(i) not in user.viewed_movies.split(',')[:-1] and str(i) not in aux:
            aux.append(i)
    res = []
    for i in aux:
        res.append(Movie.query.get(i))
    ratios = getRatios(user.colaborative_preferences.split(',')[:-1], res)
    quickSort(ratios, res, 0, len(ratios)-1)
    films = res
    print("We recommend you these movies:")
    razon = 1/3
    max_baj = 50
    pointer = len(films)-1
    count = 0
    res = []
    rat = []
    j = films[0]
    if pointer > 0:
        while count < size:
            medium = int(razon*size)
            if count >= medium*1.5:
                rep_gen = 0
                for j in res:
                    if j.genres == films[pointer].genres or j.genres in films[pointer].genres:
                        rep_gen+=1
                if rep_gen > medium:
                    pointer-=random.randint(0,max_baj)
            elif count >= medium:
                rep_gen = 0
                for j in res:
                    if j.genres == films[pointer].genres or j.genres in films[pointer].genres:
                        rep_gen+=1
                if rep_gen > medium:
                    pointer-=random.randint(0,max_baj)
            if films[pointer] not in res and films[pointer].genres!=j.genres:
                res.append(films[pointer])
                rat.append(ratios[pointer])
                count+=1
            pointer-=1
    for i in range(0,len(res)):
        print(res[i].title + " | " + res[i].genres[:-1] + " | " + str(rat[i]))
    return (res, rat)

"""print("Ha visto " + str(users[1].movies_viewed) + "peliculas.")
for i in ["Action", "Adventure", "Animation", "Children's", "Comedy", "Crime", "Documentary", "Drama", "Fantasy","Film-Noir","Horror", "Musical", "Mystery","Romance", "Sci-Fi","Thriller", "War","Western"]:
    print("Su preferencia por " + i + " es de " + str(users[1].demographic_preferences[convert(i)]))"""


