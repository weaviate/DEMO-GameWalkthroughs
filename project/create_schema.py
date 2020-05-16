import weaviate.exceptions

def create_game_schema():
    """
    Create a game schema according to game_schema.json, if container did not contains any schema
    :return:
    """
    client = weaviate.Client("http://localhost:8080")
    if not client.contains_schema():
        client.create_schema("game_schema.json")
    else:
        print("Weaviate container already contained a schema")

if __name__ == "__main__":
    create_game_schema()
