from project import helper, create_schema
import glob
import os
import weaviate
from weaviate.exceptions import UnexpectedStatusCodeException


def populate_game():
    manager = helper.Manager(weaviate.Client("http://localhost:8080"))
    with open("data/games") as i:
        for line in i:
            game_name, game_developer, raw_genres, raw_platforms = [e.strip() for e in line.strip().split(';')]
            raw_genres = [e.strip() for e in raw_genres.split(',')]
            raw_platforms = [e.strip() for e in raw_platforms.split(',')]

            game_genres = []
            game_platforms = []

            for platform_name in raw_platforms:
                created, platform = manager.get_or_create_platform(platform_name)
                game_platforms.append(platform)
                print(f"Get or Create Platform: {platform_name}, created: {created}, dict: {platform}")

            for genre_name in raw_genres:
                created, genre = manager.get_or_create_genre(genre_name)
                game_genres.append(genre)
                print(f"Get or Create Genre: {genre_name}, created: {created}, dict: {genre}")

            game = manager.create_game(game_name, game_developer,
                                        [e.get('uuid') for e in game_genres],
                                        [e.get('uuid') for e in game_platforms])
            print(game)


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
