from urllib.parse import quote
from django.shortcuts import render
import requests


RIOT_API_KEY = "RGAPI-a3f6bb49-0d83-4ce0-9856-a7132723d679"
ACCOUNT_V1_API_URL = "https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{}/{}?api_key={}"
SUMMONER_V4_BY_PUUID_API_URL = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{}?api_key={}"
LEAGUE_V4_BY_ENCRYPTED_SUMMONER_ID_API_URL = "https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/{}?api_key={}"
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
    return (
        id,
        accountId,
        puuid,
        name,
        profileIconId,
        revisionDate,
        summonerLevel,
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
            tier = entry["tier"]
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
            results = {
                "win": player["win"],
                "teamId": player["teamId"],
                "summonerName": player["summonerName"],
                "role": player["role"].capitalize(),
                "championName": player["championName"],
                "kills": player["kills"],
                "deaths": player.get("deaths"),
                "assists": player.get("assists"),
            }
            match_data.append(results)

        match_history.append(match_data)
        print(match_history)

    return match_history


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
            return render(request, "lol/layout.html", {"error": str(e)})

    return render(request, "lol/layout.html")
