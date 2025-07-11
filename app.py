from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/memories')
def memories():
    return render_template('memories.html')

@app.route('/stories')
def stories():
    family_stories = [
        {
            "name": "Mama",
            "date": "Dec 2023",
            "story": "Mama always cooked the best chapati during the holidays.",
            "image": "family1.jpg"
        },
        {
            "name": "Denis",
            "date": "July 2022",
            "story": "That time we surprised grandma with a birthday cake.",
            "image": "family2.jpg"
        },
        {
            "name": "Jane",
            "date": "May 2021",
            "story": "We took a long walk in the village fields after dinner.",
            "image": None
        }
    ]
    return render_template('stories.html', stories=family_stories)

@app.route('/timeline')
def timeline():
    return render_template('timeline.html', stories=[
        {
            "name": "Mama",
            "date": "Dec 2023",
            "story": "Mama always cooked the best chapati during the holidays.",
            "image": "family1.jpg"
        },
        {
            "name": "Denis",
            "date": "July 2022",
            "story": "That time we surprised grandma with a birthday cake.",
            "image": "family2.jpg"
        },
        {
            "name": "Jane",
            "date": "May 2021",
            "story": "We took a long walk in the village fields after dinner.",
            "image": None
        }
    ])

if __name__ == '__main__':
    app.run(debug=True)
