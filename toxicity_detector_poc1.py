import socket
import dash
from dash import dcc, html
import plotly.express as px
import datetime
from detoxify import Detoxify
import pandas as pd

# Initialize the toxicity detector
toxicity_detector = Detoxify("original")

# my existing data
data = {
    "timestamp": [datetime.datetime(2023, 1, i+1) for i in range(10)],
    "sender": ["Alice", "Bob", "Alice", "Charlie", "Bob", 
               "Charlie", "Alice", "Bob", "Charlie", "Alice"],
    "message": [
        "Great work team!",
        "You're not meeting expectations",
        "Let's collaborate on this",
        "This is unacceptable",
        "Nice job yesterday",
        "Why can't you do anything right?",
        "I appreciate your effort",
        "You're useless",
        "We're making good progress",
        "This place is toxic"
    ],
    "toxicity_score": [0.1, 0.8, 0.2, 0.9, 0.1, 0.95, 0.2, 0.85, 0.3, 0.97]
}

# create dataFrame
df = pd.DataFrame(data)
print(df)
print(df.columns)

app = dash.Dash(__name__)


# function to analyze toxicity
def analyze_toxicity(text):
    results = toxicity_detector.predict(text)

    # Return the highest toxicity score among all categories
    return max(results.values())

# Add toxicity analysis to DataFrame
df["toxicity_score"] = df["message"].apply(analyze_toxicity)
df["is_toxic"] = df["toxicity_score"] > 0.5 # flag if score is > 50%

# Display result
print(df[["message", "sender", "toxicity_score", "is_toxic"]])

# Create visualization
fig_time = px.bar(df, x="timestamp", y="toxicity_score",
                 title="Toxicity Level Over Time",
                 labels={"toxicity_score": "Toxicity Score"})

fig_sender = px.box(df, x="sender", y="toxicity_score",
                   title="Toxicity Distribution by Sender",
                   color="sender")

# Advanced NLP Analysis
#import spacy
#nlp = spacy.load("en_core_web_lg")

#def detect_exclusion(text):
    #doc = nlp(text)
    #exclusion_keywords = ["exclude", "not needed", "ignore", "without you"]
    #return any (keyword in text.lower() for keyword in exclusion_keywords)
#df["is_exclusionary"] = df["message"].apply(detect_exclusion)



app = dash.Dash(__name__)

# calculate toxicity count for each timestamp
toxicity_counts = [len(t) if isinstance(t, list) else 0 for t in df["toxicity_score"]]

#plot toxicity trends
fig = px.bar(df, x="timestamp", y=toxicity_counts,
             title="Toxicity Messages Over Time",
             labels={"y": "Number of Toxic Elements"})

app.layout = html.Div([
    html.H1("Workplace Toxicity Monitor"),
    
    # First row with two graphs
    html.Div([
        html.Div([
            dcc.Graph(figure=fig_time)
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Graph(figure=fig_sender)
        ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
    ]),
    
    # Message details table
    html.H3("Message Details"),
    html.Table([
        html.Thead(
            html.Tr([
                html.Th("Timestamp"),
                html.Th("Sender"),
                html.Th("Message"), 
                html.Th("Toxicity Score")
            ])
        ),
        html.Tbody([
            html.Tr([
                html.Td(row["timestamp"].strftime("%Y-%m-%d %H:%M")),
                html.Td(row["sender"]),
                html.Td(row["message"]),
                html.Td(f"{row['toxicity_score']:.2f}")
            ])
            for _, row in df.iterrows()
        ])
    ], style={
        'margin': '20px', 
        'width': '100%',
        'border': '1px solid #ddd',
        'border-collapse': 'collapse'
    })
], style={'padding': '20px'})

# Get local IP address
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

if __name__ == '__main__':
    local_ip = get_local_ip()
    print(f"Access on your phone: http://{local_ip}:8050")
    print("On same WiFi network!")
    app.run(debug=True, host='0.0.0.0', port=8050)