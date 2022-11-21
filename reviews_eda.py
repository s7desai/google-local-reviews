import gzip
from tqdm import tqdm, trange
import pandas as pd
from shapely.geometry import Point
import geopandas as gpd
from geopandas import GeoDataFrame
import folium
import pickle
from collections import defaultdict
from datetime import datetime
import matplotlib.pyplot as plt


places_file = "places.clean.json.gz"
users_file = "users.clean.json.gz"
reviews_file = "reviews.clean.json.gz"

user_demog_file = "user_deomograhics.pkl"
bus_demog_file = "business_deomograhics.pkl"



def parse(path):
    g = gzip.open(path, 'r')
    for l in g:
        yield eval(l)

places_data = []


users_data = []


reviews_data = []

nrec = 0
for l in tqdm(parse(places_file)):
    # if nrec == 5:
    #     break
    places_data.append(l)
    nrec += 1



places_data[0]

nrec = 0
for l in tqdm(parse(users_file)):
    if nrec == 5:
        break
    users_data.append(l)
    nrec += 1

users_data[0]

for l in tqdm(parse(reviews_file)):
    reviews_data.append(l)

with open('reviews_data.pkl', 'wb') as f:
    pickle.dump(reviews_data, f)

with open(user_demog_file, 'rb') as f:
    user_demog = pickle.load(f)

with open(bus_demog_file, 'rb') as f:
    place_demog = pickle.load(f)

place_country_dict = dict()
for p, country in place_demog:
    place_country_dict[p] = country

len(us_places_set)

place_demog[:10]

reviews_data[0]

def remove_review(review):
    if ('categories' not in review or 
        review['categories'] == None or 
        'reviewTime' not in review or 
        review['reviewTime'] == None):
        return True
    date = datetime.fromtimestamp(review['unixReviewTime'])
    month = int(date.month)
    year = int(date.year)
    if (year < 2004):
        return True
    return False

def is_place_in_us(review, place_country_dict):
    place_id = review['gPlusPlaceId']
    if place_id not in place_country_dict:
        return False
    if place_country_dict[place_id] == 'United States':
        return True
    return False

modified_reviews_data = []
for d in tqdm(reviews_data):
    if remove_review(d):
        continue
    else:
        modified_reviews_data.append(d)

us_reviews_data = []
for d in tqdm(modified_reviews_data):
    if is_place_in_us(d, place_country_dict):
        us_reviews_data.append(d)

len(modified_reviews_data)

len(us_reviews_data)

reviews_data[0]
#len(modified_reviews_data)

def user_item_interactions(rev_data):
    usersPerItem = defaultdict(set)
    itemsPerUser = defaultdict(set)
    ratingsDict = defaultdict(float)
    for d in tqdm(rev_data):
        u = d['gPlusUserId']
        i = d['gPlusPlaceId']
        ratingsDict[(u,i)] = d['rating']
        usersPerItem[i].add(u)
        itemsPerUser[u].add(i)
    return usersPerItem, itemsPerUser, ratingsDict

def get_categories_count(rev_data):
    # get categories
    categories_dict = defaultdict(list)
    for i in tqdm(range(len(rev_data))):
        for c in rev_data[i]['categories']:
            categories_dict[c].append(rev_data[i])
    categories_count_lis = []
    for c in categories_dict:
        categories_count_lis.append((c, len(categories_dict[c])))
    categories_count_lis.sort(key=lambda x: x[1], reverse=True)
    return categories_count_lis

def plot_top_categories(categories_count_lis):
    # plot top categories
    bar = plt.bar([c[0] for c in categories_count_lis[:20]] , [c[1] for c in categories_count_lis[:20]], width = 0.5)
    plt.xticks(rotation = 75)
    plt.show()

def plot_map(rev_data):
    # plotting on map
    lat_lon = []
    long_lat_dict = {
                        "Longitude" : [],
                        "Latitude" : []
                    }
    for p in tqdm(range(len(rev_data))):
        long_lat_dict["Longitude"].append(rev_data[p]['gps'][1])
        long_lat_dict["Latitude"].append(rev_data[p]['gps'][0])
        lat_lon.append((rev_data[p]['gps'][1], rev_data[p]['gps'][0]))
    df = pd.DataFrame(long_lat_dict)
    df.plot(x="Longitude", y="Latitude", kind="scatter", c="red",
        colormap="YlOrRd")


def plot_ratings_over_time(rev_data):
    rating_dict = defaultdict(list)
    for i in tqdm(range(len(rev_data))):
        date = datetime.fromtimestamp(rev_data[i]['unixReviewTime'])
        month = int(date.month)
        year = int(date.year)
        if (year < 2004):
            continue
        updated_date = datetime(year, month, 1)
        rating_dict[updated_date].append(rev_data[i]['rating'])
    date_vals = []
    for y in tqdm(rating_dict):
        nvals = len(rating_dict[y])
        date_vals.append((y, sum(rating_dict[y])/nvals))
    date_vals.sort()
    # plot of ratings over time
    dates = [y[0] for y in date_vals]
    ratings = [y[1] for y in date_vals]
    plt.plot(dates, ratings)
    # number of points per year filter on that: less points before 2013

def plot_data_every_year(rev_data):
    year_count_dict = defaultdict(int)
    for i in tqdm(range(len(rev_data))):
        date = datetime.fromtimestamp(rev_data[i]['unixReviewTime'])
        year = int(date.year)
        year_count_dict[year] += 1
    year_counts = []
    for y in year_count_dict:
        year_counts.append((y, year_count_dict[y]))
    year_counts.sort()
    bar = plt.bar([y[0] for y in year_counts] , [y[1] for y in year_counts], width = 0.5)
    plt.xticks(rotation = 75)
    plt.show()

# avg rating per place vs number of ratings for a place
def plot_item_stats(usersPerItem, ratingsDict):
    itemStats = defaultdict(tuple)
    avgItemRatings = defaultdict(float)
    totalItemCounts = defaultdict(int)
    greater100_item = 0
    for i in tqdm(usersPerItem):
        users = usersPerItem[i]
        totalItemCounts[i] = len(users)
        if (len(users) >= 50):
            greater100_item += 1
        sum_rat = 0
        for u in users:
            sum_rat += ratingsDict[(u,i)]

        avgItemRatings[i] = sum_rat/len(users)
    avgs_i_lis = []
    total_i_lis = []
    for i in tqdm(avgItemRatings):
        avgs_i_lis.append(avgItemRatings[i])
        total_i_lis.append(totalItemCounts[i])
    plt.scatter(avgs_i_lis, total_i_lis, c ="red")
    plt.show()

def plot_user_stats(itemsPerUser,ratingsDict):
    userStats = defaultdict(tuple)

    avgUserRatings = defaultdict(float)
    totalUserCounts = defaultdict(int)
    greater100_user = 0
    for u in tqdm(itemsPerUser):
        items = itemsPerUser[u]
        totalUserCounts[u] = len(items)
        if (len(items) >= 50):
            greater100_user += 1
        sum_rat = 0
        for i in items:
            sum_rat += ratingsDict[(u,i)]

        avgUserRatings[u] = sum_rat/len(items)
        
    avgs_u_lis = []
    total_u_lis = []
    for u in tqdm(avgUserRatings):
        avgs_u_lis.append(avgUserRatings[u])
        total_u_lis.append(totalUserCounts[u])
    plt.scatter(avgs_u_lis, total_u_lis, c ="red")
    plt.show()

def plot_country_interactions(places_demog, rev_data):
    place_country_dict = {}
    for p, country in places_demog:
        place_country_dict[p] = country
    country_count = defaultdict(int)
    for d in tqdm(rev_data):
        place_id = d['gPlusPlaceId']
        if place_id not in place_country_dict:
            continue
        country_count[place_country_dict[place_id]] += 1
    
    countries_tups = []
    for c in country_count:
        countries_tups.append((c, country_count[c]))
    countries_tups.sort(key=lambda x : x[1], reverse=True)
    print(countries_tups[:10])
    bar = plt.bar([y[0] for y in countries_tups[:10]] , [y[1] for y in countries_tups[:10]], width = 0.5)
    plt.xticks(rotation = 75)
    plt.show()
    return country_count
        

usersPerItem_whole, itemsPerUser_whole, ratingsDict_whole = user_item_interactions(modified_reviews_data)

categories_count_lis_whole = get_categories_count(modified_reviews_data)

plot_top_categories(categories_count_lis_whole)

plot_ratings_over_time(modified_reviews_data)

len(modified_reviews_data)

plot_data_every_year(modified_reviews_data)

cc = plot_country_interactions(place_demog, modified_reviews_data)



plot_item_stats(usersPerItem_whole, ratingsDict_whole)

plot_user_stats(itemsPerUser_whole, ratingsDict_whole)

usersPerItem_us, itemsPerUser_us, ratingsDict_us = user_item_interactions(us_reviews_data)

categories_count_lis_us = get_categories_count(us_reviews_data)

plot_top_categories(categories_count_lis_us)

plot_ratings_over_time(us_reviews_data)

plot_data_every_year(us_reviews_data)

plot_item_stats(usersPerItem_us, ratingsDict_us)

plot_user_stats(itemsPerUser_us, ratingsDict_us)

len(us_reviews_data)

with open('us_reviews_data.pkl', 'wb') as f:
    pickle.dump(us_reviews_data, f)





import gzip
from tqdm import tqdm, trange
import pandas as pd
from shapely.geometry import Point
import geopandas as gpd
from geopandas import GeoDataFrame
import folium
import pickle
from collections import defaultdict
from datetime import datetime
import matplotlib.pyplot as plt


places_file = "places.clean.json.gz"
users_file = "users.clean.json.gz"
reviews_file = "reviews.clean.json.gz"

user_demog_file = "user_deomograhics.pkl"
bus_demog_file = "business_deomograhics.pkl"



def parse(path):
    g = gzip.open(path, 'r')
    for l in g:
        yield eval(l)

places_data = []


users_data = []


reviews_data = []

nrec = 0
for l in tqdm(parse(places_file)):
    # if nrec == 5:
    #     break
    places_data.append(l)
    nrec += 1



places_data[0]

nrec = 0
for l in tqdm(parse(users_file)):
    if nrec == 5:
        break
    users_data.append(l)
    nrec += 1

users_data[0]

for l in tqdm(parse(reviews_file)):
    reviews_data.append(l)

with open('reviews_data.pkl', 'wb') as f:
    pickle.dump(reviews_data, f)

with open(user_demog_file, 'rb') as f:
    user_demog = pickle.load(f)

with open(bus_demog_file, 'rb') as f:
    place_demog = pickle.load(f)

place_country_dict = dict()
for p, country in place_demog:
    place_country_dict[p] = country

len(us_places_set)

place_demog[:10]

reviews_data[0]

def remove_review(review):
    if ('categories' not in review or 
        review['categories'] == None or 
        'reviewTime' not in review or 
        review['reviewTime'] == None):
        return True
    date = datetime.fromtimestamp(review['unixReviewTime'])
    month = int(date.month)
    year = int(date.year)
    if (year < 2004):
        return True
    return False

def is_place_in_us(review, place_country_dict):
    place_id = review['gPlusPlaceId']
    if place_id not in place_country_dict:
        return False
    if place_country_dict[place_id] == 'United States':
        return True
    return False

modified_reviews_data = []
for d in tqdm(reviews_data):
    if remove_review(d):
        continue
    else:
        modified_reviews_data.append(d)

us_reviews_data = []
for d in tqdm(modified_reviews_data):
    if is_place_in_us(d, place_country_dict):
        us_reviews_data.append(d)

len(modified_reviews_data)

len(us_reviews_data)

reviews_data[0]
#len(modified_reviews_data)

def user_item_interactions(rev_data):
    usersPerItem = defaultdict(set)
    itemsPerUser = defaultdict(set)
    ratingsDict = defaultdict(float)
    for d in tqdm(rev_data):
        u = d['gPlusUserId']
        i = d['gPlusPlaceId']
        ratingsDict[(u,i)] = d['rating']
        usersPerItem[i].add(u)
        itemsPerUser[u].add(i)
    return usersPerItem, itemsPerUser, ratingsDict

def get_categories_count(rev_data):
    # get categories
    categories_dict = defaultdict(list)
    for i in tqdm(range(len(rev_data))):
        for c in rev_data[i]['categories']:
            categories_dict[c].append(rev_data[i])
    categories_count_lis = []
    for c in categories_dict:
        categories_count_lis.append((c, len(categories_dict[c])))
    categories_count_lis.sort(key=lambda x: x[1], reverse=True)
    return categories_count_lis

def plot_top_categories(categories_count_lis):
    # plot top categories
    bar = plt.bar([c[0] for c in categories_count_lis[:20]] , [c[1] for c in categories_count_lis[:20]], width = 0.5)
    plt.xticks(rotation = 75)
    plt.show()

def plot_map(rev_data):
    # plotting on map
    lat_lon = []
    long_lat_dict = {
                        "Longitude" : [],
                        "Latitude" : []
                    }
    for p in tqdm(range(len(rev_data))):
        long_lat_dict["Longitude"].append(rev_data[p]['gps'][1])
        long_lat_dict["Latitude"].append(rev_data[p]['gps'][0])
        lat_lon.append((rev_data[p]['gps'][1], rev_data[p]['gps'][0]))
    df = pd.DataFrame(long_lat_dict)
    df.plot(x="Longitude", y="Latitude", kind="scatter", c="red",
        colormap="YlOrRd")


def plot_ratings_over_time(rev_data):
    rating_dict = defaultdict(list)
    for i in tqdm(range(len(rev_data))):
        date = datetime.fromtimestamp(rev_data[i]['unixReviewTime'])
        month = int(date.month)
        year = int(date.year)
        if (year < 2004):
            continue
        updated_date = datetime(year, month, 1)
        rating_dict[updated_date].append(rev_data[i]['rating'])
    date_vals = []
    for y in tqdm(rating_dict):
        nvals = len(rating_dict[y])
        date_vals.append((y, sum(rating_dict[y])/nvals))
    date_vals.sort()
    # plot of ratings over time
    dates = [y[0] for y in date_vals]
    ratings = [y[1] for y in date_vals]
    plt.plot(dates, ratings)
    # number of points per year filter on that: less points before 2013

def plot_data_every_year(rev_data):
    year_count_dict = defaultdict(int)
    for i in tqdm(range(len(rev_data))):
        date = datetime.fromtimestamp(rev_data[i]['unixReviewTime'])
        year = int(date.year)
        year_count_dict[year] += 1
    year_counts = []
    for y in year_count_dict:
        year_counts.append((y, year_count_dict[y]))
    year_counts.sort()
    bar = plt.bar([y[0] for y in year_counts] , [y[1] for y in year_counts], width = 0.5)
    plt.xticks(rotation = 75)
    plt.show()

# avg rating per place vs number of ratings for a place
def plot_item_stats(usersPerItem, ratingsDict):
    itemStats = defaultdict(tuple)
    avgItemRatings = defaultdict(float)
    totalItemCounts = defaultdict(int)
    greater100_item = 0
    for i in tqdm(usersPerItem):
        users = usersPerItem[i]
        totalItemCounts[i] = len(users)
        if (len(users) >= 50):
            greater100_item += 1
        sum_rat = 0
        for u in users:
            sum_rat += ratingsDict[(u,i)]

        avgItemRatings[i] = sum_rat/len(users)
    avgs_i_lis = []
    total_i_lis = []
    for i in tqdm(avgItemRatings):
        avgs_i_lis.append(avgItemRatings[i])
        total_i_lis.append(totalItemCounts[i])
    plt.scatter(avgs_i_lis, total_i_lis, c ="red")
    plt.show()

def plot_user_stats(itemsPerUser,ratingsDict):
    userStats = defaultdict(tuple)

    avgUserRatings = defaultdict(float)
    totalUserCounts = defaultdict(int)
    greater100_user = 0
    for u in tqdm(itemsPerUser):
        items = itemsPerUser[u]
        totalUserCounts[u] = len(items)
        if (len(items) >= 50):
            greater100_user += 1
        sum_rat = 0
        for i in items:
            sum_rat += ratingsDict[(u,i)]

        avgUserRatings[u] = sum_rat/len(items)
        
    avgs_u_lis = []
    total_u_lis = []
    for u in tqdm(avgUserRatings):
        avgs_u_lis.append(avgUserRatings[u])
        total_u_lis.append(totalUserCounts[u])
    plt.scatter(avgs_u_lis, total_u_lis, c ="red")
    plt.show()

def plot_country_interactions(places_demog, rev_data):
    place_country_dict = {}
    for p, country in places_demog:
        place_country_dict[p] = country
    country_count = defaultdict(int)
    for d in tqdm(rev_data):
        place_id = d['gPlusPlaceId']
        if place_id not in place_country_dict:
            continue
        country_count[place_country_dict[place_id]] += 1
    
    countries_tups = []
    for c in country_count:
        countries_tups.append((c, country_count[c]))
    countries_tups.sort(key=lambda x : x[1], reverse=True)
    print(countries_tups[:10])
    bar = plt.bar([y[0] for y in countries_tups[:10]] , [y[1] for y in countries_tups[:10]], width = 0.5)
    plt.xticks(rotation = 75)
    plt.show()
    return country_count
        

usersPerItem_whole, itemsPerUser_whole, ratingsDict_whole = user_item_interactions(modified_reviews_data)

categories_count_lis_whole = get_categories_count(modified_reviews_data)

plot_top_categories(categories_count_lis_whole)

plot_ratings_over_time(modified_reviews_data)

len(modified_reviews_data)

plot_data_every_year(modified_reviews_data)

cc = plot_country_interactions(place_demog, modified_reviews_data)



plot_item_stats(usersPerItem_whole, ratingsDict_whole)

plot_user_stats(itemsPerUser_whole, ratingsDict_whole)

usersPerItem_us, itemsPerUser_us, ratingsDict_us = user_item_interactions(us_reviews_data)

categories_count_lis_us = get_categories_count(us_reviews_data)

plot_top_categories(categories_count_lis_us)

plot_ratings_over_time(us_reviews_data)

plot_data_every_year(us_reviews_data)

plot_item_stats(usersPerItem_us, ratingsDict_us)

plot_user_stats(itemsPerUser_us, ratingsDict_us)

len(us_reviews_data)

with open('us_reviews_data.pkl', 'wb') as f:
    pickle.dump(us_reviews_data, f)





import gzip
from tqdm import tqdm, trange
import pandas as pd
from shapely.geometry import Point
import geopandas as gpd
from geopandas import GeoDataFrame
import folium
import pickle
from collections import defaultdict
from datetime import datetime
import matplotlib.pyplot as plt


places_file = "places.clean.json.gz"
users_file = "users.clean.json.gz"
reviews_file = "reviews.clean.json.gz"

user_demog_file = "user_deomograhics.pkl"
bus_demog_file = "business_deomograhics.pkl"



def parse(path):
    g = gzip.open(path, 'r')
    for l in g:
        yield eval(l)

places_data = []


users_data = []


reviews_data = []

nrec = 0
for l in tqdm(parse(places_file)):
    # if nrec == 5:
    #     break
    places_data.append(l)
    nrec += 1



places_data[0]

nrec = 0
for l in tqdm(parse(users_file)):
    if nrec == 5:
        break
    users_data.append(l)
    nrec += 1

users_data[0]

for l in tqdm(parse(reviews_file)):
    reviews_data.append(l)

with open('reviews_data.pkl', 'wb') as f:
    pickle.dump(reviews_data, f)

with open(user_demog_file, 'rb') as f:
    user_demog = pickle.load(f)

with open(bus_demog_file, 'rb') as f:
    place_demog = pickle.load(f)

place_country_dict = dict()
for p, country in place_demog:
    place_country_dict[p] = country

len(us_places_set)

place_demog[:10]

reviews_data[0]

def remove_review(review):
    if ('categories' not in review or 
        review['categories'] == None or 
        'reviewTime' not in review or 
        review['reviewTime'] == None):
        return True
    date = datetime.fromtimestamp(review['unixReviewTime'])
    month = int(date.month)
    year = int(date.year)
    if (year < 2004):
        return True
    return False

def is_place_in_us(review, place_country_dict):
    place_id = review['gPlusPlaceId']
    if place_id not in place_country_dict:
        return False
    if place_country_dict[place_id] == 'United States':
        return True
    return False

modified_reviews_data = []
for d in tqdm(reviews_data):
    if remove_review(d):
        continue
    else:
        modified_reviews_data.append(d)

us_reviews_data = []
for d in tqdm(modified_reviews_data):
    if is_place_in_us(d, place_country_dict):
        us_reviews_data.append(d)

len(modified_reviews_data)

len(us_reviews_data)

reviews_data[0]
#len(modified_reviews_data)

def user_item_interactions(rev_data):
    usersPerItem = defaultdict(set)
    itemsPerUser = defaultdict(set)
    ratingsDict = defaultdict(float)
    for d in tqdm(rev_data):
        u = d['gPlusUserId']
        i = d['gPlusPlaceId']
        ratingsDict[(u,i)] = d['rating']
        usersPerItem[i].add(u)
        itemsPerUser[u].add(i)
    return usersPerItem, itemsPerUser, ratingsDict

def get_categories_count(rev_data):
    # get categories
    categories_dict = defaultdict(list)
    for i in tqdm(range(len(rev_data))):
        for c in rev_data[i]['categories']:
            categories_dict[c].append(rev_data[i])
    categories_count_lis = []
    for c in categories_dict:
        categories_count_lis.append((c, len(categories_dict[c])))
    categories_count_lis.sort(key=lambda x: x[1], reverse=True)
    return categories_count_lis

def plot_top_categories(categories_count_lis):
    # plot top categories
    bar = plt.bar([c[0] for c in categories_count_lis[:20]] , [c[1] for c in categories_count_lis[:20]], width = 0.5)
    plt.xticks(rotation = 75)
    plt.show()

def plot_map(rev_data):
    # plotting on map
    lat_lon = []
    long_lat_dict = {
                        "Longitude" : [],
                        "Latitude" : []
                    }
    for p in tqdm(range(len(rev_data))):
        long_lat_dict["Longitude"].append(rev_data[p]['gps'][1])
        long_lat_dict["Latitude"].append(rev_data[p]['gps'][0])
        lat_lon.append((rev_data[p]['gps'][1], rev_data[p]['gps'][0]))
    df = pd.DataFrame(long_lat_dict)
    df.plot(x="Longitude", y="Latitude", kind="scatter", c="red",
        colormap="YlOrRd")


def plot_ratings_over_time(rev_data):
    rating_dict = defaultdict(list)
    for i in tqdm(range(len(rev_data))):
        date = datetime.fromtimestamp(rev_data[i]['unixReviewTime'])
        month = int(date.month)
        year = int(date.year)
        if (year < 2004):
            continue
        updated_date = datetime(year, month, 1)
        rating_dict[updated_date].append(rev_data[i]['rating'])
    date_vals = []
    for y in tqdm(rating_dict):
        nvals = len(rating_dict[y])
        date_vals.append((y, sum(rating_dict[y])/nvals))
    date_vals.sort()
    # plot of ratings over time
    dates = [y[0] for y in date_vals]
    ratings = [y[1] for y in date_vals]
    plt.plot(dates, ratings)
    # number of points per year filter on that: less points before 2013

def plot_data_every_year(rev_data):
    year_count_dict = defaultdict(int)
    for i in tqdm(range(len(rev_data))):
        date = datetime.fromtimestamp(rev_data[i]['unixReviewTime'])
        year = int(date.year)
        year_count_dict[year] += 1
    year_counts = []
    for y in year_count_dict:
        year_counts.append((y, year_count_dict[y]))
    year_counts.sort()
    bar = plt.bar([y[0] for y in year_counts] , [y[1] for y in year_counts], width = 0.5)
    plt.xticks(rotation = 75)
    plt.show()

# avg rating per place vs number of ratings for a place
def plot_item_stats(usersPerItem, ratingsDict):
    itemStats = defaultdict(tuple)
    avgItemRatings = defaultdict(float)
    totalItemCounts = defaultdict(int)
    greater100_item = 0
    for i in tqdm(usersPerItem):
        users = usersPerItem[i]
        totalItemCounts[i] = len(users)
        if (len(users) >= 50):
            greater100_item += 1
        sum_rat = 0
        for u in users:
            sum_rat += ratingsDict[(u,i)]

        avgItemRatings[i] = sum_rat/len(users)
    avgs_i_lis = []
    total_i_lis = []
    for i in tqdm(avgItemRatings):
        avgs_i_lis.append(avgItemRatings[i])
        total_i_lis.append(totalItemCounts[i])
    plt.scatter(avgs_i_lis, total_i_lis, c ="red")
    plt.show()

def plot_user_stats(itemsPerUser,ratingsDict):
    userStats = defaultdict(tuple)

    avgUserRatings = defaultdict(float)
    totalUserCounts = defaultdict(int)
    greater100_user = 0
    for u in tqdm(itemsPerUser):
        items = itemsPerUser[u]
        totalUserCounts[u] = len(items)
        if (len(items) >= 50):
            greater100_user += 1
        sum_rat = 0
        for i in items:
            sum_rat += ratingsDict[(u,i)]

        avgUserRatings[u] = sum_rat/len(items)
        
    avgs_u_lis = []
    total_u_lis = []
    for u in tqdm(avgUserRatings):
        avgs_u_lis.append(avgUserRatings[u])
        total_u_lis.append(totalUserCounts[u])
    plt.scatter(avgs_u_lis, total_u_lis, c ="red")
    plt.show()

def plot_country_interactions(places_demog, rev_data):
    place_country_dict = {}
    for p, country in places_demog:
        place_country_dict[p] = country
    country_count = defaultdict(int)
    for d in tqdm(rev_data):
        place_id = d['gPlusPlaceId']
        if place_id not in place_country_dict:
            continue
        country_count[place_country_dict[place_id]] += 1
    
    countries_tups = []
    for c in country_count:
        countries_tups.append((c, country_count[c]))
    countries_tups.sort(key=lambda x : x[1], reverse=True)
    print(countries_tups[:10])
    bar = plt.bar([y[0] for y in countries_tups[:10]] , [y[1] for y in countries_tups[:10]], width = 0.5)
    plt.xticks(rotation = 75)
    plt.show()
    return country_count
        

usersPerItem_whole, itemsPerUser_whole, ratingsDict_whole = user_item_interactions(modified_reviews_data)

categories_count_lis_whole = get_categories_count(modified_reviews_data)

plot_top_categories(categories_count_lis_whole)

plot_ratings_over_time(modified_reviews_data)

len(modified_reviews_data)

plot_data_every_year(modified_reviews_data)

cc = plot_country_interactions(place_demog, modified_reviews_data)



plot_item_stats(usersPerItem_whole, ratingsDict_whole)

plot_user_stats(itemsPerUser_whole, ratingsDict_whole)

usersPerItem_us, itemsPerUser_us, ratingsDict_us = user_item_interactions(us_reviews_data)

categories_count_lis_us = get_categories_count(us_reviews_data)

plot_top_categories(categories_count_lis_us)

plot_ratings_over_time(us_reviews_data)

plot_data_every_year(us_reviews_data)

plot_item_stats(usersPerItem_us, ratingsDict_us)

plot_user_stats(itemsPerUser_us, ratingsDict_us)

len(us_reviews_data)

with open('us_reviews_data.pkl', 'wb') as f:
    pickle.dump(us_reviews_data, f)