import requests
import json
import os
from ratelimit import limits

class User:
    def __init__(self, ign):
        mj_res = requests.get('https://api.mojang.com'
                           f'/users/profiles/minecraft/{ign}')
        if len(mj_res.text):
            mj_json = json.loads(mj_res.text)
            self.uuid = mj_json['id']
            self.ign = mj_json['name']
            hypixel_api_key = os.environ.get("hypixel-api-key")
            hy_res = requests.get('https://api.hypixel.net'
                                  f'/player?key={hypixel_api_key}'
                                  f'&uuid={self.uuid}')
            self.stats = json.loads(hy_res.text)
        else:
            self.ign = ign
            self.uuid, self.stats = None, None

    @limits(calls=100, period=60)
    def _get(self, path, ret_type=int):
        args = path.split()
        cur = self.stats
        try:
            for arg in args:
                if arg in cur:
                    cur = cur[arg]
                else:
                    return None
            return ret_type(cur)
        except (ValueError, TypeError):
            return None

    @property
    def bw_fkills(self):
        return self._get('player stats Bedwars final_kills_bedwars')
    @property
    def bw_fdeaths(self):
        return self._get('player stats Bedwars final_deaths_bedwars')
    @property
    def bw_stars(self):
        return self._get('player achievements bedwars_level')
    @property
    def bw_wins(self):
        return self._get('player stats Bedwars wins_bedwars')
    @property
    def bw_losses(self):
        return self._get('player stats Bedwars losses_bedwars')
    @property
    def bw_winstreak(self):
        return self._get('player stats Bedwars winstreak')

    @property
    def bg_wins1(self):
        return self._get('player stats Duels bridge_duel_wins')
    @property
    def bg_losses1(self):
        return self._get('player stats Duels bridge_duel_losses')
    @property
    def bg_wins2(self):
        return self._get('player stats Duels bridge_doubles_wins')
    @property
    def bg_losses2(self):
        return self._get('player stats Duels bridge_doubles_losses')
    @property
    def bg_wins4(self):
        return self._get('player stats Duels bridge_four_wins')
    @property
    def bg_losses4(self):
        return self._get('player stats Duels bridge_four_losses')
    @property
    def bg_winstreak(self):
        return self._get('player stats Duels current_bridge_winstreak')
    @property
    def bg_title(self):
        titles = 'godlike grandmaster legend master diamond gold iron rookie'
        for title in titles.split():
            full_title = f'bridge_{title}_title_prestige'
            lvl = self._get(f'player stats Duels {full_title}')
            if lvl is not None:
                return f'{title.upper()} {lvl}'
        return None
