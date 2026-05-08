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

@app.route("/api/dashboard/<int:lecturer_id>", methods=["GET"])
def get_lecturer_dashboard(lecturer_id):
    """
    Fetches the data needed to populate a specific lecturer's dashboard,
    ensuring they only see their own questions and statistics.
    """
    
    # Query 1: The detailed list
    list_sql = """
        SELECT 
            q.id AS question_id,
            q.question_text, 
            b.level_name AS blooms_category,
            q.created_at
        FROM questions q
        INNER JOIN blooms_levels b ON q.bloom_level_id = b.level_id
        WHERE q.lecturer_id = ?
        ORDER BY q.created_at DESC;
    """
    
    # Query 2: The summary statistics
    stats_sql = """
        SELECT 
            b.level_name AS blooms_category,
            COUNT(q.id) AS question_count
        FROM blooms_levels b
        LEFT JOIN questions q ON b.level_id = q.bloom_level_id AND q.lecturer_id = ?
        GROUP BY b.level_id, b.level_name
        ORDER BY b.level_id ASC;
    """
    
    try:
        # Use your context manager to execute both queries safely
        with db.get_db_cursor() as cursor:
            # Fetch the list
            cursor.execute(list_sql, (lecturer_id,))
            questions_list = [dict(row) for row in cursor.fetchall()]
            
            # Fetch the stats
            cursor.execute(stats_sql, (lecturer_id,))
            bloom_stats = [dict(row) for row in cursor.fetchall()]
            
        # Package everything neatly for the frontend
        dashboard_data = {
            "total_questions": len(questions_list),
            "statistics": bloom_stats,
            "recent_questions": questions_list
        }
            
        return jsonify(dashboard_data), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500