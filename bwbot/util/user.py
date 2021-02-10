import requests
import json
import os

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

    def _get(self, *args, ret_type=int):
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
        return self._get(*'player stats Bedwars final_kills_bedwars'.split())
    @property
    def bw_fdeaths(self):
        return self._get(*'player stats Bedwars final_deaths_bedwars'.split())
    @property
    def bw_stars(self):
        return self._get(*'player achievements bedwars_level'.split())
    @property
    def bw_wins(self):
        return self._get(*'player stats Bedwars wins_bedwars'.split())
    @property
    def bw_losses(self):
        return self._get(*'player stats Bedwars losses_bedwars'.split())
    @property
    def bw_winstreak(self):
        return self._get(*'player stats Bedwars winstreak'.split())

    @property
    def bg_wins(self):
        return self._get(*'player stats Duels bridge_duel_wins'.split())
    @property
    def bg_losses(self):
        return self._get(*'player stats Duels bridge_duel_losses'.split())
    @property
    def bg_winstreak(self):
        return self._get(*'player stats Duels current_bridge_winstreak'.split())
    @property
    def bg_title(self):
        titles = 'godlike grandmaster legend master ' \
                 'diamond gold iron rookie'.split()
        for title in titles:
            qry = f'bridge_{title}_title_prestige'
            lvl = self._get(*f'player stats Duels {qry}'.split())
            if lvl is not None:
                return f'{title.upper()} {lvl}'
        return None
