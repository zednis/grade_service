DROP TABLE IF EXISTS assignment_score;

CREATE TABLE assignment_score (
    student TEXT NOT NULL,
    course TEXT NOT NULL,
    course_session TEXT NOT NULL,
    assignment TEXT NOT NULL,
    points_possible INT NOT NULL,
    points_scored INT NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMP NOT NULL,
    PRIMARY KEY (student, course, course_session, assignment)
);