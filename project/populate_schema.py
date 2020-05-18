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

def scrap_video():
    pass


# print(scrap_article(('https://www.gamesradar.com/gta-5-guide/')))
