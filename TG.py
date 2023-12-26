import telebot
import setting
from db import *
from helpers import *
from Dataclasses import *

bot = telebot.TeleBot(setting.BOT_TOKEN, parse_mode=None)
matches = None

class TGBot():

    def polling(self):
        bot.infinity_polling()

    @bot.message_handler(commands=['start','change_account'])
    def start(message):
        sent_message = bot.send_message(message.chat.id,"Send your RiotId in Name#Tag Format")
        bot.register_next_step_handler(sent_message, TGBot.register_handler)


    def register_handler(message):
        TG_id = message.from_user.id
        if len(message.text.split('#')) < 2:
            bot.send_message(message.chat.id,"Wrong format. Please try again.")
        else:
            name = message.text.split('#')[0]
            tag = message.text.split('#')[1]
            RiotId = RiotHelper.GetRiotId(name, tag)
            if RiotId is not None:
                db = DB_req()
                db.WriteUser(TG_id, RiotId, name,tag)
                db.Close()
                bot.send_message(message.chat.id, f"Hello, {name}. You are succesfully registered.")
            else:
                bot.send_message(message.chat.id, f"Registration Error. There is no such Riot Account or Riot servers is not accessible.")


    @bot.message_handler(commands=['get_stats'])
    def get_stats(message):
        TG_id = message.from_user.id
        db = DB_req()
        Riot_id = db.GetRiotId(TG_id)
        RH = RiotHelper(Riot_id)
        matches = RH.GetMathes()
        stats = RH.GetSummonerStats(matches)
        if stats == None:
            bot.send_message(message.chat.id, "Something went wrong on Riot's side")
            return 0
        db.Close()
        bot.send_message(message.chat.id,f"Your stats: \n Summoner Name: {stats.summoner_name}\n Level: {stats.level}\n Winrate: {stats.winrate}%\n Tier: {stats.tier}\n Rank: {stats.rank}\n LP: {stats.lp}")
        sent_message = bot.send_message(message.chat.id, "Do you want to look at Champions Stats?(Y/N)")
        bot.register_next_step_handler(sent_message, TGBot.mathes_handler, Riot_id,RH, matches)

    def mathes_handler(message,riot_id, RH, matches):
        if message.text == "Y":
            champStats = RH.GetMostPlayedChampions(matches)
            out = ""
            db = DB_req()
            for stats in champStats:
                out += stats.out()
                # Write Champions
                db.WriteChampionStats(riot_id, stats.champion_name,stats.win,stats.kda,stats.mastery)
            db.Close()
            bot.send_message(message.chat.id,out)


    @bot.message_handler(commands=['check_progress'])
    def check_progress(message):
        TG_id = message.from_user.id
        db = DB_req()
        #Get riot_id
        Riot_id = db.GetRiotId(TG_id)
        #Get Summoner Stats
        o_stats = db.GetSummonerStats(Riot_id)

        #Get fresh stats from Riot API
        Riot_id = db.GetRiotId(TG_id)
        RH = RiotHelper(Riot_id)
        matches = RH.GetMathes()
        stats = RH.GetSummonerStats(matches)
        champStats = RH.GetMostPlayedChampions(matches)

        if o_stats.__getitem__(5) == None:
            bot.send_message(message.chat.id, "There is no previous progress entries")
        elif stats == None:
            bot.send_message(message.chat.id, "Can't get new data. Something wrong with Riot API")
        else:
            #Compare with last entry

            LP_diff = stats.lp - o_stats.__getitem__(7)
            tier = setting.Tier.index(stats.tier)-setting.Tier.index(o_stats.__getitem__(5))
            rank = setting.Rank.index(stats.rank)-setting.Rank.index(o_stats.__getitem__(6))
            LP_diff += 100 * rank + 400*tier

            Win_diff = o_stats.__getitem__(4) - stats.winrate
            bot.send_message(message.chat.id, "LP Gain: {}\n Winrate Gain: {:10.2f}".format(LP_diff*-1, Win_diff*-1))

        if stats != None:
            #Fill stats
            db.FillSummonerStats(Riot_id, stats.winrate, stats.tier, stats.rank, stats.lp)
            #Write last match
            db.WriteLastMatch(Riot_id, matches[0].match_id)
        db.Close()