import requests
import plotly.express as px
import pandas as pd
import plotly.io as pio
from authorize_strava import load_tokens

# Credentials
CLIENT_ID = "redacted" #removed personal CLIENT_ID
CLIENT_SECRET = "redacted" #removed personal CLIENT_SECRET
REDIRECT_URI = "http://localhost:5000/callback"

# Fetch the user's activities
def fetch_activities(access_token):
    activities_url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(activities_url, headers=headers)
    response.raise_for_status()
    activities = response.json()
    return activities

# Fetch heart rate data for activity and properly round
def get_heartrate(max_heartrate_value, activity):
    if "average_heartrate" in activity:
        return (f"{activity['average_heartrate']} average HR "
        f"({(activity['average_heartrate'] / max_heartrate_value) * 100:.2f}% max) - "
        f"{activity['max_heartrate']} max HR "
        f"({(activity['max_heartrate'] / max_heartrate_value) * 100:.2f}% max)")
    else:
        return "No heartrate data"

# Determine what percent of time an activity is spent moving
def moving_ratio(activity):
    return (f"{round(activity['moving_time']/activity['elapsed_time'],4)*100:.2f}% Time moving")

# Create heartrate graph with plotly
def create_heartrate_graph(average_hr_list, max_hr_list, activity_date,max_heartrate_value):
    data = {
    "Date": activity_date * 2,
    "Heart Rate": average_hr_list + max_hr_list, 
    "Type": ["Average HR"] * len(activity_date) + ["Max HR"] * len(activity_date)
    }
    
    heartrate_dataframe = pd.DataFrame(data)
    
    heartrate_graph = px.line(heartrate_dataframe, x="Date", y="Heart Rate", color="Type", 
              title="Average and Maximum Heart Rate Over Time",
              labels={"Heart Rate": "Heart Rate", "Date": "Date"})
    
    # Add horizontal lines denoting heart rate zones on graph
    heartrate_graph.add_hline(y=max_heartrate_value*.5, line=dict(color="red", dash="dash"), annotation_text="50%", annotation_position="top left")
    heartrate_graph.add_hline(y=max_heartrate_value*.6, line=dict(color="red", dash="dash"), annotation_text="60%", annotation_position="top left")
    heartrate_graph.add_hline(y=max_heartrate_value*.7, line=dict(color="red", dash="dash"), annotation_text="70%", annotation_position="top left")
    heartrate_graph.add_hline(y=max_heartrate_value*.8, line=dict(color="red", dash="dash"), annotation_text="80%", annotation_position="top left")
    heartrate_graph.add_hline(y=max_heartrate_value*.9, line=dict(color="red", dash="dash"), annotation_text="90%", annotation_position="top left")
    heartrate_graph.add_hline(y=max_heartrate_value, line=dict(color="red", dash="dash"), annotation_text="Maximum", annotation_position="top left")
    
    graph_html = pio.to_html(heartrate_graph, full_html=False)
    
    return graph_html

def list_activites(max_heartrate_value, number_of_activities):
    # Get access token
    access_token = load_tokens()[0]
    
    average_hr_list = []
    max_hr_list = []
    activity_date = []
    list_of_formatted_data = []
    activities = fetch_activities(access_token)
    
    activities_with_hr = [activity for activity in activities if activity.get('has_heartrate', False)]
    
    for i, activity in enumerate(activities_with_hr[:number_of_activities], start=1):
        list_of_formatted_data.append(f"{activity['name']} - {activity['distance']} meters - {get_heartrate(max_heartrate_value, activity)} - {moving_ratio(activity)}")
        average_hr_list.append(activity['average_heartrate'])
        max_hr_list.append(activity['max_heartrate'])
        activity_date.append(activity['start_date'])
    
    hr_graph = create_heartrate_graph(average_hr_list, max_hr_list, activity_date, max_heartrate_value)
    return (list_of_formatted_data, hr_graph)



