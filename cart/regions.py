
# store region names and their map coordinates
REGIONS = {
    "northeast": {
        "name": "Northeast",
        "lat": 42.8,
        "lng": -73.5
    },
    "southeast": {
        "name": "Southeast",
        "lat": 33.5,
        "lng": -83.5
    },
    "midwest": {
        "name": "Midwest",
        "lat": 41.9,
        "lng": -89.0
    },
    "southwest": {
        "name": "Southwest",
        "lat": 34.1,
        "lng": -107.0
    },
    "west": {
        "name": "West",
        "lat": 39.2,
        "lng": -120.0
    }
}

# create choices for the region dropdown at checkout
REGION_CHOICES = [
    (key, value["name"])
    for key, value in REGIONS.items()
]
