import boto3
import urllib.parse

s3_resource = boto3.resource('s3')
my_bucket = s3_resource.Bucket('searched-words')

def create_key_for_pixeled_image(url):
    rsplit_list = url.rsplit('/', 6)
    new_key = (rsplit_list[-6] + "/" +
               rsplit_list[-5] + "/" +
               urllib.parse.quote_plus(rsplit_list[-4]) + "/" +
               rsplit_list[-3] + "/" +
               rsplit_list[-2] + "/" +
               rsplit_list[-1])
    return new_key

for object_summary in my_bucket.objects.filter(Prefix="icrawler/images/" + "바보" + "/pixeled/"):
    encoded_key = create_key_for_pixeled_image(object_summary.key)

    url = "https://s3.ap-northeast-2.amazonaws.com/searched-words/" + encoded_key
    print(url)
