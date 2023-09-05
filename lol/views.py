from urllib.parse import quote
from django.shortcuts import render
import requests


RIOT_API_KEY = "RGAPI-2d5cf26b-85f3-41af-8a41-a1f83478cc5f"
ACCOUNT_V1_API_URL = "https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{}/{}?api_key={}"
SUMMONER_V4_BY_PUUID_API_URL = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{}?api_key={}"
LEAGUE_V4_BY_ENCRYPTED_SUMMONER_ID_API_URL = "https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/{}?api_key={}"
LEAGUE_V4_CHALLENGER_LEAGUE_API_URL = "https://na1.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5?api_key={}"
MATCH_V5_LIST_BY_PUUID_API_URL = "https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{}/ids?type=ranked&start=0&count=5&api_key={}"
MATCH_V5_BY_MATCH_ID_API_URL = (
    "https://americas.api.riotgames.com/lol/match/v5/matches/{}?api_key={}"
)


def landing_lol(request):
    return render(request, "lol/landing_lol.html")


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
    print(url)
    data = get_data_from_api_url(url)
    puuid = data["puuid"]
    gameName = data["gameName"]
    tagLine = data["tagLine"]
    return puuid, gameName, tagLine


def get_player_data(puuid):
    url = SUMMONER_V4_BY_PUUID_API_URL.format(puuid, RIOT_API_KEY)
    print(url)
    data = get_data_from_api_url(url)
    id = data["id"]
    accountId = data["accountId"]
    puuid = data["puuid"]
    name = data["name"]
    profileIconId = data["profileIconId"]
    revisionDate = data["revisionDate"]
    summonerLevel = data["summonerLevel"]
    dd_profileIconId = f"http://ddragon.leagueoflegends.com/cdn/13.16.1/img/profileicon/{profileIconId}.png"
    # print(f"dd_profileIconId: {dd_profileIconId}")
    return (
        id,
        accountId,
        puuid,
        name,
        profileIconId,
        revisionDate,
        summonerLevel,
        dd_profileIconId,
    )


def get_player_rank(id):
    url = LEAGUE_V4_BY_ENCRYPTED_SUMMONER_ID_API_URL.format(id, RIOT_API_KEY)
    print(url)
    data = get_data_from_api_url(url)

    rank_data = []

    for entry in data:
        if (
            "queueType" in entry
            and "tier" in entry
            and "rank" in entry
            and "leaguePoints" in entry
            and "wins" in entry
            and "losses" in entry
        ):
            queueType = entry["queueType"]
            tier = entry["tier"].capitalize()
            rank = entry["rank"]
            leaguePoints = entry["leaguePoints"]
            wins = entry["wins"]
            losses = entry["losses"]
            rank_data.append(
                {
                    "queueType": queueType,
                    "tier": tier,
                    "rank": rank,
                    "leaguePoints": leaguePoints,
                    "wins": wins,
                    "losses": losses,
                }
            )
    return rank_data


def get_match_id_list(puuid):
    url = MATCH_V5_LIST_BY_PUUID_API_URL.format(puuid, RIOT_API_KEY)
    print(url)
    data = get_data_from_api_url(url)
    match_id_list = data
    print(match_id_list)
    return match_id_list


def get_match_history(match_id_list):
    match_history = []

    for match_id in match_id_list:
        url = MATCH_V5_BY_MATCH_ID_API_URL.format(match_id, RIOT_API_KEY)
        print(url)
        data = get_data_from_api_url(url)

        match_data = []
        participants_data = data["info"]["participants"]
        for player in participants_data:
            player_info = {
                "win": player["win"],
                "teamId": player["teamId"],
                "summonerName": player["summonerName"],
                "role": player["role"].capitalize(),
                "championName": player["championName"],
                "kills": player["kills"],
                "deaths": player["deaths"],
                "assists": player["assists"],
            }
            match_data.append(player_info)

        match_history.append(match_data)
        print(match_history)

    return match_history


def leaderboards_lol(request):
    url = LEAGUE_V4_CHALLENGER_LEAGUE_API_URL.format(RIOT_API_KEY)
    print(url)
    data = get_data_from_api_url(url)

    players = data["entries"]
    tier = data["tier"].capitalize()

    leaderboard_data = sorted(
        [
            {
                "summonerName": player.get("summonerName"),
                "leaguePoints": player.get("leaguePoints"),
                "tier": tier,
                "rank": player.get("rank"),
                "wins": player.get("wins"),
                "losses": player.get("losses"),
                "matchesPlayed": (
                    int(player.get("wins")) + int(player.get("losses"))
                ),
                "winPercentage": "{:.0%}".format(
                    int(player.get("wins"))
                    / (int(player.get("wins")) + int(player.get("losses")))
                ),
            }
            for player in players
        ],
        key=lambda x: x["leaguePoints"],
        reverse=True,
    )

    return render(
        request,
        "lol/leaderboards_lol.html",
        {"leaderboard_data": leaderboard_data},
    )


def search_lol(request):
    if request.method == "POST":
        gameName = request.POST.get("gameName")
        tagLine = request.POST.get("tagLine")

        try:
            puuid, _, _ = get_account(gameName, tagLine)
            player_data = get_player_data(puuid)
            rank_data = get_player_rank(player_data[0])
            match_id_list = get_match_id_list(puuid)
            match_history = get_match_history(match_id_list)

            return render(
                request,
                "lol/profile_lol.html",
                {
                    "player_data": player_data,
                    "rank_data": rank_data,
                    "match_history": match_history,
                },
            )
        except Exception as e:
            return render(request, "lol/landing_lol.html", {"error": str(e)})

    return render(request, "lol/landing_lol.html")
