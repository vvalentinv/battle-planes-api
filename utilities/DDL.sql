DROP TABLE IF EXISTS users;

CREATE EXTENSION IF NOT EXISTS pgcrypto;
--CREATE EXTENSION IF NOT EXISTS intarray;

CREATE TABLE users(
	id SERIAL PRIMARY KEY,
	username TEXT NOT NULL UNIQUE,
	pass TEXT NOT NULL,
	email TEXT NOT NULL UNIQUE
);

SELECT  (SELECT username FROM users WHERE username='jd80@a.ca') = 'jd80@a.ca';
select * from users u ;