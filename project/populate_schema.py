import newspaper
import youtube_dl
import re

def scrap_article(article_link):
    article = newspaper.Article(article_link)
    article.download()
    article.parse()

    raw_paragraph = article.text
    paragraph_list = [p for p in raw_paragraph.split("\n") if p]
    return {
        "title": article.title,
        "paragraph_list": paragraph_list
    }

def scrap_video(video_url):
    ydl_opts = {
        "writeautomaticsub": True,
        "skip_download": True,
        "quiet": True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

def extract_autosub(subtitle_path):
    with open(subtitle_path) as i:
        raw_text = i.read()
        return re.findall("(\d\d:\d\d:\d\d\.\d\d\d) --> (\d\d:\d\d:\d\d\.\d\d\d).+\n(.{2,})\n", raw_text)


# print(scrap_article(('https://www.gamesradar.com/gta-5-guide/')))

# scrap_video('https://www.youtube.com/watch?v=Vncf_9LLagc') # gta
# scrap_video('https://www.youtube.com/watch?v=BaW_jenozKc') # ytdl example video

# process_autosub("autosub.vtt")
extract_autosub("autosub.vtt")