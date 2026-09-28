-- PostgreSQL schema. UNIQUE constraints on timetable_entries enforce H1 & H2 at DB level.
CREATE TABLE study_years   (id SERIAL PRIMARY KEY, year_no SMALLINT NOT NULL, major TEXT NOT NULL,
                            semester_type TEXT CHECK (semester_type IN ('ODD','EVEN')), room TEXT, filler TEXT);
CREATE TABLE student_groups(id SERIAL PRIMARY KEY, study_year_id INT REFERENCES study_years(id) ON DELETE CASCADE, name TEXT NOT NULL);
CREATE TABLE professors    (id SERIAL PRIMARY KEY, full_name TEXT NOT NULL, max_weekly_hours SMALLINT NOT NULL CHECK (max_weekly_hours > 0));
CREATE TABLE subjects      (id SERIAL PRIMARY KEY, study_year_id INT REFERENCES study_years(id) ON DELETE CASCADE,
                            code TEXT, title TEXT NOT NULL, kind TEXT CHECK (kind IN ('THEORY','LAB')) DEFAULT 'THEORY',
                            credits SMALLINT NOT NULL CHECK (credits > 0),          -- weekly hours = credits
                            professor_id INT NOT NULL REFERENCES professors(id));
CREATE TABLE time_slots    (day_no SMALLINT, slot_no SMALLINT, start_time TIME, end_time TIME, PRIMARY KEY (day_no, slot_no));
CREATE TABLE professor_unavailability (professor_id INT REFERENCES professors(id), day_no SMALLINT, slot_no SMALLINT,
                                       PRIMARY KEY (professor_id, day_no, slot_no));
CREATE TABLE timetable_runs(id SERIAL PRIMARY KEY, created_at TIMESTAMPTZ DEFAULT now(), seed INT, config JSONB);
CREATE TABLE timetable_entries (
  run_id INT REFERENCES timetable_runs(id) ON DELETE CASCADE,
  group_id INT REFERENCES student_groups(id), subject_id INT REFERENCES subjects(id),
  professor_id INT REFERENCES professors(id), day_no SMALLINT, slot_no SMALLINT,
  UNIQUE (run_id, group_id, day_no, slot_no),          -- H2 no group overlap
  UNIQUE (run_id, professor_id, day_no, slot_no));     -- H1 no teacher overlap
