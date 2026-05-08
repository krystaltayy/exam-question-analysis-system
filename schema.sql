
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS questions;
DROP TABLE IF EXISTS bloom_levels;

-- Create the Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the Posts table
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraint to link posts to users
    FOREIGN KEY (author_id) REFERENCES users (id) ON DELETE CASCADE
):

CREATE TABLE blooms_levels (
    level_id INTEGER PRIMARY KEY,
    level_name TEXT UNIQUE NOT NULL
);

INSERT INTO blooms_levels (level_id, level_name) VALUES
(1, 'Remembering'),
(2, 'Understanding'),
(3, 'Applying'),
(4, 'Analyzing'),
(5, 'Evaluating'),
(6, 'Creating');

CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lecturer_id INTEGER NOT NULL,
    bloom_level_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints
    FOREIGN KEY (lecturer_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (bloom_level_id) REFERENCES blooms_levels (level_id)
);

SELECT 
    q.id AS question_id,
    q.question_text, 
    b.level_name AS blooms_category,
    q.created_at
FROM questions q
INNER JOIN blooms_levels b ON q.bloom_level_id = b.level_id
WHERE q.lecturer_id = ?
ORDER BY q.created_at DESC;

SELECT 
    b.level_name AS blooms_category,
    COUNT(q.id) AS question_count
FROM blooms_levels b
LEFT JOIN questions q ON b.level_id = q.bloom_level_id AND q.lecturer_id = ?
GROUP BY b.level_id, b.level_name
ORDER BY b.level_id ASC;