use safehouse;
DROP PROCEDURE IF EXISTS CREATE_USER;
DROP PROCEDURE IF EXISTS PASSWORD_ON_UPDATE;

DELIMITER //

CREATE PROCEDURE CREATE_USER
(IN name VARCHAR(45), IN surname VARCHAR(45), email_address VARCHAR(45), number VARCHAR(12), password VARCHAR(45))
BEGIN
SELECT CURRENT_TIMESTAMP() into @curtimedate;
INSERT INTO safehouse.user (name, surname, email, number, created_at, last_updated) VALUES (name, surname, email_address, number, @curtimedate, @curtimedate);
SELECT id into @id from safehouse.user where user.email=email_address limit 1;
INSERT INTO safehouse.password (user_id, password, updated_at) VALUES (@id, password, @curtimedate);




END; 

CREATE PROCEDURE PASSWORD_ON_UPDATE
(IN id INT, IN new_password VARCHAR(45))
BEGIN
SELECT CURRENT_TIMESTAMP() into @curtimedate;
SELECT password into @old_password from safehouse.password where user.id=id;
INSERT INTO safehouse.old_password (user_id, password, changed_at) VALUES (id, @old_password, @curtimedate);
UPDATE safehouse.password set password.password=new_password, updated_at=@curtimedate where password.user_id=id;
END
//



