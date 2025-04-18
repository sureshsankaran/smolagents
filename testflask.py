# test_flask.py
from flask import Flask, render_template
app = Flask(__name__)

# Serve the chat interface
@app.route('/')
def index():
    return render_template('index.html')

# Handle chat requests
@app.route('/chat', methods=['POST'])
def chat():
    try:
        print("Chat request received")
    except Exception as e:
        logging.error(f"Error processing prompt: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("starting app")
    app.run(debug=True, host='0.0.0.0', port=5001)