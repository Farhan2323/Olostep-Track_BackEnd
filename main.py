import logging
from openai import OpenAI
import json
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import requests


app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
client = OpenAI()


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
    response = client.chat.completions.create(
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
    return json_data









if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5123))
    app.run(host='0.0.0.0', port=port, debug=True)