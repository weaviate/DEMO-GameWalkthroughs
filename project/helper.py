import uuid

def generate_id():
    return str(uuid.uuid1())

def extract_attribute(d):
    return {k: d[k] for k in d.keys() if k != "uuid"}

def generate_platform(name, has_games=None):
    return {
        "uuid": generate_id(),
        "name": name,
        "hasGames": has_games if has_games else []
    }

def generate_genre(name, has_games=None):
    return {
        "uuid": generate_id(),
        "name": name,
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

def generate_subtitle(text, start_time, end_time, ofGame=None):
    return {
        "uuid": generate_id(),
        "text": text,
        "startTime": start_time,
        "endTime": end_time,
        "ofGame": ofGame if ofGame else [],
    }

def generate_tag(name, hasGames=None):
    return {
        "uuid": generate_id(),
        "name": name,
        "hasGames": hasGames if hasGames else [],
    }

def generate_video(title, youtube_id, description, duration, view_count, ofGame=None, hasTags=None, hasSubs=None):
    return {
        "uuid": generate_id(),
        "title": title,
        "youtubeId": youtube_id,
        "description": description,
        "duration": duration,
        "viewCount": view_count,

        "ofGame": ofGame if ofGame else [],
        "hasTags": hasTags if hasSubs else [],
        "hasSubs": hasSubs if hasSubs else [],
    }