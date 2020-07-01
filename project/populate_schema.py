from project import helper, create_schema
import glob
import os
import weaviate
from weaviate.exceptions import UnexpectedStatusCodeException


def populate_game():
    manager = helper.Manager(weaviate.Client("http://localhost:8080"))
    platform_dict = {}
    genre_dict = {}

    with open("data/games") as i:
        for line in i:
            game_name, developer, genres, platforms = [e.strip() for e in line.strip().split(';')]
            genres = [e.strip() for e in genres.split(',')]
            platforms = [e.strip() for e in platforms.split(',')]

            print(game_name)
            print(developer)
            print(genres)
            print(platforms)

            for platform_name in platforms:
                created, platform = manager.get_or_create_platform(platform_name)
                if created:
                    platform_dict[platform_name] = platform
                print(platform_name, created, platform)

            for genre_name in genres:
                created, genre = manager.get_or_create_genre(genre_name)
                if created:
                    genre_dict[genre_name] = genre
                print(genre_name, created, genre)

            # todo: get or create platforms
            # todo: get or create genres
            # todo: get or create game
            exit()



def populate_video():
    client = weaviate.Client("http://localhost:8080")
    with open("data/video_links") as i:
        # todo: add batch
        for line in i:
            game_name, link = line.strip().split(';')
            print(f"game name: {game_name} | link: {link}")

            # todo: get or create game instance
            # return

            print("downloading video metadata")
            video_metadata = helper.extract_video_metadata(link)
            video = helper.generate_video(
                video_metadata["title"],
                video_metadata["youtubeId"],
                video_metadata["description"],
                video_metadata["duration"],
                video_metadata["viewCount"],

            )
            # todo: add reference "ofGame" to Game

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
                        client.add_reference_to_thing(video["uuid"], "hasSubs", subtitle["uuid"])
                    except UnexpectedStatusCodeException:
                        print("Exception on subtitles")
                        print(subtitle)

                os.remove(subtitle_path)
            else:
                print("no subtitle is found for this video")
            print()

# def populate_article():
#     with open("data/article_links") as i:
#         for link in i:
#             result = helper.scrap_article(link.strip())
#             print(result)
#             # todo: insert into graph

if __name__ == "__main__":
    create_schema.create_game_schema()
    populate_game()
    # populate_video()
    # populate_article()
