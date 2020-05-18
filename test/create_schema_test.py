import unittest
import weaviate
from project.create_schema import create_game_schema
from project import helper
import time

class TestCreateGameSchema(unittest.TestCase):

    def setUp(self) -> None:
        create_game_schema()
        self.client = weaviate.Client("http://localhost:8080")

    def test_schema_created(self):
        self.assertTrue(self.client.contains_schema(), "Container should already contain schema")

        schema = self.client.get_schema()
        self.assertIsNotNone(schema)

        class_list = schema.get("things").get("classes")
        self.assertIsNotNone(class_list)
        self.assertEqual({'Game', 'Subtitle', 'Tag', 'Video', 'Platform', 'Genre'}, set([e.get("class") for e in class_list]))

    def test_create_simple_platform(self):
        platform1 = helper.generate_platform("Platform 1", [])
        self.client.create_thing(helper.extract_attribute(platform1), "Platform", platform1["uuid"])

        time.sleep(2)

        output_platform1 = self.client.get_thing(platform1["uuid"])
        self.assertEqual(output_platform1.get("class"), "Platform")
        self.assertEqual(output_platform1.get("id"), platform1["uuid"])
        self.assertEqual(output_platform1.get("schema").get("name"), platform1["name"])
        self.assertEqual(output_platform1.get("schema").get("hasGames"), platform1["hasGames"])

        delete_output = self.client.delete_thing(platform1["uuid"])
        self.assertIsNone(delete_output)

    def test_create_simple_genre(self):
        platform1 = helper.generate_genre("Genre 1", [])
        self.client.create_thing(helper.extract_attribute(platform1), "Genre", platform1["uuid"])

        time.sleep(2)

        output_genre1 = self.client.get_thing(platform1["uuid"])
        self.assertEqual(output_genre1.get("class"), "Genre")
        self.assertEqual(output_genre1.get("id"), platform1["uuid"])
        self.assertEqual(output_genre1.get("schema").get("name"), platform1["name"])
        self.assertEqual(output_genre1.get("schema").get("hasGames"), platform1["hasGames"])

        delete_output = self.client.delete_thing(platform1["uuid"])
        self.assertIsNone(delete_output)

    def test_create_simple_subtitle(self):
        subtitle1 = helper.generate_subtitle("Subtitle 1", 1, 2)
        self.client.create_thing(helper.extract_attribute(subtitle1), "Subtitle", subtitle1["uuid"])

        time.sleep(2)

        output_subtitle1 = self.client.get_thing(subtitle1["uuid"])
        self.assertEqual(output_subtitle1.get("class"), "Subtitle")
        self.assertEqual(output_subtitle1.get("id"), subtitle1["uuid"])
        self.assertEqual(output_subtitle1.get("schema").get("text"), subtitle1["text"])
        self.assertEqual(output_subtitle1.get("schema").get("startTime"), subtitle1["startTime"])
        self.assertEqual(output_subtitle1.get("schema").get("endTime"), subtitle1["endTime"])
        self.assertEqual(output_subtitle1.get("schema").get("ofGame"), subtitle1["ofGame"])

        delete_output = self.client.delete_thing(subtitle1["uuid"])
        self.assertIsNone(delete_output)

    def test_create_simple_tag(self):
        tag1 = helper.generate_tag("Tag 1", [])
        self.client.create_thing(helper.extract_attribute(tag1), "Tag", tag1["uuid"])

        time.sleep(2)

        output_tag1 = self.client.get_thing(tag1["uuid"])
        self.assertEqual(output_tag1.get("class"), "Tag")
        self.assertEqual(output_tag1.get("id"), tag1["uuid"])
        self.assertEqual(output_tag1.get("schema").get("name"), tag1["name"])
        self.assertEqual(output_tag1.get("schema").get("hasGames"), tag1["hasGames"])

        delete_output = self.client.delete_thing(tag1["uuid"])
        self.assertIsNone(delete_output)

    def test_create_simple_game(self):
        game1 = helper.generate_game("Game 1", "Developer 1", [], [])
        self.client.create_thing(helper.extract_attribute(game1), "Game", game1["uuid"])

        time.sleep(2)

        output_game1 = self.client.get_thing(game1["uuid"])
        self.assertEqual(output_game1.get("class"), "Game")
        self.assertEqual(output_game1.get("id"), game1["uuid"])
        self.assertEqual(output_game1.get("schema").get("name"), game1["name"])
        self.assertEqual(output_game1.get("schema").get("developer"), game1["developer"])
        self.assertEqual(output_game1.get("schema").get("ofGenre"), game1["ofGenre"])
        self.assertEqual(output_game1.get("schema").get("onPlatform"), game1["onPlatform"])

        delete_output = self.client.delete_thing(game1["uuid"])
        self.assertIsNone(delete_output)

    def test_create_simple_video(self):
        video1 = helper.generate_video("Title 1", "123", "Description", 60, 100, [], [], [])
        self.client.create_thing(helper.extract_attribute(video1), "Video", video1["uuid"])

        time.sleep(2)

        output_video1 = self.client.get_thing(video1["uuid"])
        self.assertEqual(output_video1.get("class"), "Video")
        self.assertEqual(output_video1.get("id"), video1["uuid"])
        self.assertEqual(output_video1.get("schema").get("title"), video1["title"])
        self.assertEqual(output_video1.get("schema").get("youtubeId"), video1["youtubeId"])
        self.assertEqual(output_video1.get("schema").get("description"), video1["description"])
        self.assertEqual(output_video1.get("schema").get("duration"), video1["duration"])
        self.assertEqual(output_video1.get("schema").get("viewCount"), video1["viewCount"])
        self.assertEqual(output_video1.get("schema").get("ofGame"), video1["ofGame"])
        self.assertEqual(output_video1.get("schema").get("hasTags"), video1["hasTags"])
        self.assertEqual(output_video1.get("schema").get("hasSubs"), video1["hasSubs"])

        delete_output = self.client.delete_thing(video1["uuid"])
        self.assertIsNone(delete_output)

    def test_create_platform_game_relation(self):
        game = helper.generate_game("Game 1", "Developer 1")
        platform = helper.generate_platform("Platform 1")

        self.client.create_thing(helper.extract_attribute(game), "Game", game["uuid"])
        self.client.create_thing(helper.extract_attribute(platform), "Platform", platform["uuid"])

        time.sleep(2)

        self.client.add_reference_to_thing(platform["uuid"], "hasGames", game["uuid"])
        self.client.add_reference_to_thing(game["uuid"], "onPlatform", platform["uuid"])

        time.sleep(2)

        output_platform = self.client.get_thing(platform["uuid"])
        output_game = self.client.get_thing(game["uuid"])

        platform_schema = output_platform.get("schema")
        game_schema = output_game.get("schema")

        self.assertEqual(len(platform_schema.get("hasGames")), 1)
        self.assertEqual(len(game_schema.get("onPlatform")), 1)
        self.assertIn(platform["uuid"], game_schema.get("onPlatform")[0]["href"])
        self.assertIn(game["uuid"], platform_schema.get("hasGames")[0]["href"])

        delete_platform = self.client.delete_thing(platform["uuid"])
        delete_game = self.client.delete_thing(game["uuid"])
        self.assertIsNone(delete_platform)
        self.assertIsNone(delete_game)


