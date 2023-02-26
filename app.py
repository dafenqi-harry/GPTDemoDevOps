#from azure.devops.connection import Connection
#from msrest.authentication import BasicAuthentication
from flask import Flask, request, jsonify,render_template
#from azure.devops.connection import Connection
#from msrest.authentication import BasicAuthentication
#import azure
import openai
import os
import json
import requests

app = Flask(__name__)

ai_client = None
# 使用 OpenAI API
openai.api_key = os.getenv('API_KEY')
# 使用Azure OpenAI
#openai.api_key = "REPLACE_WITH_YOUR_API_KEY_HERE"
#openai.api_base =  "REPLACE_WITH_YOUR_ENDPOINT_HERE" # your endpoint should look like the following https://YOUR_RESOURCE_NAME.openai.azure.com/
#openai.api_type = 'azure'
#openai.api_version = '2022-12-01' 

# Class to get response from LLM API Server
class LLMClient:
    _ENDPOINT = 'https://httpqas26-frontend-qasazap-prod-dsm02p.qas.binginternal.com/completions'
    _SCOPES = ['api://68df66a4-cad9-4bfd-872b-c6ddde00d6b2/access']

    def __init__(self):
        #self._cache = msal.SerializableTokenCache()
        return None

    def send_stream_request(self, model_name, request):
        # get the token
        token = os.getenv('API_TOKEN')
        # populate the headers
        headers = {
            'Content-Type':'application/json', 
            'Authorization': 'Bearer ' + token, 
            'X-ModelType': model_name }

        body = str.encode(json.dumps(request))
        response = requests.post(LLMClient._ENDPOINT, data=body, headers=headers, stream=True)
        for line in response.iter_lines():
            text = line.decode('utf-8')
            if text.startswith('data: '):
                text = text[6:]
                if text == '[DONE]':
                    break
                else:
                    yield json.loads(text)       
    
    def get_response_from_request(self, prompt_str, model_name='text-davinci-003', max_tokens=1000, temperature=0.6):
        stream_request_data = {
            "prompt":prompt_str,
            "max_tokens":max_tokens,
            "temperature":temperature,
            "top_p":1,
            "n":1,
            "stream":True,
            "logprobs":None,
            "stop":"\r\n"
        }
        # get the model response
        # available models are:
        # text-davinci-001 (GPT-3)
        # text-davinci-002 (GPT-3.5)
        # text-davinci-003 (GPT-3.51)
        # text-chat-davinci-002 (ChatGPT)
        # response = self.send_request('text-davinci-002', stream_request_data)

        retstr = ''
        for response in self.send_stream_request(model_name, stream_request_data):
            retstr += response['choices'][0]['text']
        print('Calling LLM!\n')
        return retstr

# Class to get response from OpenAI API Server
class OpenAIClient:

    def __init__(self):
        # Null
        return None

    def get_response_from_request(self, prompt_str, model_name='text-davinci-003', max_tokens=1024, temperature=0.6):
        request_data = {
            "prompt":prompt_str,
            "max_tokens":max_tokens,
            "temperature":temperature,
            "top_p":1,
            "n":1,
            "stop":None
        }
        response = openai.Completion.create(request_data)
        retstr = response['choices'][0]['text'].strip()
        print('Calling OpenAI!\n')
        return retstr

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data['message']
    examples = str(data['examples']).strip()

    if examples.__len__() > 0:
        message_to_send = 'Examples:\n' + str(examples) + '\nPrompt:\n' + message
    else:
        message_to_send = message
    print(message_to_send)
    api_server_type = os.getenv('API_SERVER_TYPE')
    model_n = os.getenv('MODEL_NAME', 'text-davinci-003')
    if api_server_type == 'LLM':
        ai_client = LLMClient()
    else:
        ai_client = OpenAIClient()

    response = ai_client.get_response_from_request(message_to_send, model_name=model_n)
    
    answer = response
    print(answer)
    # return answer
    return jsonify({'answer': answer})

@app.route('/command', methods=['POST'])
def send_command():
    data = request.json
    print(data)
    command_body = data['command']

    if 'org' in command_body:
        print(command_body)
        org_name = command_body['org']
        project_name = command_body['proj']
        definition = command_body['definition']
        # org_name = 'xxxx'
        # project_name = 'yyy'
        # definition = 1
        command_line = "python3 callazuredevops.py " + org_name + " " + project_name + " " + str(definition)
        print(command_line)
        os.system(command_line)
        return jsonify({'answer': 'success'})


    print("No command to send")
    return jsonify({'answer': 'fail'})
    



if __name__ == '__main__':
    app.run()
