import weaviate.exceptions

try:
    client = weaviate.Client("http://localhost:8080")
    client.create_schema("game_schema.json")
except weaviate.exceptions.UnexpectedStatusCodeException as e:
    print(e.json)

