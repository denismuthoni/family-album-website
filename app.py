from flask import Flask, render_template, request, redirect, url_for
import os
import json
from werkzeug.utils import secure_filename
import cloudinary
import cloudinary.uploader
import cloudinary.api

app = Flask(__name__)

# ---------------- Config ---------------- #
UPLOAD_FOLDER = os.path.join('static', 'images')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Cloudinary config
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME', 'your_cloud_name'),
    api_key=os.environ.get('CLOUDINARY_API_KEY', 'your_api_key'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET', 'your_api_secret')
)

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
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(file)
            image_url = result['secure_url']
            memories.append({"file": image_url, "caption": caption})
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
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(file)
            image_url = result['secure_url']
            stories.append({"file": image_url, "caption": caption})
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
        image_url = None
        if file:
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(file)
            image_url = result['secure_url']
        timeline_events.append({
            "date": date,
            "title": title,
            "story": story,
            "image": image_url
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
        # Note: Cloudinary images persist, no need to delete
    return redirect(url_for("memories_page"))

@app.route("/stories/delete/<int:index>", methods=["POST"])
def delete_story(index):
    if 0 <= index < len(stories):
        story = stories.pop(index)
        save_data(stories_file, stories)
        # Note: Cloudinary images persist, no need to delete
    return redirect(url_for("stories_page"))

@app.route("/timeline/delete/<int:index>", methods=["POST"])
def delete_timeline(index):
    if 0 <= index < len(timeline_events):
        event = timeline_events.pop(index)
        save_data(timeline_file, timeline_events)
        # Note: Cloudinary images persist, no need to delete
    return redirect(url_for("timeline_page"))

# ---------------- Run App ---------------- #
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
