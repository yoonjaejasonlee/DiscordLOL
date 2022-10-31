import json
import requests


def get_champion_list():
    get_latest_patch = requests.get('https://ddragon.leagueoflegends.com/api/versions.json').json()
    latest_ver = get_latest_patch[0]

    full_champ = requests.get(f'http://ddragon.leagueoflegends.com/cdn/{latest_ver}/data/en_US/champion.json').json()
    re = dict()
    re["Version"] = latest_ver

    for i in full_champ['data'].keys():
        key = full_champ['data'][i]['key']
        id = full_champ['data'][i]['id']
        tags = full_champ['data'][i]['tags']
        img = full_champ['data'][i]['image']['full']
        re[key] = {
            'name': id,
            'tag': tags,
            'image': img
        }

    with open('champion.json', 'w') as f:
        json.dump(re, f, indent=4, sort_keys=True)


if __name__ == '__main__':
    get_champion_list()
