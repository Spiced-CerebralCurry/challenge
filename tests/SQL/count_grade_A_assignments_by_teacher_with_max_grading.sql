-- Write query to find the number of grade A's given by the teacher who has graded the most assignments
WITH TeacherGradingCounts AS (
    SELECT teacher_id, COUNT(*) AS total_graded
    FROM assignments
    WHERE state = 'GRADED'
    GROUP BY teacher_id
),
TeacherWithMaxGrading AS (
    SELECT teacher_id
    FROM TeacherGradingCounts
    WHERE total_graded = (SELECT MAX(total_graded) FROM TeacherGradingCounts)
)
SELECT COUNT(*) AS grade_A_count
FROM assignments
WHERE grade = 'A' 
AND state = 'GRADED'
AND teacher_id IN (SELECT teacher_id FROM TeacherWithMaxGrading);