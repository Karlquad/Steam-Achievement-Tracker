import requests
import steam_engine as engine
import messenger
import config_Markus as cfg

session = requests.Session()
filters = engine.get_time_filters()
dates = engine.get_date_strings(filters)

all_stats = {}
for acc in cfg.ACCOUNTS:
    # 1. Fetch data with rarity enabled
    stats = engine.fetch_achievements(acc["id"], cfg.STEAM_API_KEY, session, filters, include_rarity=True)
    all_stats[acc["name"]] = stats

    # 2. Send the general summary
    summary = (
        f"🏆 *{acc['name']}* hat *{len(stats['7d'])} Herausforderungen* freigeschalten (letzte 7 Tage).\n"
        f"📅 *{len(stats['30d'])} Herausforderungen* in den letzten 30 Tagen."
    )
    messenger.send_msg(session, cfg.BOT_TOKEN, cfg.CHAT_ID, summary)

    # 3. Loop through achievements to find the "Ultra Rare" ones to highlight
    for ach in stats["7d"]:
        raw_percent = ach.get("percent")
        try:
            percent_value = float(raw_percent) if raw_percent is not None else 100.0
        except (ValueError, TypeError):
            percent_value = 100.0

        if percent_value < 10.0:
            m = f"🔥 Selten! {acc['name']} hat '{ach['apiname']}' in {ach['game']} ({percent_value:.1f}%)"
            messenger.send_msg(session, cfg.BOT_TOKEN, cfg.CHAT_ID, m)

    # 4. NOW call the pie chart function (placed outside the 'for ach' loop but inside 'for acc')
    # messenger.send_rarity_pie_chart(session, cfg.BOT_TOKEN, cfg.CHAT_ID, stats, acc["name"])

# 5. Finally, send the comparison bar chart for everyone
messenger.send_chart(session, cfg.BOT_TOKEN, cfg.CHAT_ID, all_stats, [a["name"] for a in cfg.ACCOUNTS])