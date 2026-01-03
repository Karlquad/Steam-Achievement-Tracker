import requests
import steam_engine as engine
import messenger
import config_PKK as cfg

session = requests.Session()
filters = engine.get_time_filters()
dates = engine.get_date_strings(filters)
all_stats = {}

for acc in cfg.ACCOUNTS:
    stats = engine.fetch_achievements(acc["id"], cfg.STEAM_API_KEY, session, filters)
    all_stats[acc["name"]] = stats

    msg = f"🏆 *{acc['name']}* unlocked {len(stats['7d'])} achievements this week!"
    messenger.send_msg(session, cfg.BOT_TOKEN, cfg.CHAT_ID, msg)

    # Optional: Send individual rare ones
    for ach in stats["7d"]:
        # Get the rarity and try to convert it to a float
        raw_percent = ach.get("percent")

        try:
            # Convert to float; if it's already a float or a string, this works
            percent_value = float(raw_percent) if raw_percent is not None else 100.0
        except (ValueError, TypeError):
            percent_value = 100.0

        if percent_value < 10.0:  # Now this comparison is safe
            m = f"🔥 Selten! {acc['name']} hat '{ach['apiname']}' in {ach['game']} ({percent_value:.1f}%)"
            messenger.send_msg(session, cfg.BOT_TOKEN, cfg.CHAT_ID, m)


messenger.send_chart(session, cfg.BOT_TOKEN, cfg.CHAT_ID, all_stats, [a["name"] for a in cfg.ACCOUNTS])