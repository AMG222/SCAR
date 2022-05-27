NUM_GEN = 18
NUM_USERS = 6040
NUM_MOVIES = 3952
#We define the classes, three one for every file
class user:
    def __init__(self, sex, age, occupation):
        self.sex = sex
        self.age = age
        self.occupation = occupation
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
movies = [None]*(NUM_MOVIES+1)
ratings = []

#We create the objects using the data extracted of the files and append it to the respective list
f = open("ml-1m/users.dat", "r")
for person in f:
    data = person.split("::")
    users[int(data[0])] = user(data[1], int(data[2]), data[3])


f = open("ml-1m/movies.dat", "r")
for film in f:
    data = film.split("::")
    genres = []
    for genre in data[2].split('|'):
        genres.append(genre)
    movies[int(data[0])] = movie(data[1], genres)

f = open("ml-1m/ratings.dat", "r")
for valoration in f:
    data = valoration.split("::")
    ratings.append(rating(int(data[0]), int(data[1]), int(data[2]), int(data[3])))

