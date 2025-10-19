from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from textblob import TextBlob
from datetime import datetime


app = Flask(__name__)


# Set up database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///entries.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Thought model
class Thought(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)  # Full journal
    sentiment = db.Column(db.String(20), nullable=False)  # Overall mood
    breakdown = db.Column(db.Text, nullable=False)  # Per sentence results
    date = db.Column(db.DateTime, default=datetime.utcnow)


# Homepage - show all past entries
@app.route('/')
def home():
    entries = Thought.query.order_by(Thought.date.desc()).all()
    return render_template('index.html', entries=entries)


# Analyze and store journal entry
@app.route('/analyze', methods=['POST'])
def analyze():
    text = request.form['text']
    blob = TextBlob(text)
    sentence_results = []
    total_polarity = 0


    for sentence in blob.sentences:
        polarity = sentence.sentiment.polarity
        total_polarity += polarity


        if polarity > 0:
            sentiment = "Positive 😊"
        elif polarity < 0:
            sentiment = "Negative 😡"
        else:
            sentiment = "Neutral 😐"


        sentence_results.append(f"{sentence} → {sentiment}")


    avg_polarity = total_polarity / len(blob.sentences)


    if avg_polarity > 0:
        overall_sentiment = "Positive 😊"
    elif avg_polarity < 0:
        overall_sentiment = "Negative 😡"
    else:
        overall_sentiment = "Neutral 😐"


    # Save entry with breakdown joined as one string
    new_thought = Thought(
        content=text,
        sentiment=overall_sentiment,
        breakdown='\n'.join(sentence_results)
    )
    db.session.add(new_thought)
    db.session.commit()


    return redirect('/')


    return render_template('result.html', text=text, results=sentence_results, overall=overall_sentiment)


# Auto-create database on first run
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)