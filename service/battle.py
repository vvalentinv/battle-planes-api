from dao.battle import BattleDao
from dao.plane import PlaneDao


class BattleService:
    def __init__(self):
        self.battle_dao = BattleDao()
        self.plane_dao = PlaneDao()

    def add_plane_to_battle_defense_by_username(self, battle_id, cockpit, flight_direction, sky_size):
        # TO DO validate values
        # TO DO check if logged-in user is in battle
        # TO DO bring username as param
        plane_id = self.plane_dao.get_plane_id(cockpit, flight_direction, sky_size)
        username = None
        if plane_id is not None:
            # get current defense array of plane Ids for username and add plane_id to it
        planes_array = None
        return self.battle_dao.add_plane_to_battle_defense_by_username(battle_id, planes_array, username)

