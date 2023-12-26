import sqlite3
from Dataclasses import *

class DB_req:
    def __init__(self):
        self.conn = sqlite3.connect('LOL_Stats.db')
        self.cur = self.conn.cursor()

    def WriteUser(self,TG_id,Riot_id, Summoner_name, Tag):
        #Checking if such user exists
        self.cur.execute('SELECT COUNT(*) FROM Users WHERE [Telegram Id] = ?',(TG_id,))
        exist = self.cur.fetchone()
        if exist[0] > 0:
            self.cur.execute('UPDATE Users SET  [Riot Id] = ?, [Summoner Name]=?, [Tag]=? WHERE [Telegram Id] =  ?',(Riot_id, Summoner_name, Tag,TG_id))
            self.conn.commit()
        else:
            self.cur.execute('INSERT INTO Users ([Telegram Id], [Riot Id], [Summoner Name], [Tag]) VALUES (?, ?, ?,?)', (TG_id,Riot_id,Summoner_name,Tag))
            self.conn.commit()

    def GetRiotId(self,TG_id):
        self.cur.execute(f'SELECT [Riot Id] FROM Users WHERE [Telegram Id] = {TG_id}')
        stats = self.cur.fetchone()
        return stats[0]

    def GetSummonerStats(self, Riot_id):
        #Getting Summoner Stats from DB
        self.cur.execute('SELECT * FROM Users WHERE [Riot Id] = ?',(Riot_id,))
        stats = self.cur.fetchone()
        return stats

    def FillSummonerStats(self, Riot_id, Winrate, Tier, Rank, LP):
        #Filling extra rows in Users Stats Table
        self.cur.execute('UPDATE Users SET  [Winrate] = ?, [Tier]=?, [Rank]=?, [LP]=? WHERE [Riot Id] =  ?',(Winrate, Tier, Rank, LP, Riot_id))
        self.conn.commit()


    def WriteLastMatch(self, Riot_id, Match_id):
        #Writing or updating Last Match Id
        self.cur.execute('UPDATE Users SET  [Last Match Id]=?  WHERE [Riot Id] =  ?',(Match_id, Riot_id))
        self.conn.commit()


    def WriteChampionStats(self, Riot_id, Champion, Win, KDA, Mastery):
        #Writing Winrates and masteries on different Champions to DB
        self.cur.execute('SELECT COUNT(*) FROM Winrates WHERE [Riot ID] = ? AND [Champion]=?',(str(Riot_id),Champion))
        exist = self.cur.fetchone()
        if exist[0] > 0:
            self.cur.execute('UPDATE Winrates SET [Winrate]=?, [Mastery]=?, [KDA]=? WHERE [Riot ID] =  ? AND [Champion] = ?',( Win, Mastery, KDA, Riot_id, Champion))
            self.conn.commit()
        else:
            self.cur.execute('INSERT INTO Winrates ([Riot ID], [Champion], [Winrate],[Mastery],[KDA]) VALUES (?, ?, ?,?,?)',(Riot_id, Champion, Win, Mastery, KDA))
            self.conn.commit()

    def Close(self):
        self.conn.close()
