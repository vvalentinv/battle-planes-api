![logo-flat](https://github.com/vvalentinv/battle-planes-api/assets/55762636/0702ca91-f6dd-4d19-8961-86312ed63878)


# battle-planes-api
Battle-Planes is a Battleships similar game where all targets have a 10-square shape. 

- [ ] update ERD as the project scales in complexity
[ERD](/utilities/battle-planes-api.pdf)


Python battle-planes backend with the following endpoints:
- POST /users - adds a user record in the db with a unique username and email and valid password format
- PUT /users/<username> - if request is validated it updates a users email or password, not both 
- POST /planes/<sky_size> - not for public use; adds all possible planes in the planes table for a given battle matrix size
- POST /battles - adds an unchallenged battle for a user, body params, user's defense (array of plane IDs), sky size, defense                   size and the time willing to wait for a challenger
  - [ ] TO DO (add a private param that takes a username or a list of usernames (array of IDs), making the battle                     available just for a specific user or users list)
- PUT /battles/<battle_id> - if valid (takes three boolean query parameters) adds an attack to the battle record for the user or                            accepts a user's challenge or adds a plane to a user's defense after a challenge is accepted
- GET /battles/<battle_id> - if valid returns the battle data for either of the users engaged in battle, performs random attack                            for opponent if they run out of time.
- GET /battles - returns a list of battle details for users waiting for a challenger
  - [ ]           TO DO (add query params to filter list by defense size and sky size)
  - [ ]        TO DO (by query param if player has access to feature, filter the list by their preferred user or list of users)
 
  FUTURE FEATURE - add option to remove time constraint, automatic random attack, treat the battle as a game of chess that can                    be allways resumed until concluded. 

 unit testing - 12th May 2023
![image](https://github.com/vvalentinv/battle-planes-api/assets/55762636/8745b429-3d66-4a9b-b108-292b557c98a0)
