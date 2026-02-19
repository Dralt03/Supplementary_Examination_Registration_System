DELIMITER //
-- Procedure 1: Add Student
CREATE PROCEDURE add_student(
    IN p_roll INT,
    IN p_name VARCHAR(45),
    IN p_branch VARCHAR(45),
    IN p_sem VARCHAR(45),
    IN p_email VARCHAR(45)
)
BEGIN
    INSERT INTO student VALUES (p_roll, p_name, p_branch, p_sem, p_email);
END //


-- Procedure 2: Add Course
CREATE PROCEDURE add_course(
    IN p_code VARCHAR(45),
    IN p_name VARCHAR(45),
    IN p_dept VARCHAR(45),
    IN p_credits VARCHAR(45)
)
BEGIN
    INSERT INTO courses VALUES (p_code, p_name, p_dept, p_credits);
END //


-- Procedure 3: Add Grade
CREATE PROCEDURE add_grade(
    IN p_roll INT,
    IN p_code VARCHAR(45),
    IN p_dept VARCHAR(45),
    IN p_credits VARCHAR(45),
    IN p_grade VARCHAR(45)
)
BEGIN
    INSERT INTO grades VALUES (p_roll, p_code, p_dept, p_credits, p_grade);
END //


-- Procedure 4: Add Payment
CREATE PROCEDURE add_payment(
    IN p_txn INT,
    IN p_roll INT,
    IN p_code VARCHAR(45),
    IN p_amount INT,
    IN p_date DATE,
    IN p_status VARCHAR(45)
)
BEGIN
    INSERT INTO payment VALUES (p_txn, p_roll, p_code, p_amount, p_date, p_status);
END //


-- Procedure 5: Register Supplementary
CREATE PROCEDURE register_supplementary(
    IN p_sup INT,
    IN p_roll INT,
    IN p_txn INT,
    IN p_code VARCHAR(45),
    IN p_date DATE
)
BEGIN

    -- Check failed course
    IF NOT EXISTS (
        SELECT 1 FROM grades
        WHERE roll_no = p_roll
        AND course_code = p_code
        AND grade_id = 'F'
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Student did not fail this course';
    END IF;

    -- Check payment success
    IF NOT EXISTS (
        SELECT 1 FROM payment
        WHERE transaction_no = p_txn
        AND payment_status = 'SUCCESS'
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Payment not completed';
    END IF;

    -- Insert supplementary
    INSERT INTO supplementary VALUES (p_sup, p_roll, p_txn, p_code, p_date);

END //

DELIMITER ;

