DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS mcq_options;
DROP TABLE IF EXISTS essay_details;
DROP TABLE IF EXISTS questions;
DROP TABLE IF EXISTS blooms_levels;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS question_group_mapping;
DROP TABLE IF EXISTS custom_groups;

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
); -- <-- THIS WAS A COLON BEFORE!

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

CREATE TABLE mcq_options (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    option_text TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    
    -- Foreign Key Constraint to link options to questions
    FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE CASCADE
);

CREATE TABLE essay_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL UNIQUE, -- UNIQUE ensures only one rubric per essay
    marking_rubric TEXT,                 -- What the lecturer looks for
    suggested_word_count INTEGER,
    FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE CASCADE
);

-- Table 1: Stores the actual groups created by the lecturer
CREATE TABLE custom_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lecturer_id INTEGER NOT NULL,
    group_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Links the group to the lecturer who made it
    FOREIGN KEY (lecturer_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Table 2: The "Junction Table" that links a question to a group
CREATE TABLE question_group_mapping (
    group_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    
    -- This ensures a question can't be added to the exact same group twice
    PRIMARY KEY (group_id, question_id),
    
    -- If a group or question is deleted, automatically remove this link
    FOREIGN KEY (group_id) REFERENCES custom_groups (id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE CASCADE
);


CREATE TABLE uploaded_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lecturer_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (lecturer_id)
    REFERENCES users(id)
);

CREATE TABLE file_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    bloom_level_id INTEGER NOT NULL,

    FOREIGN KEY (file_id)
    REFERENCES uploaded_files(id),

    FOREIGN KEY (bloom_level_id)
    REFERENCES blooms_levels(level_id)
);