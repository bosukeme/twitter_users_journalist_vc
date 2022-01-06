import tweepy
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import sleep
from selenium.webdriver.chrome.options import Options

options=Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
#options.add_argument('--headless')
# options.add_experimental_option('excludeSwitches', ['enable-logging'])
# options.add_argument("disable-infobars")
# options.add_argument("--remote-debugging-port=9222")

from Config.settings import (
    CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET ) 

from Config.settings import MONGODB_USERNAME, MONGODB_PASSWORD



CONNECTION_STRING = "mongodb+srv://%s:%s@bloverseservices.xisjj.mongodb.net/myFirstDatabase?retryWrites=true&w=majority" % (MONGODB_USERNAME, MONGODB_PASSWORD)
client = MongoClient(CONNECTION_STRING)

db = client.twitter_users

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)



# def initialise_mongo_cloud_db_client(MONGODB_USERNAME, MONGODB_PASSWORD):
#     """
#     This is specifically for mongodb cloud, we take the mongo username and password and generate
#     the connection string to connect to the db
#     ** When is the best time to close the mongo client instance?, do we just leave it open indefinitely on the server?
#     """
#     # Generate the connection string
#     CONNECTION_STRING = "mongodb+srv://%s:%s@bloverseservices.xisjj.mongodb.net/myFirstDatabase?retryWrites=true&w=majority" % (MONGODB_USERNAME, MONGODB_PASSWORD)

#     client = MongoClient(CONNECTION_STRING)
    
#     return client


def open_browser(topic_url):
    """
        This starts the chrome browser and opens the url
    """
    ## windows
    PATH = 'C://Users/hp/Desktop/Chrome Driver/chromedriver.exe'

    ## linux
#     PATH = "/usr/lib/chromium-browser/chromedriver"

    try:
        driver = webdriver.Chrome(PATH, options=options)
        driver.maximize_window()
        sleep(2)

        driver.get(topic_url)
        sleep(5)
    except Exception as e:
        print(e)

    return driver


def get_name_and_handle_and_bio(driver):
    """
        This inspectsthe twitter page and gets the name, handle and bio
    """
    try:
        class_path_text = "[class='css-1dbjc4n r-1iusvr4 r-16y2uox']"
        name_handle_bio = driver.find_elements_by_css_selector(class_path_text)
        sleep(4)
        
        bio_data = []
        for item in name_handle_bio:
            name_handle_bio_text = item.text.split("\n")
            
            try:
                name = name_handle_bio_text[0]
            except:
                name = "NA"
                
            try:
                handle = name_handle_bio_text[1].replace("@", "")
            except:
                handle = "NA"
            
            try:
                bio = name_handle_bio_text[3]
            except:
                bio = "NA"
                
            
            data = {
                "name" : name,
                "handle": handle,
                "bio": bio
            }
            
            bio_data.append(data)
        
    except Exception as e:
        print(e)

    return bio_data



def get_record_details(search_dict, collection, find_one=True):
    """
        This searches through mongodb for a single record
    """
    try:
        query = collection.find_one(search_dict) if find_one else collection.find(search_dict)
        return query
    except Exception as e:
        print(e)
        return None


def insert_records(collection, record):
    """
        This inserts a single record to mongo db
    """
    try:
        collection.insert_one(record)
    except Exception as e:
        print(e)

def save_to_mongo_db(data, collection):
    """
        This saves the record to mongo db
    """
    insert_records(collection, data)
    # cur = collection.count_documents({})
    # print(f"we have {cur} entries")







def scroll_down_twitter(driver, collection):
    """
        This implements an infinite scroll on twitter and stops at the end of the page
    """
    try:
        last_height = driver.execute_script("return document.body.scrollHeight") + 20000

        new_height = 10

        while True:

            driver.execute_script(f"window.scrollTo(0, {new_height});")
            sleep(7)
            
            bio_data = get_name_and_handle_and_bio(driver)
            
            for item in bio_data:
                handle = item['handle']
                print(handle)
                search_dict = {'handle': handle}
                
                query  = get_record_details(search_dict, collection, find_one=True)
                if query  == None:

                    user_query = api.get_user(screen_name = handle)._json 
                    
                    followings_count = user_query['friends_count']
                    followers_count = user_query['followers_count']
                    is_verified_query = user_query['verified']

                    if is_verified_query:
                        verified = {"verified" : "Yes"}

                        collection1 = db.verified_twitter_users
                        query1  = get_record_details(search_dict, collection1, find_one=True)
                        if query1  == None:
                            data1 = {
                                    'handle': user_query['screen_name'],
                                    'user_bio': user_query['description'],
                                    'user_id': user_query['id'],
                                    'user_profile_image': user_query['profile_image_url'],
                                    'username': user_query['name']
                                }

                            save_to_mongo_db(data1, collection1)

                    else:
                        verified = {"verified" : "No"}


                    follower_following_dict = {
                        "followings_count": followings_count,
                        "followers_count" : followers_count
                    }
                    data = {**item, **verified, **follower_following_dict}
                    print(data)
                    save_to_mongo_db(data, collection)

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script(f"return {new_height+1000}")
            if new_height >  2000: #last_height:
                break
    except Exception as e:
        print(e)
        
    return None




def get_tweet_users():
    search_word = "journalist"
    url = f"https://twitter.com/search?q={search_word}&src=typed_query&f=user"

    collection = db[search_word]

    driver = open_browser(url)
    scroll_down_twitter(driver, collection)

    driver.quit()


get_tweet_users()