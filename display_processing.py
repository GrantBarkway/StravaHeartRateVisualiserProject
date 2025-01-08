from flask import Flask, render_template, request
from get_activities import list_activites

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('User_input.html')

@app.route('/process', methods=['POST'])

# Retrieves user input from input field
def process():
    max_hr = request.form['max_hr_input']
    num_activities = request.form['number_of_activities_input']
    
    fetch_data = list_activites(int(max_hr), int(num_activities))
    activities = fetch_data[0]
    graph = fetch_data[1]
    
    return render_template('display.html', activities=activities, graph=graph)

if __name__ == '__main__':
    app.run(debug=True)
