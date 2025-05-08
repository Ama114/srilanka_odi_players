from flask import Flask, render_template, request
import pandas as pd
import joblib
import os
 
app = Flask(__name__)

# Load the model and data
model_bundle = joblib.load("full_player_performance_model.pkl")
 
df = pd.read_csv("srilanka_ODI_Stats.csv", encoding="ISO-8859-1")
df["Runs"] = pd.to_numeric(df["Runs"], errors="coerce")
df.dropna(subset=["Runs"], inplace=True)
df[["Player Name", "Ground", "Opposition", "Dismissal"]] = df[["Player Name", "Ground", "Opposition", "Dismissal"]].astype(str).apply(lambda x: x.str.strip().str.lower())

# For dropdowns
player_names = sorted(df["Player Name"].unique())
ground_names = sorted(df["Ground"].unique())

def get_actual_stats(player, ground):
    filtered_df = df[(df["Player Name"] == player) & (df["Ground"] == ground)]
    if filtered_df.empty:
        return {"message": "No data found."}

    total_runs = filtered_df["Runs"].sum()
    average_runs = filtered_df["Runs"].mean()
    most_common_dismissal = filtered_df["Dismissal"].value_counts().idxmax()
    opposition_group = filtered_df.groupby("Opposition")["Runs"].sum()
    top_opposition = opposition_group.idxmax()
    top_opposition_runs = opposition_group.max()

    return {
        "Player": player.title(),
        "Ground": ground.title(),
        "Total Runs at Ground": int(total_runs),
        "Average Runs": round(average_runs, 2),
        "Most Common Dismissal": most_common_dismissal,
        "Top Opposition at Ground": top_opposition,
        "Runs Against Top Opposition": int(top_opposition_runs)
    } 

 


@app.route('/', methods=['GET', 'POST'])
def index():
    player_names = sorted(df["Player Name"].unique())
    ground_names = sorted(df["Ground"].unique())
    result = None
    selected_player = None
    selected_ground = None
    image_path = None

    if request.method == 'POST':
        selected_player = request.form['player']
        selected_ground = request.form['ground']
        result = get_actual_stats(selected_player, selected_ground)

        image_filename = selected_player.lower().replace(" ", "_") + ".jpg"
        image_path = f"images/{image_filename}"
       # image_path = os.path.join("images", image_filename)
       # player_image = image_path
    
    #else:
        #player_image = None

    # ✅ Update the return to include 'player_image'
    return render_template("index.html", player_names=player_names, ground_names=ground_names,
                       result=result, selected_player=selected_player, selected_ground=selected_ground, player_image=image_path)
                     #  player_image=player_image)

if __name__ == "__main__":
    app.run(debug=True)
