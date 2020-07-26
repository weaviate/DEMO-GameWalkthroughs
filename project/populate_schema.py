from project import helper, create_schema
import glob
import os
import weaviate
import time


def populate_game(manager):
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

            game = manager.create_game(name=game_name,
                                       developer=game_developer,
                                       ofGenre=[e.get('uuid') for e in game_genres],
                                       onPlatform=[e.get('uuid') for e in game_platforms])
            print(f"Created Game: {game}")
            print()


def populate_video(manager):
    with open("data/video_links") as i:
        for line in i:
            game_name, link = line.strip().split(';')
            print(f"game name: {game_name} | link: {link}")

            game = manager.get_game_or_false(game_name)
            if game == False:
                raise Exception(f"Game {game_name} is not there yet. Please run populate_game() first.")

            print("downloading video metadata")
            video_metadata = helper.extract_video_metadata(link)

            video = manager.create_video(
                video_metadata["title"],
                video_metadata["youtubeId"],
                video_metadata["description"],
                video_metadata["duration"],
                video_metadata["viewCount"],
                ofGame=[game["uuid"]]
            )

            print("download and scrap video subtitles")
            helper.scrap_video_autosub(link.strip())
            subtitle_list = glob.glob("*.vtt")

            if len(subtitle_list):
                subtitle_path = subtitle_list[0]
                extracted = helper.extract_autosub(subtitle_path)

                print(f"Inserting {len(extracted)} subtitles")
                inserted_subtitle_uuids = []
                for e in extracted:
                    subtitle = manager.create_subtitle(text=e[2],
                                                       start_time=e[0],
                                                       end_time=e[1])
                    if subtitle is not None:
                        inserted_subtitle_uuids.append(subtitle["uuid"])

                time.sleep(2)

                # cross reference
                manager.add_reference_of_game_subtitle(game["uuid"], inserted_subtitle_uuids)
                manager.add_reference_has_subs(video["uuid"], inserted_subtitle_uuids)

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
    manager = helper.Manager(weaviate.Client("http://localhost:8080"))
    populate_game(manager)
    populate_video(manager)
    # populate_article()
