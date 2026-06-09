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
    
    -- NEW COLUMNS ADDED HERE:
    question_type TEXT NOT NULL DEFAULT 'MCQ', -- e.g., 'MCQ', 'Essay', 'Case Study', 'Structured'
    file_path TEXT,                            -- Stores the folder path where the backend saves the attached file
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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

-- 1. The Dictionary: Stores all the action verbs used by the algorithm
CREATE TABLE bloom_verbs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    verb TEXT NOT NULL UNIQUE,          
    bloom_level_id INTEGER NOT NULL,    
    
    FOREIGN KEY (bloom_level_id) REFERENCES blooms_levels (level_id) ON DELETE CASCADE
-- Remembering (Level 1)
INSERT INTO bloom_verbs (verb, bloom_level_id) VALUES ('list', 1), ('define', 1), ('name', 1), ('state', 1), ('identify', 1), ('label', 1);
-- Understanding (Level 2)
INSERT INTO bloom_verbs (verb, bloom_level_id) VALUES ('explain', 2), ('summarize', 2), ('interpret', 2), ('classify', 2), ('compare', 2), ('contrast', 2), ('describe', 2);
-- Applying (Level 3)
INSERT INTO bloom_verbs (verb, bloom_level_id) VALUES ('apply', 3), ('use', 3), ('demonstrate', 3), ('solve', 3), ('implement', 3), ('execute', 3), ('interpret', 3);
-- Analyzing (Level 4)
INSERT INTO bloom_verbs (verb, bloom_level_id) VALUES ('analyze', 4), ('differentiate', 4), ('organize', 4), ('attribute', 4), ('deconstruct', 4), ('relate', 4), ('examine', 4), ('distinguish', 4);
-- Evaluating (Level 5)
INSERT INTO bloom_verbs (verb, bloom_level_id) VALUES ('evaluate', 5), ('judge', 5), ('critique', 5), ('justify', 5), ('defend', 5), ('appraise', 5), ('assess', 5), ('argue', 5), ('recommend', 5);
-- Creating (Level 6)
INSERT INTO bloom_verbs (verb, bloom_level_id) VALUES ('design', 6), ('construct', 6),( 'develop', 6), ('formulate', 6), ('assemble', 6), ('generate', 6), ('plan', 6), ('produce', 6), ('invent', 6);
);

CREATE TABLE question_analysis_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    verb_id INTEGER NOT NULL,           
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE CASCADE,
    FOREIGN KEY (verb_id) REFERENCES bloom_verbs (id) ON DELETE CASCADE
);