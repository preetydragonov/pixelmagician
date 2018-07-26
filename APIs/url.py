import boto3

s3_resource = boto3.resource('s3')
my_bucket = s3_resource.Bucket('searched-words')
for object_summary in my_bucket.objects.filter(Prefix="icrawler/images/happy/pixeled/"):
        print (object_summary.key)
