DROP TABLE IF EXISTS battle_results;
DROP TABLE IF EXISTS battles; 
DROP TABLE IF EXISTS planes;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS flight_directions;

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
	challenger_id INT NOT NULL,
	challenged_id INT NOT NULL,
	challenger_defense INT[],
	challenged_defense INT[] NOT NULL,
	sky_size INT NOT NULL,
	challenger_attacks INT[],
	challenged_attacks INT[],
	rnd_attack_er INT[],
	rnd_attack_ed INT[],
	concluded BOOLEAN  NOT NULL,
	defense_size INT NOT NULL,
	end_battle_turn_at TIMESTAMPTZ NOT NULL,
	battle_turn_size INT NOT NULL,
	CONSTRAINT fk_challenger_id
  		FOREIGN KEY (challenger_id) REFERENCES "users" (id),
  	CONSTRAINT fk_challenged_id
  		FOREIGN KEY (challenged_id) REFERENCES "users" (id)
);

CREATE TABLE battle_results(
	id SERIAL PRIMARY KEY,
	battle_id INT NOT NULL,
	winner INT,
	disconnected_user INT,
	CONSTRAINT fk_br_battle_id
  		FOREIGN KEY (battle_id) REFERENCES "battles" (id)
);


INSERT INTO users (id, username, pass, email) VALUES (0, 'default-challenger', '', '');
INSERT INTO flight_directions VALUES (1, 'North'), (2, 'East'), (3, 'South'), (4, 'West');

INSERT INTO battles (challenger_id, challenged_id, challenger_defense, challenged_defense, challenger_attacks, challenged_attacks, rnd_attack_ed, concluded, battle_turn) VALUES 
					(0, 2, array[1,2,3], array[1,2,3], array[0, 9, 90, 99], array[0, 9, 90, 99], array[0, 9, 90, 99], False, Now() + '7 MINUTE');
update battles set concluded  = true  WHERE id = 187 RETURNING *;
SELECT (SELECT username FROM users WHERE username='jcad1') = 'jcad1';
select (Select battle_turn from battles b Where id = 185) > Now();
select * from planes where id IN(125,88);

SELECT () = 

delete from battles;
select * from flight_directions f ;
select * from users u ;
select * from planes p ;
select * from battles b ;
delete from battles;
select * from battle_results br ;

Select id
		FROM battles
        WHERE concluded IS False AND challenger_id = 2 AND Now() < battle_turn + interval '15 MINUTE'   
		UNION
     	SELECT id 
     	FROM battles 
     	WHERE concluded IS False AND challenged_id = 2 AND challenger_id <> 0 AND Now() < battle_turn 
     	 = 2;

SELECT * FROM battles WHERE challenger_id = 1 and (cardinality(challenger_defense) < defense_size or cardinality(challenger_defense ) = NULL )and concluded = False;

Select cardinality(challenger_defense) as def_size From battles;
SELECT * FROM battles b WHERE challenged_id = 5 and challenger_id = 0;