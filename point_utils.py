'''
point_utils.py

functions that deal with updating viewer records 
'''
import json
import os
from dotenv import load_dotenv

load_dotenv()
VIEWERS_FILE = os.getenv('VIEWERS_FILE')
CURRENT_VIEWERS_FILE = os.getenv('CURRENT_VIEWERS_FILE')


def get_viewer_data():
    viewer_data = {}
    with open(VIEWERS_FILE, "r") as jsonFile:
        viewer_data = json.load(jsonFile)
    return viewer_data


def update_viewer_data(viewer_data):
    with open(VIEWERS_FILE, "w") as jsonFile:
        json.dump(viewer_data, jsonFile)


def update_current_viewers(current_viewers_dict):
    with open(CURRENT_VIEWERS_FILE, "w") as current_viewer_file:
        json.dump(current_viewers_dict, current_viewer_file, indent=4)

def get_points(username):
    # read in the viewers.json file
    with open(VIEWERS_FILE, "r") as jsonFile:
            viewer_data = json.load(jsonFile)

    points = viewer_data[username]['points']
    message = 'No points yet. Your time will come.'

    return points


def set_points(username, amount):
    # read in the points file
    with open(VIEWERS_FILE, "r") as jsonFile:
            viewer_data = json.load(jsonFile)

    viewer_data[username]['points'] = amount

    # write updated points to file
    with open(VIEWERS_FILE, "w") as jsonFile:
        json.dump(viewer_data, jsonFile)
