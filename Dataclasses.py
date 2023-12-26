
class Match:
    def __init__(self,match_id,win,kda,champion,champion_id):
        self.match_id = match_id
        self.win = win
        self.kda = kda
        self.champion = champion
        self.champion_id = champion_id

class Stats:
    def __init__(self,summoner_name,level,tier,rank,lp,winrate):
        self.summoner_name = summoner_name
        self.level = level
        self.tier = tier
        self.rank = rank
        self.lp = lp
        self.winrate = winrate

def game_count(g):
    return g.game_cnt

class ChampionStats:
    def __init__(self,champion_name,champion_id,game_cnt,kda,win,mastery):
        self.champion_name = champion_name
        self.champion_id = champion_id
        self.game_cnt = game_cnt
        self.kda = kda
        self.win = win
        self.mastery = mastery

    def out(self):
        return (str(self.champion_name)+ "\n" + " Game Count: " + str(self.game_cnt) + "\n Mastery: " + str(self.mastery) + "\nWinrate: {:10.2f}\nKDA: {:10.2f}\n".format(self.win,self.kda) + "\n")