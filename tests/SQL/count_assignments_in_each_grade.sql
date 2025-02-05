-- Write query to get count of assignments in each grade
SELECT grade, COUNT(*) AS assignment_count
FROM assignments
WHERE state = 'GRADED'
GROUP BY grade;