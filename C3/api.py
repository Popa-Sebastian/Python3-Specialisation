import requests
import json

bp = {"Similar": {"Info": [{"Name": "Black Panther", "Type": "movie"}], "Results": [{"Name": "Ready Player One", "Type": "movie"}, {"Name": "A Quiet Place", "Type": "movie"}, {"Name": "Deadpool 2", "Type": "movie"}, {"Name": "Thor: Ragnarok", "Type": "movie"}, {"Name": "Avengers: Infinity War", "Type": "movie"}]}}
cm = {"Similar": {"Info": [{"Name": "Captain Marvel", "Type": "movie"}], "Results": [{"Name": "Spider-Man: Far From Home", "Type": "movie"}, {"Name": "Ant-Man And The Wasp", "Type": "movie"}, {"Name": "Shazam!", "Type": "movie"}, {"Name": "Avengers: Endgame", "Type": "movie"}, {"Name": "Avengers: Infinity War", "Type": "movie"}]}}
dp = {"Title":"Deadpool 2","Year":"2018","Rated":"R","Released":"18 May 2018","Runtime":"119 min","Genre":"Action, Adventure, Comedy, Sci-Fi","Director":"David Leitch","Writer":"Rhett Reese, Paul Wernick, Ryan Reynolds","Actors":"Ryan Reynolds, Josh Brolin, Morena Baccarin, Julian Dennison","Plot":"Foul-mouthed mutant mercenary Wade Wilson (a.k.a. Deadpool), brings together a team of fellow mutant rogues to protect a young boy with supernatural abilities from the brutal, time-traveling cyborg Cable.","Language":"English, Cantonese, Spanish, Russian","Country":"Canada, USA","Awards":"6 wins & 51 nominations.","Poster":"https://m.media-amazon.com/images/M/MV5BNjk1Njk3YjctMmMyYS00Y2I4LThhMzktN2U0MTMyZTFlYWQ5XkEyXkFqcGdeQXVyODM2ODEzMDA@._V1_SX300.jpg","Ratings":[{"Source":"Internet Movie Database","Value":"7.7/10"},{"Source":"Rotten Tomatoes","Value":"84%"},{"Source":"Metacritic","Value":"66/100"}],"Metascore":"66","imdbRating":"7.7","imdbVotes":"476,268","imdbID":"tt5463162","Type":"movie","DVD":"N/A","BoxOffice":"$324,591,735","Production":"Kinberg Genre, Maximum Effort","Website":"N/A","Response":"True"}
def get_movies_from_tastedive(input_str):
    baseurl = 'https://tastedive.com/api/similar'
    params_dict = {}
    params_dict['q'] = input_str
    params_dict['type'] = 'movies'
    params_dict['limit'] = '5'
    params_dict['k'] = '399698-Coursewo-UQRJ7JMB'
    tastedive_response = requests.get(baseurl, params=params_dict)
    print("Taste Dive generated URL:\n{}".format(tastedive_response.url))
    # print(tastedive_response.text)
    # print(json.dumps(tastedive_response.json(), indent=4))
    return tastedive_response.json()


def extract_movie_titles(movie_dict):
    # print(movie_dict['Similar']['Results'])
    movies = movie_dict['Similar']['Results']
    titles_list = []
    for d in movies:
        if d['Type'] == 'movie':
            # print(d['Name'])
            titles_list.append(d['Name'])
    # print(titles_list)
    return (titles_list)

def get_related_titles(input_list):
    title_list = []
    for movie in input_list:
        titles = extract_movie_titles(get_movies_from_tastedive(movie))
        for title in titles:
            if title not in title_list:
                title_list.append(title)
    print("Related titles for {}\n".format(input_list))
    print(title_list)
    return title_list

def get_movie_data(input_title):
    params_dict = {}
    baseurl = 'http://www.omdbapi.com/'
    params_dict['apikey'] = '8a82b120'
    params_dict['t'] = input_title
    params_dict['r'] = 'json'
    omdb_response = requests.get(baseurl, params=params_dict)
    # print("OMDb generated URL:\n{}".format(omdb_response.url))
    # print(omdb_response.text)
    # print(json.dumps(omdb_response.json(), indent=4))
    return omdb_response.json()

def get_movie_rating(omdb_dict):
    # print(omdb_dict['Ratings'][1])
    if omdb_dict['Ratings'][1]['Source'] == 'Rotten Tomatoes':
        # print(int(omdb_dict['Ratings'][1]["Value"][:-1]))
        return int(omdb_dict['Ratings'][1]["Value"][:-1])
    else:
        return 0

def get_sorted_recommendations(movie_list):
    titles = get_related_titles(movie_list)
    ratings = []
    for title in titles:
        ratings.append(get_movie_rating(get_movie_data(title)))
    titles_ratings = list(zip(titles, ratings))
    sorted_titles_tup = sorted(titles_ratings, key = lambda x: -x[1])
    print("Sorted titles and related score\n{}".format(sorted_titles_tup))
    sorted_titles = [x[0] for x in sorted_titles_tup]
    print ("Sorted titles by Rotten Tomatoes rating:\n{}".format(sorted_titles))
    return sorted_titles

# get_movies_from_tastedive("Black Panther")
# get_movies_from_tastedive("Captain Marvel")
# get_related_titles(["Black Panther", "Captain Marvel"])
# get_movie_data("Venom")
# get_movie_data("Baby Mama")

get_sorted_recommendations(["Bridesmaids", "Sherlock Holmes"])