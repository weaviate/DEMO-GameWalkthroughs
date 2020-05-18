import newspaper
import youtube_dl

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

def is_clean(text):
    if "-->" in text: return False
    if '<c>' in text: return False
    if text.strip() == "": return False
    return True

def remove_duplicated_sub(filtered_list):
    d = {}
    distinct = []

    for l in filtered_list:
        if l in d.keys():
            continue
        d[l] = True
        distinct.append(l)

    return distinct

def process_autosub(subtitle_path):
    with open(subtitle_path) as i:
        # cut several unused lines at the beginning of the file
        i.readline()
        i.readline()
        i.readline()

        raw_text = i.read()
        filtered_list = [e for e in raw_text.split("\n") if is_clean(e)]

        distinc_list = remove_duplicated_sub(filtered_list)

        for l in distinc_list:
            print(l)


# print(scrap_article(('https://www.gamesradar.com/gta-5-guide/')))

# scrap_video('https://www.youtube.com/watch?v=Vncf_9LLagc') # gta
# scrap_video('https://www.youtube.com/watch?v=BaW_jenozKc') # ytdl example video

process_autosub("autosub.vtt")