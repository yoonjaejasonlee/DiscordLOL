import requests
import json
from urllib.parse import quote
from getChamps import get_champion_list

with open('champion.json') as f:
    champ_info = json.load(f)

mapRankName = {
    'RANKED_FLEX_SR': 'FLEX 5:5 Rank',
    'RANKED_SOLO_5x5': "Personal/Duo Rank"
}


class riot_api_request(object):

    def __init__(self, RiotAPI):
        self.endpoint = 'https://na1.api.riotgames.com'
        self.puuidEnd = '/lol/summoner/v4/summoners/by-name/'
        self.personal_Info = '/lol/league/v4/entries/by-summoner'
        self.personal_Champ_Mastery = 'lol/champion-mastery/v4/champion-masteries/by-summoner/'
        self.req_header = {
            "User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.96 '
                          'Safari/537.36',
            "Accept_Language": 'en_US',
            "X-Riot-Token": RiotAPI
        }

    def re_open_json(self):
        with open('champion.json') as f:
            info = json.load(f)

    def update_client_info(self):
        if requests.get('https://ddragon.leagueoflegends.com/api/versions.json').json()[0] != champ_info['Version']:
            get_champion_list()
            self.re_open_json()
        else:
            pass

    def get_puuid_and_encryptedID(self, name):
        get_json = requests.get(self.endpoint + self.puuidEnd + quote(name), headers=self.req_header).json()
        summoner_keybox = {
            'encid': get_json['id'],
            'puuid': get_json['puuid']
        }
        return summoner_keybox

    def get_personal_champ_mastery(self, name):
        self.update_client_info()
        try:
            keybox = self.get_puuid_and_encryptedID(name)
            mastery = \
                requests.get(self.endpoint + self.personal_Champ_Mastery + keybox['encid'],
                             headers=self.req_header).json()[
                    0]
            chid = mastery['championId']
            chlv = mastery['championLevel']
            chpoint = mastery['championPoints']
            process_mastery = {
                'championname': champ_info[str(chid)]['name'],
                'championlevel': chlv,
                'championpoint': chpoint,
                'championImage': champ_info[str(chid)]["image"]
            }
            return process_mastery
        except KeyError as e:
            return False

    def get_personal_champ_masteries(self, name):
        self.update_client_info()
        try:
            keybox = self.get_puuid_and_encryptedID(name)
            mastery = requests.get(self.endpoint + self.personal_Champ_Mastery + keybox['encid'],
                                   headers=self.req_header).json()
            re = dict()
            if len(mastery) > 3:
                mastery = mastery[0:3]
                for i in mastery:
                    chid = i['championId']
                    chlv = i['championLevel']
                    chpoint = i['championPoints']
                    re[champ_info[str(chid)]]['name'] = {
                        'championlevel': chlv,
                        'championpoint': chpoint,
                        'championImage': champ_info[str(chid)]["image"]
                    }
            else:
                for i in mastery:
                    chid = i['championId']
                    chlv = i['championLevel']
                    chpoint = i['championPoints']
                    re[champ_info[str(chid)]]['name'] = {
                        'championlevel': chlv,
                        'championpoint': chpoint,
                        'championImage': champ_info[str(chid)]["image"]
                    }
            return re
        except KeyError as e:
            return False

    def get_personal_game_record(self, name):
        self.update_client_info()
        try:
            keybox = self.get_puuid_and_encryptedID(name)
            get_mastery = self.get_personal_champ_mastery(name)
            get_json = requests.get(self.endpoint + self.personal_Info + keybox['encid'],
                                    headers=self.req_header).json()
            re = dict()

            for i in get_json:
                re[mapRankName[i['queueType']]] = {
                    'tier': f"{i['tier']}",
                    'rank': f"{i['rank']}",
                    'leaguepoint': i['leaguePoints'],
                    'win': i['wins'],
                    'loss': i['losses']
                }

            summary = {
                'Record': re,
                'ChampionMastery': get_mastery
            }
            return summary
        except KeyError as e:
            return False
