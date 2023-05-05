DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS flight_directions
DROP TABLE IF EXISTS planes;
DROP TABLE IF EXISTS battles; 

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
	cockpit INT NOT NULL,
	flight_direction_id INT NOT NULL,
	body INT[] NOT NULL,
	sky_size INT NOT NULL,
	CONSTRAINT fk_flight_direction_id
  		FOREIGN KEY (flight_direction_id) REFERENCES "flight_directions" (id)
);

CREATE TABLE battles(
	id SERIAL PRIMARY KEY,
	challenger_id INT DEFAULT 0,
	challenged_id INT NOT NULL,
	challenger_defense INT[],
	challenged_defense INT[] NOT NULL,
	sky_size INT DEFAULT 10,
	challenger_attacks INT[],
	challenged_attacks INT[],
	rnd_attack_er INT[],
	rnd_attack_ed INT[],
	concluded BOOLEAN  NOT NULL DEFAULT False,
	defense_size INT DEFAULT 3,
	battle_turn TIMESTAMP,
	CONSTRAINT fk_challenger_id
  		FOREIGN KEY (challenger_id) REFERENCES "users" (id),
  	CONSTRAINT fk_challenged_id
  		FOREIGN KEY (challenged_id) REFERENCES "users" (id)
);

INSERT INTO users (id, username, pass, email) VALUES (0, 'default-challenger', '', '');
INSERT INTO flight_directions VALUES (1, 'North'), (2, 'East'), (3, 'South'), (4, 'West');

INSERT INTO battles (challenged_id, challenged_defense, concluded, battle_turn) VALUES 
					(0, array[1,2,3], False, Now());
update battles set concluded  = false  WHERE id = 16;
SELECT (SELECT username FROM users WHERE username='jcad1') = 'jcad1';
select (Select battle_turn from battles b Where id = 6) > Now();

delete from battles;
select * from flight_directions f ;
select * from users u ;
select * from planes p ;
select * from battles b ;

SELECT (SELECT challenger_id 
		FROM battles
        WHERE concluded IS False AND challenger_id = 2
		UNION
     	SELECT challenged_id 
     	FROM battles 
     	WHERE concluded IS False AND challenged_id = 2 AND challenger_id <> 0 )
     	 = 2;

