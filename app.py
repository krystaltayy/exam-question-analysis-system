from flask import Flask, request, jsonify  # type: ignore[import]
import math # Needed for pagination
import db

app = Flask(__name__)
db.init_app(app)

# ---WEB ROUTES GO HERE---
@app.route("/")
def home():
    return "<h1>Server is running!</h1><p>Centralized DB module is active.</p>"

@app.route("/api/questions", methods=["POST"]) # <-- FIXED ROUTE NAME
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
        return jsonify({"error": str(e)}), 500

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
            questions = [dict(row) for row in cursor.fetchall()] # Added dictionary conversion for JSON
            
        return jsonify(questions), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/dashboard/<int:lecturer_id>", methods=["GET"])
def get_lecturer_dashboard(lecturer_id):
    """
    Fetches the data needed to populate a specific lecturer's dashboard,
    ensuring they only see their own questions and statistics.
    """
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
        with db.get_db_cursor() as cursor:
            cursor.execute(list_sql, (lecturer_id,))
            questions_list = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute(stats_sql, (lecturer_id,))
            bloom_stats = [dict(row) for row in cursor.fetchall()]
            
        dashboard_data = {
            "total_questions": len(questions_list),
            "statistics": bloom_stats,
            "recent_questions": questions_list
        }
            
        return jsonify(dashboard_data), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# --- ROUTE 1: Create a New Group ---
@app.route("/api/groups", methods=["POST"])
def create_group():
    data = request.get_json()
    lecturer_id = data.get("lecturer_id")
    group_name = data.get("group_name")
    
    if not all([lecturer_id, group_name]):
        return jsonify({"error": "Missing lecturer_id or group_name"}), 400
        
    sql = "INSERT INTO custom_groups (lecturer_id, group_name) VALUES (?, ?)"
    
    try:
        with db.get_db_cursor() as cursor:
            cursor.execute(sql, (lecturer_id, group_name))
        return jsonify({"message": f"Group '{group_name}' created successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- ROUTE 2: Add a Question to a Group ---
@app.route("/api/groups/add-question", methods=["POST"])
def add_question_to_group():
    data = request.get_json()
    group_id = data.get("group_id")
    question_id = data.get("question_id")
    
    if not all([group_id, question_id]):
        return jsonify({"error": "Missing group_id or question_id"}), 400
        
    sql = "INSERT INTO question_group_mapping (group_id, question_id) VALUES (?, ?)"
    
    try:
        with db.get_db_cursor() as cursor:
            cursor.execute(sql, (group_id, question_id))
        return jsonify({"message": "Question added to group successfully!"}), 201
    except db.sqlite3.IntegrityError:
        return jsonify({"error": "This question is already in this group."}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- ROUTE 3: View All Questions Inside a Specific Group ---
@app.route("/api/groups/<int:group_id>/questions", methods=["GET"])
def get_group_questions(group_id):
    sql = """
        SELECT 
            q.id AS question_id,
            q.question_text, 
            b.level_name AS blooms_category,
            q.created_at
        FROM questions q
        INNER JOIN question_group_mapping map ON q.id = map.question_id
        INNER JOIN blooms_levels b ON q.bloom_level_id = b.level_id
        WHERE map.group_id = ? 
        ORDER BY q.created_at DESC;
    """
    
    try:
        with db.get_db_cursor() as cursor:
            cursor.execute(sql, (group_id,))
            group_questions = [dict(row) for row in cursor.fetchall()]
            
        return jsonify({
            "group_id": group_id,
            "total_questions": len(group_questions),
            "questions": group_questions
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- MOVED TO THE BOTTOM! ---
if __name__ == "__main__":
    app.run(debug=True)