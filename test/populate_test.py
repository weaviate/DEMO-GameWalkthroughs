import unittest
import weaviate
from project.create_schema import create_game_schema
from project import helper
import time

class TestPopulateGameSchema(unittest.TestCase):

    get_video_with_ofGame = """
    {
      Get {
        Things {
          Video {
            uuid
            title
            duration
            viewCount
            youtubeId
            OfGame {
              ... on Game {
                uuid
                name
                developer
              }
            }
          }
        }
      }
    }
    """

    def setUp(self) -> None:
        create_game_schema()
        self.client = weaviate.Client("http://localhost:8080")
        self.manager = helper.Manager(self.client)
        self.uuid_list = []

    def tearDown(self) -> None:
        for uuid in self.uuid_list:
            self.client.delete_thing(uuid)
        super().tearDown()


    def test_get_or_create_platform(self):
        created, platform = self.manager.get_or_create_platform('Platform 1')
        self.uuid_list.append(platform['uuid'])
        self.assertTrue(created)

        time.sleep(2)

        created, platform = self.manager.get_or_create_platform('Platform 1')
        self.assertFalse(created)

    def test_get_platform_or_false(self):
        result = self.manager.get_platform_or_false('Platform 2')
        self.assertFalse(result)

        created, platform = self.manager.get_or_create_platform('Platform 2')
        self.uuid_list.append(platform['uuid'])
        self.assertTrue(created)

        time.sleep(2)

        result = self.manager.get_platform_or_false('Platform 2')
        self.assertTrue(result['uuid'] == platform['uuid'])

    def test_get_or_create_genre(self):
        created, genre = self.manager.get_or_create_genre('Genre 2')
        self.uuid_list.append(genre['uuid'])
        self.assertTrue(created)

        time.sleep(2)

        created, genre = self.manager.get_or_create_genre('Genre 2')
        self.assertFalse(created)

    def test_get_genre_or_false(self):
        result = self.manager.get_genre_or_false('Genre 1')
        self.assertFalse(result)

        created, genre = self.manager.get_or_create_genre('Genre 1')
        self.uuid_list.append(genre['uuid'])
        self.assertTrue(created)

        time.sleep(2)

        result = self.manager.get_genre_or_false('Genre 1')
        self.assertTrue(result['uuid'] == genre['uuid'])

    def test_crete_game_and_get_game_or_false(self):
        genre_created, genre = self.manager.get_or_create_genre('Genre 2')
        platform_created, platform = self.manager.get_or_create_platform('Platform 2')
        self.uuid_list.append(genre['uuid'])
        self.uuid_list.append(platform['uuid'])

        time.sleep(2)

        self.assertTrue(genre_created)
        self.assertTrue(platform_created)

        game = self.manager.create_game("Game 1", "Developer 1", ofGenre=[genre['uuid']], onPlatform=[platform['uuid']])
        self.uuid_list.append(game['uuid'])

        time.sleep(2)

        result = self.client.query("""
            {
              Get {
                Things {
                  Game {
                    uuid
                    name
                    developer
                    OfGenre {
                      ... on Genre {
                        uuid
                        name
                      }
                    }
                    OnPlatform {
                      ... on Platform {
                        uuid
                        name
                      }
                    }
                  }
                }
              }
            }
        """)
        self.assertEqual(result['data']['Get']['Things']['Game'][0]['OfGenre'][0]['uuid'], genre['uuid'])
        self.assertEqual(result['data']['Get']['Things']['Game'][0]['OnPlatform'][0]['uuid'], platform['uuid'])


        game_result = self.manager.get_game_or_false("Game 1")
        self.assertEqual(game_result['uuid'], game['uuid'])

    def test_crete_video_and_get_video_or_false(self):
        game = self.manager.create_game("Game 1", "Developer 1")
        self.uuid_list.append(game['uuid'])

        time.sleep(2)

        result = self.manager.get_video_or_false('video2')
        self.assertFalse(result)

        subtitle1 = self.manager.create_subtitle("subtitle 1", "1", "2")
        subtitle2 = self.manager.create_subtitle("subtitle 2", "2", "3")
        self.uuid_list.append(subtitle1['uuid'])
        self.uuid_list.append(subtitle2['uuid'])

        time.sleep(2)

        video = self.manager.create_video('Video 1', 'video2', "Description 1", 60, 100, ofGame=[game['uuid']], hasSubs=[subtitle1['uuid'], subtitle2['uuid']])
        self.uuid_list.append(video['uuid'])

        time.sleep(2)

        result = self.manager.get_video_or_false('video2')
        self.assertEqual(video['uuid'], result.get('uuid'))

        result = self.client.query("""
        {
          Get {
            Things {
              Video {
                uuid
                title
                OfGame {
                  ... on Game {
                    uuid
                    name
                    developer
                  }
                }
                HasSubs {
                  ... on Subtitle {
                    uuid
                    text
                    startTime
                    endTime
                  }
                }
              }
            }
          }
        }
        """)
        self.assertEqual(result['data']['Get']['Things']['Video'][0]['OfGame'][0]['uuid'], game['uuid'])
        self.assertEqual(result['data']['Get']['Things']['Video'][0]['HasSubs'][0]['uuid'], subtitle1['uuid'])
        self.assertEqual(result['data']['Get']['Things']['Video'][0]['HasSubs'][1]['uuid'], subtitle2['uuid'])
