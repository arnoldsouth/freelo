from pkgutil import get_data
from urllib.parse import quote
from django.shortcuts import render
import requests


RIOT_API_KEY = "RGAPI-2d5cf26b-85f3-41af-8a41-a1f83478cc5f"
ACCOUNT_V1_API_URL = "https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{}/{}?api_key={}"
VAL_CONTENT_V1_BY_LOCALE_API_URL = "https://na.api.riotgames.com/val/content/v1/contents?locale=en-US&api_key={}"
VAL_RANKED_V1_BY_ACT_API_URL = "https://na.api.riotgames.com/val/ranked/v1/leaderboards/by-act/{}?size=200&startIndex=0&api_key={}"

HENRIK_V1_ACCOUNT_API_URL = (
    "https://api.henrikdev.xyz/valorant/v1/account/{}/{}"
)
HENRIK_V1_MMR_API_URL = "https://api.henrikdev.xyz/valorant/v1/mmr/na/{}/{}"
HENRIK_V2_MMR_API_URL = (
    "https://api.henrikdev.xyz/valorant/v2/mmr/na/{}/{}?season=e7a1"
)
HENRIK_V1_LIFETIME_MATCHES_API_URL = "https://api.henrikdev.xyz/valorant/v1/lifetime/matches/na/{}/{}?mode=competitive&size=5"
HENRIK_V2_MATCH_DETAIL_API_URL = (
    "https://api.henrikdev.xyz/valorant/v2/match/{}"
)

TIER_MAPPING = {
    24: "Immortal 1",
    25: "Immortal 2",
    26: "Immortal 3",
    27: "Radiant",
}


def get_tier(tier):
    return TIER_MAPPING.get(tier, tier)


def landing_val(request):
    return render(request, "val/landing_val.html")


def get_data_from_api_url(api_url):
    response = requests.get(api_url)
    response.raise_for_status()
    data = response.json()

    return data


def get_account(gameName, tagLine):
    encoded_gameName = quote(gameName)
    encoded_tagLine = quote(tagLine)
    url = ACCOUNT_V1_API_URL.format(
        encoded_gameName, encoded_tagLine, RIOT_API_KEY
    )
    data = get_data_from_api_url(url)

    puuid = data["puuid"]
    gameName = data["gameName"]
    tagLine = data["tagLine"]

    return puuid, gameName, tagLine


def get_content():
    url = VAL_CONTENT_V1_BY_LOCALE_API_URL.format(RIOT_API_KEY)
    data = get_data_from_api_url(url)

    acts = data["acts"]
    print(f"\nacts: {acts}")

    return acts


def get_active_act():
    acts = get_content()
    for act in acts:
        if act.get("type") == "act" and act.get("isActive") == True:
            print(f"\nactId: {act['id']}")
            return act["id"]


def get_leaderboards():
    actId = get_active_act()
    if not actId:
        return {}

    url = VAL_RANKED_V1_BY_ACT_API_URL.format(actId, RIOT_API_KEY)
    print(f"\nurl: {url}")
    data = get_data_from_api_url(url)

    return data


def leaderboards_val(request):
    leaderboard = get_leaderboards()

    players = leaderboard.get("players", [])

    leaderboard_data = [
        {
            "gameName": player.get("gameName"),
            "tagLine": player.get("tagLine"),
            "leaderboardRank": player.get("leaderboardRank"),
            "rankedRating": player.get("rankedRating"),
            "numberOfWins": player.get("numberOfWins"),
            "competitiveTier": "Radiant"
            if player.get("competitiveTier") == 27
            else (
                "Immortal 3"
                if player.get("competitiveTier") == 26
                else (
                    "Immortal 2"
                    if player.get("competitiveTier") == 25
                    else (
                        "Immortal 1"
                        if player.get("competitiveTier") == 24
                        else player.get("competitiveTier")
                    )
                )
            ),
        }
        for player in players
    ]

    return render(
        request,
        "val/leaderboards_val.html",
        {"leaderboard_data": leaderboard_data},
    )


def get_account_data(name, tag):
    encoded_name = quote(name)
    encoded_tag = quote(tag)
    url = HENRIK_V1_ACCOUNT_API_URL.format(encoded_name, encoded_tag)
    data = get_data_from_api_url(url)

    puuid = data["data"]["puuid"]
    account_level = data["data"]["account_level"]
    name = data["data"]["name"]
    tag = data["data"]["tag"]
    card = data["data"]["card"]["small"]

    return puuid, account_level, name, tag, card


def get_mmr_elo(name, tag):
    encoded_name = quote(name)
    encoded_tag = quote(tag)
    url = HENRIK_V1_MMR_API_URL.format(encoded_name, encoded_tag)
    data = get_data_from_api_url(url)

    currenttier = data["data"]["currenttier"]
    currenttierpatched = data["data"]["currenttierpatched"]
    images = data["data"]["images"]["small"]
    elo = data["data"]["elo"]

    return currenttier, currenttierpatched, images, elo


def get_mmr_record(name, tag):
    encoded_name = quote(name)
    encoded_tag = quote(tag)
    url = HENRIK_V2_MMR_API_URL.format(encoded_name, encoded_tag)
    data = get_data_from_api_url(url)

    number_of_games = data["data"]["number_of_games"]
    wins = data["data"]["wins"]
    losses = number_of_games - wins
    rank = data["data"]["final_rank_patched"]
    return wins, losses, rank


def get_match_id_list(name, tag):
    encoded_name = quote(name)
    encoded_tag = quote(tag)
    url = HENRIK_V1_LIFETIME_MATCHES_API_URL.format(encoded_name, encoded_tag)

    data = get_data_from_api_url(url)
    lifetime_matches_list = data["data"]

    match_id_list = [match["meta"]["id"] for match in lifetime_matches_list]
    # print(match_id_list)
    return match_id_list


def get_match_history(match_id_list):
    match_history = []

    for match_id in match_id_list:
        url = HENRIK_V2_MATCH_DETAIL_API_URL.format(match_id)
        data = get_data_from_api_url(url)

        match_data = []
        player_data = data["data"]["players"]["all_players"]

        for player in player_data:
            player_info = {
                "name": player["name"],
                "tag": player["tag"],
                "team": player["team"],
                "character": player["character"],
                "currenttier": player["currenttier"],
                "currenttier_patched": player["currenttier_patched"],
                "agent_icon": player["assets"]["agent"]["small"],
                "score": player["stats"]["score"],
                "kills": player["stats"]["kills"],
                "deaths": player["stats"]["deaths"],
                "assists": player["stats"]["assists"],
                "headshots": player["stats"]["headshots"],
            }
            match_data.append(player_info)

        match_history.append(match_data)

        print(match_history)

    return match_history


def search_val(request):
    if request.method == "POST":
        name = request.POST.get("name")
        tag = request.POST.get("tag")

        try:
            account_data = get_account_data(name, tag)
            mmr_elo = get_mmr_elo(name, tag)
            mmr_record = get_mmr_record(name, tag)
            match_id_list = get_match_id_list(name, tag)
            match_history = get_match_history(match_id_list)

            return render(
                request,
                "val/profile_val.html",
                {
                    "account_data": account_data,
                    "mmr_elo": mmr_elo,
                    "mmr_record": mmr_record,
                    "match_history": match_history,
                },
            )
        except Exception as e:
            return render(request, "val/landing_val.html", {"error": str(e)})

    return render(request, "val/landing_val.html")
