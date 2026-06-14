import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from google import genai
from datetime import datetime
import sqlite3

app = Flask(__name__)

load_dotenv('keys.env')

DB_FILE = "lectures.db"

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS lectures (
                LectureID TEXT PRIMARY KEY,
                Topic TEXT NOT NULL,
                Date TEXT NOT NULL,
                Content TEXT NOT NULL
            )
        """)

init_db()


@app.route("/")
def home():
    return render_template("HomePage.html")

@app.route("/QuizGenerator")
def quizGenerator():
    return render_template("Quiz Generator.html")

@app.route("/LectureGenerator")
def lectureGenerator():
    return render_template("Lecture Generator.html")

@app.route("/generate_intro", methods=["POST"])
def generate_intro():
    data = request.json
    topic = data.get("topic", "")

    for i in range(1,7):
        key_name = f"GEMINI_API_KEY_{i}"
        key = os.getenv(key_name)

        if not key:
            print(f"Warning: {key_name} not found in environment. Skipping to next...")
            continue
        try:
            client = genai.Client(api_key=key)
            print(f"Connected successfully using {key_name}")
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=
                f"You are an educational app that is used to create informative lectures to help students."
                f"Do not use Markdown formatting (no **bold**, no *italics*, no backticks). "
                f"Only use plain text and HTML tags. "
                """Wrap the text in <div class="introduction animate-in">"""
                f"Do not include your thinking process or any other unrelated information on the output, "
                f"only write what is requested in the following line in the language of the topic request. "
                f"Generate a title and 2 long paragraphs that will act as the introduction of a lecture about this topic: "
                f"{topic}."
                f"Do not include greetings, openings, or phrases like 'Welcome students' or 'Today we will…'. "
                f"Begin immediately with the subject matter. "
                f"Place the lecture title outside of the introduction <div> in a simple <h1 class='lecture-title'>"
                f"Put each paragraph in a classless <p> element."
                f"If the topic appears to be a random string, gibberish, or a sequence of meaningless characters, "
                f"if no sensical meaning can be derived, do NOT try to hallucinate a specific meaning unrelated to randomness."
                f"Instead, treat the input as a demonstration of Randomness or Entropy."
                f"Use these premade css classes as needed: lecture-title, introduction, heading, subheading."
                )
            introduction = response.text.strip()
            return jsonify({"introduction": introduction})
        except Exception as e:
            print(f"Failed to initialize client: {e, topic, key_name}")
            continue


@app.route("/generate_body", methods=["POST"])
def generate_body():
    data = request.json
    topic = data.get("topic", "")
    intro = data.get("introduction", "")

    for i in range(1,7):
        key_name = f"GEMINI_API_KEY_{i}"
        key = os.getenv(key_name)

        if not key:
            print(f"Warning: {key_name} not found in environment. Skipping to next...")
            continue
        try:
            client = genai.Client(api_key=key)
            print(f"Connected successfully using {key_name}")
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=
                f"""You are an educational app that is used to create informative lectures to help students.
                Do not use Markdown formatting (no **bold**, no *italics*, no backticks). 
                Only use plain text and HTML tags. 
                Do not include your thinking process or any other unrelated information on the output, 
                only write what is requested in the following line in the language of the topic request. 
                Here is the introduction of a lecture:\n{intro}\n\n with the topic: {topic}. 
                Now continue by writing the main body of the lecture, with each individual section having a length of at least 2 long paragraphs. 
                Expand upon the topic that was introduced and try to include examples(give exercises, 
                and solve the exercises yourself to act as an example), 
                significance (where this topic is used in the real world), and a 2 paragraph conclusion. 
                Only include these sections if it makes sense and skip them if needed (no exercises for guides or 
                recipes, maybe add pro tips). 
                If a guide is required (eg. a recipe) include the ingredients, and a step by step guide. 
                Wrap the text in :
                <div class="lecbody animate-in"> for the opening of the body"
                <div class='conclusion'> for the conclusion, 
                <div class='examples'> for examples, 
                <div class='tools'> for tools and/or ingredients, 
                <div class='guide'> for guides, 
                <div class='significance'> for real-world use, applications or importance.
                Inside this div, always include a heading which should be creative and varied, not formulaic. 
                Do NOT wrap the conclusion inside the <div class="lecbody animate-in">, keep it in its own, separate div.
                Include a heading inside the start of the body and inside the conclusion div.
                Do not include any list styling yourself. 
                When generating content inside an <li> tag, DO NOT use <p> tags as they break list flow. Use inline text only.
                Use any other html tags as you see fit and these premade css classes:
                ul for .tools ,ol for .guide, .list-numbered, .list-lettered, .list-plain, heading, subheading."""
                )
            body = response.text.strip()
            return jsonify({"body": body})
        except Exception as e:
            print(f"Failed to initialize client: {e, topic, key_name}")
            continue


@app.route("/generate_quiz", methods=["POST"])
def generate_quiz():
    data = request.json
    topic = data.get("topic", "")
    body = data.get("body", "")
    quiz = data.get("quiz", "")

    for i in range(1, 7):
        key_name = f"GEMINI_API_KEY_{i}"
        key = os.getenv(key_name)

        if not key:
            print(f"Warning: {key_name} not found in environment. Skipping to next...")
            continue
        try:
            client = genai.Client(api_key=key)
            print(f"Connected successfully using {key_name}")
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=
                f"""You are an educational app that is used to create informative lectures to help students.
                Do not use Markdown formatting (no **bold**, no *italics*, no backticks). 
                Only use plain text and HTML tags. 
                Do not include your thinking process or any other unrelated information on the output, 
                only write what is requested in the following line. 
                Here is the body of a lecture:\n{body}\n\n, and the previous quiz:\n{quiz}\n\n with the topic: {topic}. 
                Now continue by writing a quizz section for the lecture trying to avoid questions from the previous quiz. 
                Wrap the text in <div class='quizz'> tags 
                Include 3 True/False questions, 3 multiple choice questions, and 4 fill in the blanks. 
                Include a hidden answer key wrapped in <div class='key'> at the end in this format: 
                 {{'q1':'False', 'q2':'17', 'q3':'Paris',...}}, and so on for each question in order 
                from true/false to fill in the blanks. 

                **Important HTML Structure Rules:**
                1. **True/False Questions:** Use radio buttons with hidden inputs: 
                  <p>1. Question 1.</p>
                  <div>
                    <input type="radio" name="qid" id="qid-true" value="True">
                    <label for="qid-true" class="label-style">True</label> 
                    <input type="radio" name="qid" id="qid-false" value="False">
                    <label for="qid-false" class="label-style">False</label> 
                  </div>
                2. Multiple Choice Questions: Use radio buttons inside each list item:
                  <ul>
                    <li><input type="radio" name="qid" value="a" id="qid-a"><label for="q4-a" class="label-style">a) Option</label></li>
                3. Fill in the Blanks: Use text input with matching ID and name:
                   <input type="text" id="qid" name="qid-input" class="fill-in-input">
                   Where the field is put inside the paragraph containing it :
                   <p>Some text at start and/or end <input type="text" id="qid" name="qid-input" class="fill-in-input">.</p>
                   Do not include any special characters for the input field.

                Start with question id q1 and go on until q10
                Do not include the question id in the actual question text.
                Add these items at the end of the quiz:
                <button id="validation" onclick="validateQuiz()" class="validation">Submit Quiz</button>
                <div id="quiz-result"></div>
                Use any other html tags as you see fit and these premade css classes:
                .quizz, .quizz .heading, .quizz h2, .label-style, input[type="radio"], #quizz-result, 
                .fill-in-input, input[type="text"], and #key for the answer key."""
                )
            quiz = response.text.strip()
            return jsonify({"quiz": quiz})
        except Exception as e:
            print(f"Failed to initialize client: {e, topic, key_name}")
            continue


@app.route("/independentQuiz", methods=["POST"])
def indie_quiz():
    body = request.form.get("body", "")
    file = request.files.get("file")
    quiz = request.form.get("quiz", "")
    temp_path = None
    mime = None

    if file:
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as f:
            file.save(f)
            f.flush()
            os.fsync(f.fileno())
        mime = "application/pdf" if file.filename.endswith(".pdf") else "text/plain"

    for i in range(1, 7):
        key_name = f"GEMINI_API_KEY_{i}"
        key = os.getenv(key_name)

        if not key:
            print(f"Warning: {key_name} not found in environment. Skipping to next...")
            continue

        try:
            client = genai.Client(api_key=key)
            print(f"Connected successfully using {key_name}")

            uploaded_file = None
            if temp_path:
                uploaded_file = client.files.upload(file=temp_path, config={"mime_type": mime})
                print(f"File uploaded: {uploaded_file.name}, state: {uploaded_file.state}")

            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=[
                    uploaded_file if uploaded_file else "",
                    f"""You are an educational app that is used to create informative lectures to help students.
                Do not use Markdown formatting (no **bold**, no *italics*, no backticks). 
                Only use plain text and HTML tags. 
                Do not include your thinking process or any other unrelated information on the output, 
                only write what is requested in the following line. 
                Here is the topic of a lecture:\n{body}\n\n, and the previous quiz:\n{quiz}\n\n, and/or files. 
                Now continue by writing a quizz section for the lecture trying to avoid questions from the previous quiz. 
                Wrap the text in <div class='quizz'> tags 
                Include 3 True/False questions, 3 multiple choice questions, and 4 fill in the blanks. 
                Include a hidden answer key wrapped in <div class='key'> at the end in this format: 
                 {{'q1':'False', 'q2':'17', 'q3':'Paris',...}}, and so on for each question in order 
                from true/false to fill in the blanks. 

                **Important HTML Structure Rules:**
                1. **True/False Questions:** Use radio buttons with hidden inputs: 
                  <p>1. Question 1.</p>
                  <div>
                    <input type="radio" name="qid" id="qid-true" value="True">
                    <label for="qid-true" class="label-style">True</label> 
                    <input type="radio" name="qid" id="qid-false" value="False">
                    <label for="qid-false" class="label-style">False</label> 
                  </div>
                2. Multiple Choice Questions: Use radio buttons inside each list item:
                  <ul>
                    <li><input type="radio" name="qid" value="a" id="qid-a"><label for="q4-a" class="label-style">a) Option</label></li>
                3. Fill in the Blanks: Use text input with matching ID and name:
                   <input type="text" id="qid" name="qid-input" class="fill-in-input">
                   Where the field is put inside the paragraph containing it :
                   <p>Some text at start and/or end <input type="text" id="qid" name="qid-input" class="fill-in-input">.</p>
                   Do not include any special characters for the input field.

                Start with question id q1 and go on until q10
                Do not include the question id in the actual question text.
                Add these items at the end of the quiz:
                <button id="validation" onclick="validateQuiz()" class="validation">Submit Quiz</button>
                <div id="quiz-result"></div>
                Use any other html tags as you see fit and these premade css classes:
                .quizz, .quizz .heading, .quizz h2, .label-style, input[type="radio"], #quizz-result, 
                .fill-in-input, input[type="text"], and #key for the answer key."""
                ]
            )
            quiz = response.text.strip()
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            return jsonify({"quiz": quiz})

        except Exception as e:
            print(f"Failed to initialize client: {e, key_name}")
            
    if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
    print(f"Failed to initialize client with available keys.")
    return jsonify({"error": "System is Currently Unavailable"}), 500

            


@app.route("/save_lecture", methods=["POST"])
def save_lecture():
    data = request.json
    topic = data.get("topic", "Untitled")
    html = data.get("html", "")
    key = "lecture_" + str(int(datetime.now().timestamp() * 1000))
    date = datetime.now().strftime("%Y-%m-%d")

    with get_db() as conn:
        conn.execute(
            "INSERT INTO lectures (LectureID, Topic, Date, Content) VALUES (?, ?, ?, ?)",
            (key, topic, date, html)
        )
    return jsonify({"success": True, "key": key})


@app.route("/get_lectures", methods=["GET"])
def get_lectures():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT LectureID, Topic, Date, Content FROM lectures ORDER BY LectureID DESC"
        ).fetchall()
    return jsonify({row["LectureID"]: {"topic": row["Topic"], "date": row["Date"], "html": row["Content"]} for row in rows})


@app.route("/delete_lecture/<key>", methods=["DELETE"])
def delete_lecture(key):
    with get_db() as conn:
        result = conn.execute("DELETE FROM lectures WHERE LectureID = ?", (key,))
    if result.rowcount:
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Not found"}), 404

@app.route("/Lecture/<key>")
def view_lecture(key):
    with get_db() as conn:
        row = conn.execute(
            "SELECT LectureID, Topic, Date, Content FROM lectures WHERE LectureID = ?", (key,)
        ).fetchone()
    if not row:
        return "Lecture not found.", 404
    return render_template("Lecture.html", topic=row["Topic"], date=row["Date"], html=row["Content"])

if __name__ == "__main__":
    app.run(debug=True)
