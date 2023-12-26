
import requests
from urllib.parse import urlencode
import time
from Dataclasses import *
import setting

class RiotHelper():

    @staticmethod
    def GetRiotId(summoner_name, tag, region = setting.DEFAULT_REGION):
        #Getting Encrypted RiotId by Name and Tag
        params = {
            'api_key': setting.API_KEY
        }
        api_url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{tag}"
        try:
            response = requests.get(api_url, params=urlencode(params))
            response.raise_for_status()
            RiotId =  response.json()['puuid']
        except requests.exceptions.RequestException as e:
            return None;
        #Getting Summoner Id

        return RiotId

    def GetMostPlayedChampions(self,matches,region_code = setting.DEFAULT_REGION_CODE):
        champs = []
        champ_stats = []

        for match in matches:
            if not (match.champion_id in champs):
                champs.append(match.champion_id)
                champ_stats.append(
                    ChampionStats(match.champion, match.champion_id, 1, match.kda, int(match.win)*100.0, 0))
            else:
                for stats in champ_stats:
                    if stats.champion_id == match.champion_id:
                        stats.game_cnt += 1
                        stats.kda += match.kda
                        stats.win += int(match.win)*100.0

        champ_stats.sort(key=game_count, reverse=True)
        champ_stats = champ_stats[:3]

        #Getting Mastery from Riot API and calculating winrate and overal KDA
        params = {
            'api_key': setting.API_KEY,
        }
        for stats in champ_stats:
            api_url = f"https://{region_code}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{self.riot_id}/by-champion/{stats.champion_id}"
            try:
                response = requests.get(api_url, params=urlencode(params))
                response.raise_for_status()
                mastery =  response.json()['championPoints']
            except requests.exceptions.RequestException as e:
                return None;
            stats.win = stats.win / stats.game_cnt
            stats.kda = stats.kda / stats.game_cnt
            stats.mastery = mastery

        return champ_stats

    def __init__(self,riotId):
        self.riot_id = riotId;

    def GetMathes(self,match_count = setting.MATCH_COUNT,region = setting.DEFAULT_REGION):
        #Getting Last N mathes
        params = {
            'api_key': setting.API_KEY,
            'count' : match_count
        }
        api_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{self.riot_id}/ids"
        try:
            response = requests.get(api_url, params=urlencode(params))
            response.raise_for_status()
            match_ids = response.json()
        except requests.exceptions.RequestException as e:
            return None;

        #Getting match stats(KDA, Champion Name, Win/Lose)

        mathes = []

        params = {
            'api_key': setting.API_KEY,
        }

        for match_id in match_ids:
            api_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
            time.sleep(0.075)
            try:
                response = requests.get(api_url, params=urlencode(params))
                response.raise_for_status()
                match =  response.json()
                player_id = match['metadata']['participants'].index(self.riot_id)
                player_info = match['info']['participants'][player_id]
                d = player_info['deaths']
                if d == 0: d = 1
                mathes.append(Match(match_id, player_info['win'],(player_info['kills']+player_info['assists'])/d,player_info['championName'],player_info['championId']))
            except requests.exceptions.RequestException as e:
                return None;
        return mathes

    def GetSummonerStats(self,matches,region_code = setting.DEFAULT_REGION_CODE):
        #Getting Summoner stats
        params = {
            'api_key': setting.API_KEY,
        }
        api_url = f"https://{region_code}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{self.riot_id}"
        try:
            response = requests.get(api_url, params=urlencode(params))
            response.raise_for_status()
            summoner_id = response.json()['id']
            level = response.json()['summonerLevel']
        except requests.exceptions.RequestException as e:
            return None;

        api_url = f"https://{region_code}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}"
        try:
            response = requests.get(api_url, params=urlencode(params))
            response.raise_for_status()
            league = response.json()
            if len(league) == 0:
                return None
            tier = league[0]['tier']
            rank = league[0]['rank']
            lp = league[0]['leaguePoints']
            name = league[0]['summonerName']

            winrate = 0
            gm_cnt = 0
            for match in matches:
                winrate += int(match.win)
                gm_cnt += 1


            return Stats(name,level,tier,rank,lp,(winrate*100.0)/gm_cnt)
        except requests.exceptions.RequestException as e:
            return None;