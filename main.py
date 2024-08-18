import logging
import string
from openai import OpenAI
import json
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import requests
from pymongo import MongoClient
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
openAI_client = OpenAI()



uri = "mongodb+srv://farhan2323fa:EeV0ORVTs0jbQ48m@cluster0.tsgib.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


db = client['url_summary_db'] 
collection = db["summaries"]
doc = {'title' : 'test' , 'summary' : 'teset'}
#collection.insert_one(doc)



def load_json_schema(schema_file: str) -> dict:
    with open(schema_file, 'r') as file:
        return json.load(file)


@app.route('/health-check')
def health_check():
    logger.info("in health check")
    return jsonify({"message": "Hello World!"})


@app.route('/scrape', methods=['POST'])
def scraper():
    logger.info('in web scraper')
    data = request.get_json()
    logger.info('date: ' + str(data))
    url = data['url']


    response = requests.get(url)
    content = response.text
    schema = load_json_schema('schema.json')
    logger.info('schema before: ' + str(schema))
    data_types = data['dataTypes']
    logger.info('data types: ' + str(data_types))
    for data_type in data_types:
        schema['properties'][data_type] = {}
        schema['properties'][data_type]['type'] = 'string'
        schema['properties'][data_type]['description'] = data_type

    logger.info('schema after: ' + str(schema))
    response = openAI_client.chat.completions.create(
    model='gpt-4o-mini',
    response_format={"type": "json_object"},
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Extract the properties from this image using the following JSON Schema as a guide: " +
                    json.dumps(schema)},
                {
                    "type": "text",
                    "text": content
                }
            ],
        }
    ],
    max_tokens=500,
)
   

    logger.info(response.choices[0].message.content)
    json_data = json.loads(response.choices[0].message.content)
    logger.info('js data: ' + str(json_data))
    logger.info('TITLE HERE LOOK ' + str(json_data['title']))
    collection.insert_one({'url': url, 'title': json_data['title'], 'summary': json_data['summary']})
    logger.info("Title and summary successfully stored in MongoDB!")


    return json_data




if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5123))
    app.run(host='0.0.0.0', port=port, debug=True)