import json
import urllib.request
import urllib.parse

def formatData(data):
    data = data + '.json'
    formattedData = {
        "Records": [{
            "s3": {
                "configurationId": "testConfigRule",
                "object": {
                    "key": data,
                },
            "s3SchemaVersion": "1.0"
            },
        "awsRegion": "ap-northeast-2"
        }]
    }
    params = urllib.parse.urlencode(formattedData)
    print(params)
    return params

url = "https://gemq3v63g6.execute-api.ap-northeast-2.amazonaws.com/prod/image"
params = formatData("happy.json")

full_url = url + '?' + params

data = urllib.request.urlopen(full_url)
print(urllib.parse.unquote(params))
print(data.read())


