from flask import Flask, render_template, request, redirect, url_for
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ---------------- Config ---------------- #
UPLOAD_FOLDER = os.path.join('static', 'images')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ---------------- JSON Helper Functions ---------------- #
def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_data(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

# ---------------- Load Data ---------------- #
memories_file = 'memories.json'
stories_file = 'stories.json'
timeline_file = 'timeline.json'

memories = load_data(memories_file)
stories = load_data(stories_file)
timeline_events = load_data(timeline_file)

# ---------------- Routes ---------------- #

# Home page
@app.route("/")
def home():
    return render_template("index.html")

# Memories page
@app.route("/memories", methods=["GET", "POST"])
def memories_page():
    if request.method == "POST":
        file = request.files["photo"]
        caption = request.form["caption"]
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            memories.append({"file": filename, "caption": caption})
            save_data(memories_file, memories)  # Save permanently
        return redirect(url_for("memories_page"))
    return render_template("memories.html", memories=memories)

# Stories page
@app.route("/stories", methods=["GET", "POST"])
def stories_page():
    if request.method == "POST":
        file = request.files["photo"]
        caption = request.form["caption"]
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            stories.append({"file": filename, "caption": caption})
            save_data(stories_file, stories)  # Save permanently
        return redirect(url_for("stories_page"))
    return render_template("stories.html", stories=stories)

# Timeline page
@app.route("/timeline", methods=["GET", "POST"])
def timeline_page():
    if request.method == "POST":
        date = request.form["date"]
        title = request.form["title"]
        story = request.form["story"]
        file = request.files["photo"]
        filename = None
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        timeline_events.append({
            "date": date,
            "title": title,
            "story": story,
            "image": filename
        })
        timeline_events.sort(key=lambda x: x["date"], reverse=True)
        save_data(timeline_file, timeline_events)  # Save permanently
        return redirect(url_for("timeline_page"))
    return render_template("timeline.html", timeline_events=timeline_events)

# ---------------- Delete Routes ---------------- #
@app.route("/memories/delete/<int:index>", methods=["POST"])
def delete_memory(index):
    if 0 <= index < len(memories):
        memory = memories.pop(index)
        save_data(memories_file, memories)
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], memory["file"]))
        except:
            pass
    return redirect(url_for("memories_page"))

@app.route("/stories/delete/<int:index>", methods=["POST"])
def delete_story(index):
    if 0 <= index < len(stories):
        story = stories.pop(index)
        save_data(stories_file, stories)
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], story["file"]))
        except:
            pass
    return redirect(url_for("stories_page"))

@app.route("/timeline/delete/<int:index>", methods=["POST"])
def delete_timeline(index):
    if 0 <= index < len(timeline_events):
        event = timeline_events.pop(index)
        save_data(timeline_file, timeline_events)
        if event.get("image"):
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], event["image"]))
            except:
                pass
    return redirect(url_for("timeline_page"))

# ---------------- Run App ---------------- #
if __name__ == "__main__":
    app.run(debug=True)
