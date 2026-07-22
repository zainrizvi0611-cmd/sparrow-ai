from flask import Flask, request, jsonify
from god_mode_final import NoRefusalGod

app = Flask(__name__)
agent = NoRefusalGod()

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    query = data.get('query', '')
    response = agent.run(query)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
