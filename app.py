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
HAS_CLOUDINARY = all([
    os.environ.get('CLOUDINARY_CLOUD_NAME'),
    os.environ.get('CLOUDINARY_API_KEY'),
    os.environ.get('CLOUDINARY_API_SECRET')
])

if HAS_CLOUDINARY:
    try:
        cloudinary.config(
            cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
            api_key=os.environ.get('CLOUDINARY_API_KEY'),
            api_secret=os.environ.get('CLOUDINARY_API_SECRET')
        )
        print("Cloudinary configured successfully")
    except Exception as e:
        print(f"Cloudinary configuration error: {e}")
        HAS_CLOUDINARY = False
else:
    print("Cloudinary credentials not found - using local storage")

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_image(file):
    """Upload image to Cloudinary if configured, otherwise save locally"""
    if not file or not allowed_file(file.filename):
        return None
    
    try:
        if HAS_CLOUDINARY:
            # Try Cloudinary first
            result = cloudinary.uploader.upload(file)
            return result['secure_url']
    except Exception as e:
        print(f"Cloudinary upload failed: {e}")
    
    # Fallback to local storage
    try:
        # Reset file pointer to the beginning
        file.seek(0)
        filename = secure_filename(file.filename)
        # Add timestamp to avoid filename conflicts
        import time
        filename = f"{int(time.time())}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return f"/static/images/{filename}"
    except Exception as e:
        print(f"Local upload failed: {e}")
        return None

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
        try:
            file = request.files.get("photo")
            caption = request.form.get("caption", "").strip()
            
            if not file:
                print("No file provided")
                return redirect(url_for("memories_page"))
            
            if not caption:
                print("No caption provided")
                return redirect(url_for("memories_page"))
            
            image_url = upload_image(file)
            if image_url:
                memories.append({"file": image_url, "caption": caption})
                save_data(memories_file, memories)
                print(f"Memory added successfully: {caption}")
            else:
                print("Image upload returned None")
        except Exception as e:
            print(f"Error in memories_page: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
        return redirect(url_for("memories_page"))
    return render_template("memories.html", memories=memories)

# Stories page
@app.route("/stories", methods=["GET", "POST"])
def stories_page():
    if request.method == "POST":
        try:
            file = request.files.get("photo")
            caption = request.form.get("caption", "").strip()
            
            if not file:
                print("No file provided")
                return redirect(url_for("stories_page"))
            
            if not caption:
                print("No caption provided")
                return redirect(url_for("stories_page"))
            
            image_url = upload_image(file)
            if image_url:
                stories.append({"file": image_url, "caption": caption})
                save_data(stories_file, stories)
                print(f"Story added successfully: {caption}")
            else:
                print("Image upload returned None")
        except Exception as e:
            print(f"Error in stories_page: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
        return redirect(url_for("stories_page"))
    return render_template("stories.html", stories=stories)

# Timeline page
@app.route("/timeline", methods=["GET", "POST"])
def timeline_page():
    if request.method == "POST":
        try:
            date = request.form.get("date", "").strip()
            title = request.form.get("title", "").strip()
            story = request.form.get("story", "").strip()
            file = request.files.get("photo")
            
            if not all([date, title, story]):
                print("Missing required fields")
                return redirect(url_for("timeline_page"))
            
            image_url = None
            if file:
                image_url = upload_image(file)
            
            timeline_events.append({
                "date": date,
                "title": title,
                "story": story,
                "image": image_url
            })
            timeline_events.sort(key=lambda x: x["date"], reverse=True)
            save_data(timeline_file, timeline_events)
            print(f"Timeline event added successfully: {title}")
        except Exception as e:
            print(f"Error in timeline_page: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
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


@app.errorhandler(500)
def internal_error(error):
    print(f"Internal Server Error: {error}")
    import traceback
    traceback.print_exc()
    return "Internal Server Error - Check server logs for details", 500

@app.errorhandler(404)
def not_found(error):
    return redirect(url_for("home"))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
