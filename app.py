from flask import Flask, request, jsonify  # type: ignore[import]
import db
app = Flask(__name__)
db.init_app(app)
# ---WEB ROUTES GO HERE---
@app.route("/")
def home():
    return "<h1>Server is running!</h1><p>Centeralized DB module is active.</p>"
@app.route("/users", methods=["POST"])
def save_question():
    """
    Saves a newly added question and maps it to a Bloom's level.
    Expects JSON payload: {"lecturer_id": 1, "question_text": "...", "bloom_level_id": 2}
    """
    data = request.get_json()
    
    lecturer_id = data.get("lecturer_id")
    question_text = data.get("question_text")
    bloom_level_id = data.get("bloom_level_id")
    
    if not all([lecturer_id, question_text, bloom_level_id]):
        return jsonify({"error": "Missing required fields"}), 400

    sql = """
        INSERT INTO questions (lecturer_id, question_text, bloom_level_id)
        VALUES (?, ?, ?)
    """
    
    try:
        with db.get_db_cursor() as cursor:
            cursor.execute(sql, (lecturer_id, question_text, bloom_level_id))
            
        return jsonify({"message": "Question successfully saved and mapped!"}), 201
        
    except Exception as e:
        # get_db_cursor() already handles the rollback, so we just return the error
        return jsonify({"error": str(e)}), 500
    
if __name__ == "__main__":
    app.run(debug=True)

@app.route("/lecturer/<int:lecturer_id>/questions", methods=["GET"])
def get_lecturer_questions(lecturer_id):
    sql = """
        SELECT 
            q.question_text, 
            b.level_name AS blooms_category
        FROM questions q
        INNER JOIN blooms_levels b ON q.bloom_level_id = b.level_id
        WHERE q.lecturer_id = ?
    """
    
    try:
        with db.get_db_cursor() as cursor:
            cursor.execute(sql, (lecturer_id,))
            questions = cursor.fetchall()
            
        return jsonify(questions), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500