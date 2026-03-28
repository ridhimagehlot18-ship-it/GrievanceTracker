from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Backend is running 🚀"

@app.route('/submit', methods=['POST'])
def submit_issue():
    data = request.json
    
    issue = {
        "name": data.get("name"),
        "location": data.get("location"),
        "issue": data.get("issue"),
        "status": "Pending"
    }
    
    return jsonify({
        "message": "Issue submitted successfully",
        "data": issue
    })

if __name__ == '__main__':
    app.run(debug=True)
