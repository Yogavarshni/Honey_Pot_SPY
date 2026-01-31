from pydantic import BaseModel
import json
from flask import Flask, request, Response, jsonify, send_file
from typing import List, Dict, Any
 
import os, json
import pandas as pd
from utils import *
from flask_cors import cross_origin
from flask import Flask, request, jsonify
from flask_cors import CORS
from graph import build_honey_pot


graph = build_honey_pot()
app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes by default
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

@app.route('/')
def health_check():
    return jsonify({'status': 'Flask is running'}), 200
 
@app.route('/invocataion', methods = ['POST'])
@cross_origin()
def fetch_policy_id():
    data = request.get_json()
    global input_message 
    input_message = data.get('input_message')
    if input_message:
        graph, state = build_honey_pot()
        state['input_message'] = input_message
        result = graph.invoke(state)
        return jsonify(result['final_payload'])
    else:
        return jsonify({'error': 'Try again'}), 404  

if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug = True, port = 8004, use_reloader = False)
 