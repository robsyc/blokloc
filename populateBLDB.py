#!/usr/bin/env python3
################################################################################################
# SET UP

print("\nINITIATING SETUP...\n")

# import libraries
import os            # for making directories
import sys           # for command line arguments (API url)
import json          # for reading / writing to json file
import requests      # for getting data from API
import time          # for getting current date and time (for date_created and date_modified fields)
import re            # for splitting address into street, number, postal code and city     
import random        # for generating random ratings for locations and observations

# make directories
print("\tPackages loaded\n\tCurrent directory\t: ", os.getcwd())
if not os.path.exists("./data"):
    os.mkdir("./data")
if not os.path.exists("./data/images"):
    os.mkdir("./data/images")
print("\tDirectories created\t: ./date and ./data/images")

# define variables
if len(sys.argv) > 1:
    url = sys.argv[1]
else:
    url = "https://data.stad.gent/api/records/1.0/search/?dataset=bloklocaties-gent&q=&rows=100"
    print("\n\tNo API url specified, using default url")

observation_type_list = ["text", "image", "time_open", "time_close", "wifi", "occupancy", "power", "toilet", "water", "resto", "parking", "link", "phone", "email", "reservation", "weekend"]
observation_type      = dict(zip(observation_type_list, range(1, len(observation_type_list)+1)))
    # Observation types:
    # 1: text       - Textual description/review of the location
    #                   format: "my text"
    # 2: image      - Image of the location
    #                   format: "./data/<title>/<title>_home.jpg"
    # 3: time_open  - Opening hours of the location
    #                   format: "08:00"
    # 4: time_close - Closing hours of the location
    #                   format: "18:00"
    # 5: wifi       - Wifi availability
    # 6: occupancy  - Occupancy of the location
    # 7: power      - Power availability
    # 8: toilet     - Toilet availability
    # 9: water      - Water availability
    # 10: resto     - Student restaurant availability
    # 11: parking   - Parking availability
    # 12: link      - Link to a website with more information 
    #                   format: "my link name:http://www.example.com"
    # ...

user_status_list      = ["lurker", "newbie", "regular", "poweruser", "admin", "dummy"]
user_status           = dict(zip(user_status_list, range(1, len(user_status_list)+1)))
    # User status:
    # 1: lurker     - New user without ratings (cannot add observations or locations)
    # 2: newbie     - User with 1-x ratings (cannot add observations or locations)
    # 3: regular    - User with x-y ratings (can add observations but not locations)
    # 4: poweruser  - User with y-n ratings (can add observations and locations and create new observation types)
    # 5: admin      - User with all rights (add/remove observations and locations from other users)
    # 6: dummy      - Dummy user for testing purposes

rating_list           = ["downvote", "upvote"]
rating                = dict(zip(rating_list, range(0, 2)))
    # You can upvote or downvote an observation or location
    # 0: downvote
    # 1: upvote

odds_loc_rating       = 0.5
odds_obs_rating       = 0.25

print("\tOdds of generating location rating\t: ", odds_loc_rating)
print("\tOdds of generating aobservation rating\t: ", odds_obs_rating)
print("\n\tSetup Complete!\n")

################################################################################################
# HELPER FUNCTIONS

def getDate():
    """
        Returns the current date and time in the format: YYYY-MM-DDTHH:MM:SS+02:00
        This is used for the date_created and date_modified fields in the database.
    """
    return time.strftime("%Y-%m-%dT%H:%M:%S+02:00")


def getImage(title: str, url: str):
    """
        Downloads an image from the given url and saves it in the folder ./data/<title>
        Returns the path to the image.
    """
    img_title = re.sub(r'[^\w\s]', '', title.replace(" ", "_"))
    if not os.path.exists("./data/images/" + img_title):
        os.mkdir("./data/images/" + img_title)
    path = "./data/images/" + img_title + "/" + img_title + "_home" ".jpg"
    data = requests.get(url).content
    with open(path, "wb") as f:
        f.write(data)
    return path


def getAddress(address: str):
    """
        Splits the address into street, number, postal code and city.
        Returns a tuple with these values.
    """
    if ',' in address:
        street_nr, postal_city = address.split(", ")
        postal_city = postal_city.split(" ")
    else:
        postal_city = "9000 Gent"
        street_nr = address
    
    nr = re.search(r'\d+\s*\w*', street_nr).group()
    street = re.split(r'\d', street_nr)[0].strip()

    if len(postal_city) == 2:
        code = postal_city[0]
        city = postal_city[1]
    elif "Gent" in postal_city or "9000" in postal_city:
        code = "9000"
        city = "Gent"
    elif "Merelbeke" in postal_city:
        code = "9820"
        city = "Merelbeke"
    
    return street, nr, code, city


def RandomRating(odds: float):
    """
        Generates a random rating for a location or observation.
        Returns tuple with choices or False if no rating is generated.
    """
    if random.random() < odds:
        user   = random.randint(1, 2)   # 1 = admin     2 = dummy
        rating = random.randint(0, 1)   # 0 = downvote  1 = upvote
        return user, rating
    else:
        return False


################################################################################################
# MAIN

def populateBLDB(url: str):
    data  = requests.get(url).json()
    nhits = data['nhits']
    print("\tNumber of records: " + str(nhits))

    # Data to be added to the database
    data_location    = []
    data_loc_rating  = []
    data_observation = []
    data_obs_rating  = []
    data_user        = [
        {
            "model" : "home.User",
            "pk"    : 1,
            "fields": { 
                "userstatus"    : user_status["admin"],
                "username"      : "test_admin",
                "password"      : "admin123",
                "date_created"  : getDate(),
                "date_modified" : getDate()
            }
        }, {
            "model" : "home.User",
            "pk"    : 2,
            "fields": {
                "userstatus"    : user_status["dummy"],
                "username"      : "test_dummy",
                "password"      : "dummy123",
                "date_created"  : getDate(),
                "date_modified" : getDate()
            }
        }
    ]

    # Keys for the database
    loc_key = 1
    obs_key = 1
    rating_loc_key = 1
    rating_obs_key = 1

    # Loop through all records
    for i in range(nhits):
        # Extract data from record
        record    = data['records'][i]
        record_id = record['recordid']
        fields    = record['fields']
        address   = getAddress(fields['adres'])

        # Determine if location / observation will be rated
        rating_loc = RandomRating(odds_loc_rating)
        if rating_loc:
            loc_rating_user   = rating_loc[0]
            loc_rating_rating = rating_loc[1]
            if loc_rating_rating == 1:
                loc_rating = 1
            else:
                loc_rating = -1
        else:
            loc_rating = 0

        rating_obs = RandomRating(odds_obs_rating)
        if rating_obs:
            obs_rating_user   = rating_obs[0]
            obs_rating_rating = rating_obs[1]
            if obs_rating_rating == 1:
                obs_rating = 1
            else:
                obs_rating = -1
        else:
            obs_rating = 0

        # Add location
        data_location.append({
            "model" : "home.Location",
            "pk"    : loc_key,
            "fields": {
                "fk_user"       : 1,
                "record_id"     : record_id,
                "name"          : fields['label_1'],
                "title"         : fields['titel'],
                "date_created"  : getDate(),
                "date_modified" : getDate(),
                "link"          : fields['lees_meer'],
                "street"        : address[0],
                "number"        : address[1],
                "city"          : address[3],
                "postal_code"   : address[2],
                "latitude"      : fields['geo_punt'][0],
                "longitude"     : fields['geo_punt'][1],
                "capacity"      : fields['totale_capaciteit'],
                "reserved"      : fields['gereserveerde_plaatsen'],
                "loc_rating"    : loc_rating
            }
        })

        # Add image observation to location (as admin)
        data_observation.append({
            "model" : "home.Observation",
            "pk"    : obs_key,
            "fields": {
                "fk_user"       : 1,
                "fk_location"   : loc_key,
                "date_created"  : getDate(),
                "date_modified" : getDate(),
                "obs_rating"    : 0,
                "obs_type"      : observation_type["image"],
                "obs_content"   : getImage(fields['titel'], fields['teaser_img_url'])
            }
        })
        obs_key += 1

        # Add link observation to location (as admin)
        data_observation.append({
            "model" : "home.Observation",
            "pk"    : obs_key,
            "fields": {
                "fk_user"       : user_status["admin"],
                "fk_location"   : loc_key,
                "date_created"  : getDate(),
                "date_modified" : getDate(),
                "obs_rating"    : 0,
                "obs_type"      : observation_type["link"],
                "obs_content"   : "Homepage:" + fields['lees_meer']
            }
        })
        obs_key += 1

        # Add text observation to location (as dummy)
        data_observation.append({
            "model" : "home.Observation",
            "pk"    : obs_key,
            "fields": {
                "fk_user"       : user_status["dummy"],
                "fk_location"   : loc_key,
                "date_created"  : getDate(),
                "date_modified" : getDate(),
                "obs_rating"    : obs_rating,
                "obs_type"      : observation_type["text"],
                "obs_content"   : "Hi! Dummy here, this is a test TEXT-observation for home location " + fields['titel']
            }
        })

        # Add rating to location randomly
        if rating_loc:
            data_loc_rating.append({
                "model" : "home.RatingLoc",
                "pk"    : rating_loc_key,
                "fields": {
                    "fk_user"       : loc_rating_user,
                    "fk_location"   : loc_key,
                    "date_created"  : getDate(),
                    "date_modified" : getDate(),
                    "rating"        : loc_rating_rating
                }
            })
            rating_loc_key += 1

        # Add rating to dummy's TEXT-observation randomly
        if rating_obs:
            data_obs_rating.append({
                "model" : "home.RatingObs",
                "pk"    : rating_obs_key,
                "fields": {
                    "fk_user"       : obs_rating_user,
                    "fk_observation": obs_key,
                    "date_created"  : getDate(),
                    "date_modified" : getDate(),
                    "rating"        : obs_rating_rating
                }
            })
            rating_obs_key += 1
        
        # up to the next location key
        loc_key += 1
        obs_key += 1

    # Combine all lists and save to .json file for later use in Django model
    # >>> python manage.py loaddata initial_blokloc_data.json
    all_data = data_user + data_location + data_observation + data_loc_rating + data_obs_rating
    with open('./data/initial_blokloc_data.json', 'w') as outfile:
        json.dump(all_data, outfile, indent=4)

    print("\n\tData saved to ./data/initial_blokloc_data.json\n\n\
\tTo load data into Django model, run:\n\
\t\tpython manage.py loaddata <path.json>\n")
    
    # Print some statistics
    print("\tNumber of locations\t\t: " + str(loc_key - 1))
    print("\tNumber of observations\t\t: " + str(obs_key - 1))
    print("\tNumber of location ratings\t: " + str(rating_loc_key - 1))
    print("\tNumber of observation ratings\t: " + str(rating_obs_key - 1))

print("------------------------------------------------------------\n\n\
RUNNING MAIN...\n")
populateBLDB(url)
print("\n------------------------------------------------------------\n\n\
DONE!\n")