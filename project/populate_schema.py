from project import helper
import glob
import os

def populate_video():
    with open("video_links") as i:
        for link in i:
            helper.scrap_video(link.strip())
            subtitle_list = glob.glob("*.vtt")
            if len(subtitle_list):
                subtitle_path = subtitle_list[0]
                extracted = helper.extract_autosub(subtitle_path)
                for e in extracted:
                    print(e)
                    # todo: insert into graph
                os.remove(subtitle_path)

def populate_article():
    with open("article_links") as i:
        for link in i:
            result = helper.scrap_article(link.strip())
            print(result)
            # todo: insert into graph

# populate_video()
# populate_article()