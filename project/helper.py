import uuid
import newspaper
import youtube_dl
import re
import time
from weaviate.exceptions import UnexpectedStatusCodeException


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

def scrap_article(article_link):
    article = newspaper.Article(article_link)
    article.download()
    article.parse()

    raw_paragraph = article.text
    paragraph_list = [p for p in raw_paragraph.split("\n") if p]
    return {
        "title": article.title,
        "paragraph_list": paragraph_list
    }

def scrap_video_autosub(video_url):
    ydl_opts = {
        "writeautomaticsub": True,
        "skip_download": True,
        "quiet": True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

def extract_video_metadata(video_url):
    ydl_opts = {
        "quiet": True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        meta = ydl.extract_info(video_url, download=False)
        return {
            'youtubeId': meta.get("id"),
            'title': meta.get("title"),
            'description': meta.get("description"),
            'duration': meta.get("duration"),
            'viewCount': meta.get("view_count"),
        }

def extract_autosub(subtitle_path):
    with open(subtitle_path) as i:
        raw_text = i.read()
        return re.findall("(\d\d:\d\d:\d\d\.\d\d\d) --> (\d\d:\d\d:\d\d\.\d\d\d).+\n(.{2,})\n", raw_text)


class Manager():
    def __init__(self, client):
        self.client = client

    def execute_query(self, query):
        return self.client.query(query)

    def get_platform_or_false(self, platform_name):
        result = self.execute_query(f"""
        {{
          Get {{
            Things {{
              Platform(where: {{
                path: ["name"],
                operator: Equal,
                valueString: "{platform_name}"
              }}) {{
                uuid
                name
              }}
            }}
          }}
        }}
        """)
        platforms = result['data']['Get']['Things']['Platform']
        if len(platforms):
            return platforms[0]
        else:
            return False

    def get_or_create_platform(self, platform_name):
        platform = self.get_platform_or_false(platform_name)
        if platform == False:
            platform = generate_platform(platform_name, [])
            self.client.create_thing(extract_attribute(platform), "Platform", platform["uuid"])
            return True, platform
        return False, platform

    def get_genre_or_false(self, genre_name):
        result = self.execute_query(f"""
        {{
          Get {{
            Things {{
              Genre(where: {{
                path: ["name"],
                operator: Equal,
                valueString: "{genre_name}"
              }}) {{
                uuid
                name
              }}
            }}
          }}
        }}
        """)
        genre = result['data']['Get']['Things']['Genre']
        if len(genre):
            return genre[0]
        else:
            return False

    def get_or_create_genre(self, genre_name):
        genre = self.get_genre_or_false(genre_name)
        if genre == False:
            genre = generate_genre(genre_name, [])
            self.client.create_thing(extract_attribute(genre), "Genre", genre["uuid"])
            return True, genre
        return False, genre

    def create_game(self, name, developer, ofGenre=None, onPlatform=None):
        game_dict = {
            "uuid": generate_id(),
            "name": name,
            "developer": developer,
        }
        self.client.create_thing(extract_attribute(game_dict), "Game", game_dict["uuid"])

        time.sleep(2)

        if ofGenre:
            for genre_uuid in ofGenre:
                self.client.add_reference_to_thing(game_dict["uuid"], "ofGenre", genre_uuid)
                self.client.add_reference_to_thing(genre_uuid, "hasGames", game_dict["uuid"])

        if onPlatform:
            for platform_uuid in onPlatform:
                self.client.add_reference_to_thing(game_dict["uuid"], "onPlatform", platform_uuid)
                self.client.add_reference_to_thing(platform_uuid, "hasGames", game_dict["uuid"])

        return game_dict

    def get_game_or_false(self, game_name):
        result = self.execute_query(f"""
        {{
          Get {{
            Things {{
              Game(where: {{
                path: ["name"],
                operator: Equal,
                valueString: "{game_name}"
              }}) {{
                uuid
                name
                developer
                OfGenre {{
                  ... on Genre {{
                    uuid
                    name
                  }}
                }}
                OnPlatform {{
                  ... on Platform {{
                    uuid
                    name
                  }}
                }}
              }}
            }}
          }}
        }}
        """)
        genre = result['data']['Get']['Things']['Game']
        if len(genre):
            return genre[0]
        else:
            return False

    def get_video_or_false(self, youtube_id):
        result = self.execute_query(f"""
        {{
          Get {{
            Things {{
              Video(where: {{
                path: ["youtubeId"],
                operator: Equal,
                valueString: "{youtube_id}"
              }}) {{
                uuid
                title
                duration
                youtubeId
                viewCount
              }}
            }}
          }}
        }}
        """)

        videos = result['data']['Get']['Things']['Video']
        if len(videos):
            return videos[0]
        else:
            return False

    def create_video(self, title, youtube_id, description, duration, view_count, ofGame=None, hasTags=None, hasSubs=None):
        video_dict = {
            "uuid": generate_id(),
            "title": title,
            "youtubeId": youtube_id,
            "description": description,
            "duration": duration,
            "viewCount": view_count,
        }

        self.client.create_thing(extract_attribute(video_dict), "Video", video_dict["uuid"])

        time.sleep(2)

        if ofGame:
            for game_uuid in ofGame:
                self.client.add_reference_to_thing(video_dict["uuid"], "ofGame", game_uuid)

        if hasTags:
            for tag_uuid in hasTags:
                self.client.add_reference_to_thing(video_dict["uuid"], "hasTags", tag_uuid)

        if hasSubs:
            for subtitle_uuid in hasSubs:
                self.client.add_reference_to_thing(video_dict["uuid"], "hasSubs", subtitle_uuid)

        return video_dict

    def create_subtitle(self, text, start_time, end_time):
        subtitle_dict = {
            "uuid": generate_id(),
            "text": text,
            "startTime": start_time,
            "endTime": end_time,
        }

        try:
            self.client.create_thing(extract_attribute(subtitle_dict), "Subtitle", subtitle_dict["uuid"])
            return subtitle_dict
        except UnexpectedStatusCodeException:
            print("Exception on subtitles")
            print(subtitle_dict)

    def add_reference_of_game_subtitle(self, game_uuid, subtitle_uuids=None):
        if subtitle_uuids:
            for subtitle_uuid in subtitle_uuids:
                self.client.add_reference_to_thing(subtitle_uuid, "ofGame", game_uuid)

    def add_reference_has_subs(self, video_uuid, subtitle_uuids=None):
        if subtitle_uuids:
            for subtitle_uuid in subtitle_uuids:
                self.client.add_reference_to_thing(video_uuid, "hasSubs", subtitle_uuid)

