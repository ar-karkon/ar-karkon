"""Fetch contribution stats from the GitHub GraphQL API into stats.json.

Needs GITHUB_TOKEN (the Actions token is enough).
"""
import datetime
import json
import os
import urllib.request

LOGIN = "ar-karkon"
QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}"},
    )
    with urllib.request.urlopen(req) as r:
        return json.load(r)["data"]["user"]


def streaks(days):
    longest = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] else 0
        longest = max(longest, run)
    current = 0
    # today may not have activity yet; don't let that break the streak
    for d in reversed(days[:-1] if days and not days[-1]["contributionCount"] else days):
        if not d["contributionCount"]:
            break
        current += 1
    return longest, current


def main():
    user = fetch()
    cal = user["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    longest, current = streaks(days)
    stats = {
        "contributions": cal["totalContributions"],
        "active_days": sum(1 for d in days if d["contributionCount"]),
        "longest_streak": longest,
        "current_streak": current,
        "followers": user["followers"]["totalCount"],
        "updated": datetime.date.today().isoformat(),
    }
    with open("stats.json", "w") as f:
        json.dump(stats, f, indent=2)
    print(stats)


main()
