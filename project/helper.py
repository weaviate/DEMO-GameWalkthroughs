import uuid

def generate_id():
    return str(uuid.uuid1())

def extract_attribute(d):
    return {k: d[k] for k in d.keys() if k != "uuid"}

def generate_platform(platform_name, has_games=None):
    return {
        "uuid": generate_id(),
        "name": platform_name,
        "hasGames": has_games if has_games else []
    }

def generate_game(name, developer, ofGenre=None, onPlatform=None):
    return {
        "uuid": generate_id(),
        "name": name,
        "developer": developer,
        "ofGenre": ofGenre if ofGenre else [],
        "onPlatform": onPlatform if onPlatform else [],
    }