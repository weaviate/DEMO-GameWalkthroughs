from project import helper
import glob
import os
import weaviate
from weaviate.exceptions import UnexpectedStatusCodeException


def populate_game():
    pass


def populate_video():
    client = weaviate.Client("http://localhost:8080")
    with open("video_links") as i:
        # todo: add batch
        for line in i:
            game_name, link = line.strip().split(';')
            print(f"game name: {game_name} | link: {link}")

            # todo: get or create game instance

            print("downloading video metadata")
            video_metadata = helper.extract_video_metadata(link)
            video = helper.generate_video(
                video_metadata["title"],
                video_metadata["youtubeId"],
                video_metadata["description"],
                video_metadata["duration"],
                video_metadata["viewCount"],

                # todo: add "ofGame"
            )

            client.create_thing(helper.extract_attribute(video), "Video", video["uuid"])

            print("download and scrap video subtitles")
            helper.scrap_video_autosub(link.strip())
            subtitle_list = glob.glob("*.vtt")

            if len(subtitle_list):
                subtitle_path = subtitle_list[0]
                extracted = helper.extract_autosub(subtitle_path)
                for e in extracted:
                    # todo: insert into graph
                    subtitle = helper.generate_subtitle(e[2], e[0], e[1])
                    try:
                        client.create_thing(helper.extract_attribute(subtitle), "Subtitle", subtitle["uuid"])
                    except UnexpectedStatusCodeException:
                        print("Exception on subtitles")
                        print(subtitle)

                os.remove(subtitle_path)
            else:
                print("no subtitle is found for this video")
            print()

def populate_article():
    with open("article_links") as i:
        for link in i:
            result = helper.scrap_article(link.strip())
            print(result)
            # todo: insert into graph

populate_video()
# populate_article()
