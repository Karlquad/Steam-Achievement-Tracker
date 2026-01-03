import matplotlib.pyplot as plt
import numpy as np


def send_msg(session, token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    session.get(url, params={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})


def send_chart(session, token, chat_id, all_stats, users):
    timeframes = ["Last 7 Days", "Last 30 Days", "Last 3 Months", "Last Year"]
    x = np.arange(len(timeframes))
    width = 0.2
    plt.figure(figsize=(10, 6))

    for i, user in enumerate(users):
        counts = [len(all_stats[user][k]) for k in ["7d", "30d", "3m", "1y"]]
        plt.bar(x + i * width - width, counts, width, label=user)

    plt.xticks(x, timeframes)
    plt.ylabel("Achievements")
    plt.title("Steam Achievement Comparison")
    plt.legend()
    plt.savefig("chart.png")
    plt.close()

    with open("chart.png", "rb") as f:
        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        session.post(url, data={"chat_id": chat_id}, files={"photo": f})


def send_rarity_pie_chart(session, token, chat_id, user_stats, username):
    # Safely convert percentages to floats, defaulting to 100 if missing or invalid
    rarities = []
    for a in user_stats.get("7d", []):
        raw_val = a.get("percent")
        try:
            rarities.append(float(raw_val) if raw_val is not None else 100.0)
        except (ValueError, TypeError):
            rarities.append(100.0)

    # Now the comparisons will work correctly
    categories = {
        "Ultra Rare (<1%)": len([r for r in rarities if r < 1]),
        "Rare (1-10%)": len([r for r in rarities if 1 <= r < 10]),
        "Common (>10%)": len([r for r in rarities if r >= 10])
    }

    if sum(categories.values()) > 0:
        plt.figure(figsize=(6, 6))
        plt.pie(categories.values(), labels=categories.keys(), autopct='%1.1f%%', startangle=140)
        plt.title(f"Achievement Rarity Distribution: {username}")

        filename = f"rarity_{username}.png".lower()
        plt.savefig(filename)
        plt.close()

        with open(filename, "rb") as f:
            url = f"https://api.telegram.org/bot{token}/sendPhoto"
            session.post(url, data={"chat_id": chat_id}, files={"photo": f})