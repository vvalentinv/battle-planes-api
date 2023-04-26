DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS flight_directions
DROP TABLE IF EXISTS planes;

CREATE EXTENSION IF NOT EXISTS intarray;

CREATE TABLE users(
	id SERIAL PRIMARY KEY,
	username TEXT NOT NULL UNIQUE,
	pass TEXT NOT NULL,
	email TEXT NOT NULL UNIQUE
);

CREATE TABLE flight_directions(
	id INT PRIMARY KEY,
	flight_direction_name VARCHAR(5)
);

CREATE TABLE planes(
	id SERIAL PRIMARY KEY,
	cockpit int NOT NULL,
	flight_direction_id INT NOT NULL,
	body INT[] NOT NULL,
	sky_size INT NOT NULL,
	CONSTRAINT fk_flight_direction_id
  		FOREIGN KEY (flight_direction_id) REFERENCES "flight_directions" (id)
);

CREATE TABLE battles(
	id SERIAL PRIMARY KEY,
	cockpit int NOT NULL,
	flight_direction_id INT NOT NULL,
	body INT[] NOT NULL,
	sky_size INT NOT NULL,
	CONSTRAINT fk_flight_direction_id
  		FOREIGN KEY (flight_direction_id) REFERENCES "flight_directions" (id)
);

INSERT INTO flight_directions VALUES (1, 'North'), (2, 'East'), (3, 'South'), (4, 'West');

select * from flight_directions f ;
select * from users u ;
select * from planes p ;
