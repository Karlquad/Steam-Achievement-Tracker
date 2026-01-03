import requests
import time
from datetime import datetime


def get_time_filters():
    now = int(time.time())
    return {
        "7d": now - 7 * 24 * 60 * 60,
        "30d": now - 30 * 24 * 60 * 60,
        "3m": now - 90 * 24 * 60 * 60,
        "1y": now - 365 * 24 * 60 * 60,
        "now": now
    }


def get_date_strings(filters):
    fmt = "%Y-%m-%d"
    return {
        "start_7": datetime.fromtimestamp(filters["7d"]).strftime(fmt),
        "end": datetime.fromtimestamp(filters["now"]).strftime(fmt),
        "start_30": datetime.fromtimestamp(filters["30d"]).strftime(fmt),
        "start_3m": datetime.fromtimestamp(filters["3m"]).strftime(fmt),
        "start_1y": datetime.fromtimestamp(filters["1y"]).strftime(fmt),
    }


def fetch_achievements(steam_id, api_key, session, filters, include_rarity=False):
    owned_url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={api_key}&steamid={steam_id}&include_appinfo=1"
    games = session.get(owned_url).json().get("response", {}).get("games", [])

    # Storage for achievements
    res = {"7d": [], "30d": [], "3m": [], "1y": []}

    for game in games:
        appid = str(game["appid"])
        ach_url = f"http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v1/?key={api_key}&steamid={steam_id}&appid={appid}"
        try:
            ach_data = session.get(ach_url).json()
            if "playerstats" in ach_data and "achievements" in ach_data["playerstats"]:
                for ach in ach_data["playerstats"]["achievements"]:
                    if ach["achieved"]:
                        ts = ach.get("unlocktime", 0)
                        info = {"appid": appid, "game": game["name"], "apiname": ach["apiname"]}
                        if ts > filters["7d"]: res["7d"].append(info)
                        if ts > filters["30d"]: res["30d"].append(info)
                        if ts > filters["3m"]: res["3m"].append(info)
                        if ts > filters["1y"]: res["1y"].append(info)
        except:
            continue

    if include_rarity:
        # Get rarity for 7d and 30d combined
        unique_ids = set(a["appid"] for a in res["7d"] + res["30d"])
        rarity_map = {}
        for aid in unique_ids:
            g_url = f"http://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v2/?gameid={aid}"
            g_data = session.get(g_url).json()
            for g_ach in g_data.get("achievementpercentages", {}).get("achievements", []):
                rarity_map[(aid, g_ach["name"])] = g_ach.get("percent", 0.0)

        # Attach rarity to the achievement objects
        for timeframe in ["7d", "30d"]:
            for a in res[timeframe]:
                a["percent"] = rarity_map.get((a["appid"], a["apiname"]), None)

    return res