import weaviate.exceptions
import time


def create_game_schema():
    """
    Create a game schema according to game_schema.json, if container did not contains any schema
    :return:
    """
    client = weaviate.Client("http://localhost:8080")
    if not client.is_reachable():
        raise Exception("Container is not reachable")
    if not client.contains_schema():
        print("Creating schema")
        time.sleep(10)
        client.create_schema("project/game_schema.json")
        time.sleep(10)
        print("Done Creating schema")
    else:
        print("Weaviate container already contained a schema")

if __name__ == "__main__":
    create_game_schema()
    # todo: make article scheme
