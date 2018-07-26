class APPNAME(object):
    SEARCHWORD = "searchWord"

class HTML(object):
    HOME = "home.html"
    LOADING = "loading.html"
    AFTER_SEARCHING_WORD = "afterSearchingWord.html"

class KEY(object):
    QUERY_WORD = "queryWord"
    IMAGES = "images"

class URL(object):
     PUT_IMAGES_TO_S3 = "https://gemq3v63g6.execute-api.ap-northeast-2.amazonaws.com/prod/image"
     GET_IMAGES_FROM_S3 = "https://gemq3v63g6.execute-api.ap-northeast-2.amazonaws.com/prod/image"
     ICRAWLER_TRIGGER = "https://eh60oviexk.execute-api.ap-northeast-2.amazonaws.com/dev/prod/image/icrawl/trigger"

