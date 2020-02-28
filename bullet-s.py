from lxml import html
import requests
import time
import os
import csv
from datetime import datetime
import xml.etree.ElementTree as ET
from operator import itemgetter

bullet_colors = {
    'Green': "#00FF40",
    'Orange': "#FF9633",
    'Yellow': "#FFFF33"
}

team_abbrevs = {
    'Luleå': 'LHF',
    'Örebro': 'ÖRE',
    'Färjestad': 'FBK',
    'Frölunda': 'FHC',
    'Rögle': 'RBK',
    'Skellefteå': 'SKE',
    'Djurgården': 'DIF',
    'HV71': 'HV71',
    'Malmö': 'MIF',
    'Växjö': 'VLH',
    'Brynäs': 'BIF',
    'Linköping': 'LHC',
    'Leksand': 'LIF',
    'Oskarshamn': 'IKO'
}

team_long_names = {
    'LHF': 'Luleå',
    'ÖRE': 'Örebro',
    'FBK': 'Färjestad',
    'FHC': 'Frölunda',
    'RBK': 'Rögle',
    'SKE': 'Skellefteå',
    'DIF': 'Djurgården',
    'HV71': 'HV71',
    'MIF': 'Malmö',
    'VLH': 'Växjö',
    'BIF': 'Brynäs',
    'LHC': 'Linköping',
    'LIF': 'Leksand',
    'IKO': 'Oskarshamn'
}

team_logos = {
    'Luleå': 'LHF',
    'Örebro': 'OHK',
    'Färjestad': 'FBK',
    'Frölunda': 'FHC',
    'Rögle': 'RBK',
    'Skellefteå': 'SKE',
    'Djurgården': 'DIF',
    'HV71': 'HV71',
    'Malmö': 'MIF',
    'Växjö': 'VLH',
    'Brynäs': 'BIF',
    'Linköping': 'LHC',
    'Leksand': 'LIF',
    'Oskarshamn': 'IKO'
}

month_names_short = {
    '01': 'JAN',
    '02': 'FEB',
    '03': 'MAR',
    '04': 'APR',
    '05': 'MAJ',
    '06': 'JUN',
    '07': 'JUL',
    '08': 'AUG',
    '09': 'SEP',
    '10': 'OKT',
    '11': 'NOV',
    '12': 'DEC'
}

def get_team_urls():
    teams_page = requests.get("https://www.shl.se/statistik/tabell?season=&gameType=regular")
    teams_tree = html.fromstring(teams_page.content)
    team_links = {}
    for team in teams_tree.xpath('//table[@class="rmss_t-stat-table rmss_t-scrollable-table"]//tr'):
        team_url = team.xpath('td//a/@href')
        team_name = team.xpath('td//a/span[@class="rmss_t--unpinned-hide"]/text()')
        if (len(team_url) > 0 and len(team_name) > 0):
            team_links.update({ team_name[0]: team_url[0] })
    return team_links

def get_team_names():
    teams_page = requests.get("https://www.shl.se/statistik/tabell?season=&gameType=regular")
    teams_tree = html.fromstring(teams_page.content)
    team_names = {}
    for team in teams_tree.xpath('//table[@class="rmss_t-stat-table rmss_t-scrollable-table"]//tr'):
        team_name = team.xpath('td//a/span[@class="rmss_t--pinned-hide"]/text()')
        team_abbrev = team.xpath('td//a/span[@class="rmss_t--unpinned-hide"]/text()')
        if (len(team_abbrev) > 0 and len(team_name) > 0):
            team_names.update({ team_abbrev[0]: team_name[0] })
    return team_names

def get_roster_url(teamurl):
    team_page = requests.get("https://www.shl.se" + teamurl)
    team_tree = html.fromstring(team_page.content)
    return team_tree.xpath('//a[text()="Trupp"]/@href')[0]

def find_opposing_team(game, team):
    if (game[1] == team):
        return game[2]
    else:
        return game[1]

def handle_game(game, position, own_team):
    own_team_short = team_abbrevs[own_team]
    opponent = find_opposing_team(game, own_team_short)
    if (position == "Målvakt"):
        if (game[4] == 'Ej med i laguppställningen denna match'):
            handled_game = {
                'played': False,
                'date': game[0],
                'hometeam': game[1],
                'awayteam': game[2],
                'opponent': opponent,
                'league': game[3],
                'played': 0,
                'started': 0,
                'won': 0,
                'ga': 0,
                'gaa': 0,
                'so': 0,
                'soga': 0,
                'svs': 0,
                'svspercent': 0,
                'mip': 0
            }
        else:
            handled_game = {
                'played': True,
                'date': game[0],
                'hometeam': game[1],
                'awayteam': game[2],
                'opponent': opponent,
                'league': game[3],
                'played': game[4],
                'started': game[5],
                'won': game[6],
                'ga': game[7],
                'gaa': game[8],
                'so': game[9],
                'soga': game[10],
                'svs': game[11],
                'svspercent': game[12],
                'mip': game[13]
            }
    else:
        if (game[4] == 'Ej med i laguppställningen denna match'):
            handled_game = {
                'played': False,
                'date': game[0],
                'hometeam': game[1],
                'awayteam': game[2],
                'opponent': opponent,
                'league': game[3],
                'goals': 0,
                'assists': 0,
                'points': 0,
                'plusminus': 0,
                'pim': 0,
                'ppg': 0,
                'shg': 0,
                'gwg': 0,
                'sog': 0,
                'hits': 0,
                'toi': 0
            }
        else:
            handled_game = {
                'played': True,
                'date': game[0],
                'hometeam': game[1],
                'awayteam': game[2],
                'opponent': opponent,
                'league': game[3],
                'goals': int(game[4]),
                'assists': int(game[5]),
                'points': int(game[6]),
                'plusminus': int(game[7]),
                'pim': int(game[8]),
                'ppg': int(game[9]),
                'shg': int(game[10]),
                'gwg': int(game[11]),
                'sog': int(game[12]),
                'hits': int(game[13]),
                'toi': game[14]
            }
    return handled_game

def get_player_stats(teamurl):
    url = 'https://www.shl.se' + teamurl
    roster = requests.get(url)
    roster_tree = html.fromstring(roster.content)

    player_links = roster_tree.xpath('//div[@class="rmss_c-squad__team-cont-roster-group"]//div[@class="rmss_c-squad__team-cont-roster-group-item"]/a/@href')

    players = []

    for player in player_links:
        gamelog_link = "https://www.shl.se" + player + "/gamelog"
        gamelog_page = requests.get(gamelog_link)
        gamelog_tree = html.fromstring(gamelog_page.content)
        player_number = gamelog_tree.xpath('//div[@class="rmss_c-squad__player-header-name-jersey"]//text()')
        player_name = gamelog_tree.xpath('//header[@class="rmss_c-squad__player-header-name-h"]/text()')
        player_position = gamelog_tree.xpath('//span[@class="rmss_c-squad__player-header-name-info-position"]/text()')
        player_team = gamelog_tree.xpath('//span[@class="rmss_c-squad__player-header-name-info-team"]/text()')
        player_birthday = gamelog_tree.xpath('//div[@class="rmss_c-squad__player-header-info-items-item"]/span[text()="Född"]/../span[@class="rmss_c-squad__player-header-info-items-item-value"]/text()')
        player_age = gamelog_tree.xpath('//div[@class="rmss_c-squad__player-header-info-items-item"]/span[text()="Ålder"]/../span[@class="rmss_c-squad__player-header-info-items-item-value"]/text()')
        player_nationality = gamelog_tree.xpath('//div[@class="rmss_c-squad__player-header-info-items-item"]/span[text()="Nationalitet"]/../span[@class="rmss_c-squad__player-header-info-items-item-value"]/text()')
        player_length = gamelog_tree.xpath('//div[@class="rmss_c-squad__player-header-info-items-item"]/span[text()="Längd"]/../span[@class="rmss_c-squad__player-header-info-items-item-value"]/text()')
        player_weight = gamelog_tree.xpath('//div[@class="rmss_c-squad__player-header-info-items-item"]/span[text()="Vikt"]/../span[@class="rmss_c-squad__player-header-info-items-item-value"]/text()')
        # Ful-fix (händer bara om en spelare är ny och inte fått något nummer än; "Lias-tillbaka-i-HV71-syndromet")
        if (len(player_number) == 0):
            player_number = ["", ""]
        if (player_position == "Målvakt"):
            player_handed = gamelog_tree.xpath('//div[@class="rmss_c-squad__player-header-info-items-item"]/span[text()="Plockar"]/../span[@class="rmss_c-squad__player-header-info-items-item-value"]/text()')
        else:
            player_handed = gamelog_tree.xpath('//div[@class="rmss_c-squad__player-header-info-items-item"]/span[text()="Skjuter"]/../span[@class="rmss_c-squad__player-header-info-items-item-value"]/text()')
        games = []
        if (len(player_handed) == 0):
            player_handed = ["-", "-"]
        for row in gamelog_tree.xpath('//table[@class="rmss_t-stat-table rmss_t-scrollable-table"]//tr'):
            game = row.xpath('td//text()')
            if (len(game) > 2):
                games.append(handle_game(game, player_position[0], player_team[0]))
        extra_player_info = gamelog_tree.xpath('//td[@class="rmss_t-stat-table__row-item rmss_t--stat-table__align-left rmss_t--stat-table__item-highlight"]/text()')
        player_flag = False
        if (len(extra_player_info) > 0):
            if (" bytte lag " in extra_player_info[0]):
                player_flag = True
        players.append({ 
            'number': player_number[1], 
            'name': player_name[0],
            'team': player_team[0],
            'position': player_position[0],
            'birthday': player_birthday[0],
            'age': player_age[0],
            'nationality': player_nationality[0],
            'length': player_length[0],
            'weight': player_weight[0],
            'handedness': player_handed[0],
            'flagged': player_flag,
            'games': games
        })
    return sorted(players, key = lambda i: i['number'])

def format_date_for_bullet(date_in):
    date_split = date_in.split('-')
    if (len(date_split) == 3):
        return str(int(date_split[2])) + " " + month_names_short[date_split[1]] + " " + date_split[0]
    else:
        return date_in

def get_full_team_name(shortname):
    if shortname in team_long_names:
        return team_long_names[shortname].upper()
    else:
        return shortname.upper()

def goals_in_last_game(player):
    bullet = {}
    teams = get_team_names()
    if (len(player['games']) > 0):
        if (player['games'][0]['played']):
            if (player['games'][0]['goals'] > 0):
                bullet = {
                    'text': str(player['games'][0]['goals']) + " MÅL SENAST MOT " + get_full_team_name(player['games'][0]['opponent']),
                    'number': player['number'],
                    'name': player['name'],
                    'team_logo': team_logos[player['team']],
                    'color': bullet_colors['Green'],
                    'description': str(player['games'][0]['goals']) + "G SENAST"
                }
    return bullet

def points_in_last_game(player):
    bullet = {}
    teams = get_team_names()
    if (len(player['games']) > 0):
        if (player['games'][0]['played']):
            if (player['games'][0]['points'] > 1):
                bullet = {
                    'text': str(player['games'][0]['points']) + " POÄNG (" + str(player['games'][0]['goals']) + "+" + str(player['games'][0]['assists']) + ") SENAST MOT " + get_full_team_name(player['games'][0]['opponent']),
                    'number': player['number'],
                    'name': player['name'],
                    'team_logo': team_logos[player['team']],
                    'color': bullet_colors['Green'],
                    'description': str(player['games'][0]['points']) + "P SENAST"
                }
    return bullet

def goal_streak(player):
    bullet = {}
    if (len(player['games']) > 0):
        last_game = player['games'][0]
        if (last_game['played'] and last_game['goals'] > 0):
            length_of_streak = 1
            number_of_goals = 0
            while (player['games'][length_of_streak]['played'] and player['games'][length_of_streak]['goals'] > 0 and length_of_streak < len(player['games'])):
                length_of_streak += 1
            if (length_of_streak > 1):
                for i in range(length_of_streak):
                    number_of_goals += player['games'][i]['goals']
                bullet = {
                    'text': "MÅL I " + str(length_of_streak) + " RAKA MATCHER  |  " + str(number_of_goals) + " MÅL",
                    'number': player['number'],
                    'name': player['name'],
                    'team_logo': team_logos[player['team']],
                    'color': bullet_colors['Green'],
                    'description': "MÅL " + str(length_of_streak) + " RAKA"
                }
    return bullet

def point_streak(player):
    bullet = {}
    if (len(player['games']) > 0):
        last_game = player['games'][0]
        if (last_game['played'] and last_game['points'] > 0):
            length_of_streak = 1
            number_of_points = 0
            number_of_goals = 0
            number_of_assists = 0
            while (player['games'][length_of_streak]['played'] and 0 < player['games'][length_of_streak]['points'] and length_of_streak < len(player['games'])):
                length_of_streak += 1
            if (length_of_streak > 2):
                for i in range(length_of_streak):
                    number_of_points += player['games'][i]['points']
                    number_of_goals += player['games'][i]['goals']
                    number_of_assists += player['games'][i]['assists']
                bullet = {
                    'text': "POÄNG I " + str(length_of_streak) + " RAKA MATCHER  |  " + str(number_of_points) + " POÄNG (" + str(number_of_goals) + "+" + str(number_of_assists) + ")",
                    'number': player['number'],
                    'name': player['name'],
                    'team_logo': team_logos[player['team']],
                    'color': bullet_colors['Green'],
                    'description': "P " + str(length_of_streak) + " RAKA"
                }
    return bullet

def played_and_points(game):
    if (game['played'] and game['points'] > 0):
        return True
    else:
        return False

def create_point_form_bullet(points, goals, assists, streak, player):
    return {
        'text': str(points) + " POÄNG (" + str(goals) + "+" + str(assists) + ") DE " + str(streak) + " SENASTE MATCHERNA",
        'number': player['number'],
        'name': player['name'],
        'team_logo': team_logos[player['team']],
        'color': bullet_colors['Green'],
        'description': str(points) + "P LAST" + str(streak)
    }

def calculate_streak_totals(games, length_of_streak):
    points = 0
    goals = 0
    assists = 0
    for i in range(length_of_streak):
        points += games[i]['points']
        goals += games[i]['goals']
        assists += games[i]['assists']
    return [points, goals, assists]

def points_recently(player):
    streak = {}
    if (len(player['games']) > 0):
        length_of_streak = 0
        count = 0
        while (len(player['games']) > count + 1 and (played_and_points(player['games'][count]) or played_and_points(player['games'][count + 1]))):
            length_of_streak += 1
            count += 1
        if (length_of_streak > 1):
            streak_totals = calculate_streak_totals(player['games'], length_of_streak)
            if (length_of_streak > 3):
                if (streak_totals[0] >= length_of_streak - 1):
                    streak = create_point_form_bullet(streak_totals[0], streak_totals[1], streak_totals[2], length_of_streak, player)
                else:
                    length_of_streak = 0
                    count = 0
                    while (len(player['games']) > count + 1 and (played_and_points(player['games'][count]) or played_and_points(player['games'][count + 1]))):
                        length_of_streak += 1
                        count += 1
                        current_points = calculate_streak_totals(player['games'], length_of_streak)
                        if (length_of_streak > current_points[0]):
                            streak_totals = current_points
                            length_of_streak -= 1
                            break
                    if (length_of_streak > 1):
                        streak = create_point_form_bullet(streak_totals[0], streak_totals[1], streak_totals[2], length_of_streak, player)
            else:
                if (streak_totals[0] >= length_of_streak):
                    streak = create_point_form_bullet(streak_totals[0], streak_totals[1], streak_totals[2], length_of_streak, player)
    return streak

def played_and_goals(game):
    if (game['played'] and game['goals'] > 0):
        return True
    else:
        return False

def create_goal_form_bullet(goals, streak, player):
    return {
        'text': str(goals) + " MÅL DE " + str(streak) + " SENASTE MATCHERNA",
        'number': player['number'],
        'name': player['name'],
        'team_logo': team_logos[player['team']],
        'color': bullet_colors['Green'],
        'description': str(goals) + "G LAST" + str(streak)
    }

def calculate_goal_totals(games, length_of_streak):
    goals = 0
    for i in range(length_of_streak):
        goals += games[i]['goals']
    return goals

def goals_recently(player):
    bullet = {}
    if (len(player['games']) > 0):
        length_of_streak = 0
        count = 0
        while (len(player['games']) > count + 1 and (played_and_goals(player['games'][count]) or played_and_goals(player['games'][count + 1]))):
            length_of_streak += 1
            count += 1
        if (length_of_streak > 1):
            streak_totals = calculate_goal_totals(player['games'], length_of_streak)
            if (length_of_streak > 3):
                if (streak_totals >= length_of_streak - 1):
                    bullet = create_goal_form_bullet(streak_totals, length_of_streak, player)
                else:
                    length_of_streak = 0
                    count = 0
                    while (len(player['games']) > count + 1 and (played_and_goals(player['games'][count]) or played_and_goals(player['games'][count + 1]))):
                        length_of_streak += 1
                        count += 1
                        current_goals = calculate_goal_totals(player['games'], length_of_streak)
                        if (length_of_streak > current_goals):
                            streak_totals = current_goals
                            length_of_streak -= 1
                            break
                    if (length_of_streak > 1):
                        bullet = create_goal_form_bullet(streak_totals, length_of_streak, player)
            else:
                if (streak_totals >= length_of_streak):
                    bullet = create_goal_form_bullet(streak_totals, length_of_streak, player)
    return bullet

def game_was_vs_opponent(own_team, game, opponent):
    if (game['hometeam'] == own_team and game['awayteam'] == opponent):
        return True
    elif (game['hometeam'] == opponent and game['awayteam'] == own_team):
        return True
    return False

def points_against_opponent(player, own_team, opponent):
    games_against_opponent = []
    teams = get_team_names()
    bullet = {}
    for game in player['games']:
        if (game['played'] and game_was_vs_opponent(own_team, game, opponent)):
            games_against_opponent.append(game)
    if (len(games_against_opponent) > 0):
        point_totals = calculate_streak_totals(games_against_opponent, len(games_against_opponent))
        if (len(games_against_opponent) > 1):
            if point_totals[0] > 1:
                bullet = {
                    'text': str(point_totals[0]) + " POÄNG (" + str(point_totals[1]) + "+" + str(point_totals[2]) + ") PÅ " + str(len(games_against_opponent)) + " MATCHER MOT " + get_full_team_name(games_against_opponent[0]['opponent']),
                    'number': player['number'],
                    'name': player['name'],
                    'team_logo': team_logos[player['team']],
                    'color': bullet_colors['Green'],
                    'description': str(point_totals[0]) + "P V. " + teams[games_against_opponent[0]['opponent']].upper()
                }
        else:
            if point_totals[0] > 1:
                bullet = {
                    'text': "GJORDE " + str(point_totals[0]) + " POÄNG (" + str(point_totals[1]) + "+" + str(point_totals[1]) + ") " + format_date_for_bullet(games_against_opponent[0]['date']) + " MOT " + get_full_team_name(games_against_opponent[0]['opponent']),
                    'number': player['number'],
                    'name': player['name'],
                    'team_logo': team_logos[player['team']],
                    'color': bullet_colors['Green'],
                    'description': str(point_totals[0]) + "P V. " + teams[games_against_opponent[0]['opponent']].upper() + " 1 MATCH"
                }
    return bullet

def goals_against_opponent(player, own_team, opponent):
    games_against_opponent = []
    teams = get_team_names()
    bullet = {}
    for game in player['games']:
        if (game['played'] and game_was_vs_opponent(own_team, game, opponent) and game['goals'] > 0):
            games_against_opponent.append(game)
    if (len(games_against_opponent) > 0):
        goals = 0
        for game in games_against_opponent:
            goals += game['goals']
        if (len(games_against_opponent) > 1):
            bullet = {
                'text': str(goals) + " MÅL PÅ " + str(len(games_against_opponent)) + " MATCHER MOT " + get_full_team_name(games_against_opponent[0]['opponent']),
                'number': player['number'],
                'name': player['name'],
                'team_logo': team_logos[player['team']],
                'color': bullet_colors['Green'],
                'description': str(goals) + "G V. " + teams[games_against_opponent[0]['opponent']].upper()
            }
        else:
            bullet = {
                'text': "GJORDE " + str(goals) + " MÅL " + format_date_for_bullet(games_against_opponent[0]['date']) + " MOT " + get_full_team_name(games_against_opponent[0]['opponent']),
                'number': player['number'],
                'name': player['name'],
                'team_logo': team_logos[player['team']],
                'color': bullet_colors['Green'],
                'description': str(goals) + "G V. " + teams[games_against_opponent[0]['opponent']].upper() + " 1 MATCH"
            }
    return bullet

def player_played_and_no_goals(game):
    if (game['played'] and game['goals'] == 0):
        return True
    else:
        return False

def goalless_streak(player):
    bullet = {}
    teams = get_team_names()
    if (len(player['games']) > 4):
        if (player_played_and_no_goals(player['games'][1]) and player_played_and_no_goals(player['games'][2]) and player_played_and_no_goals(player['games'][3])):
            count = 3
            if (player['games'][0]['goals'] > 0):
                while (len(player['games']) > count):
                    if (player_played_and_no_goals(player['games'][count])):
                        count += 1
                    else:
                        break
                bullet = {
                    'text': str(player['games'][0]['goals']) + " MÅL SENAST MOT " + get_full_team_name(player['games'][0]['opponent']) + "  |  INNAN DET:  " + str(count - 1) + " RAKA MATCHER UTAN MÅL",
                    'number': player['number'],
                    'name': player['name'],
                    'team_logo': team_logos[player['team']],
                    'color': bullet_colors['Green'],
                    'description': "BRUTIT " + str(count - 1) + "GS MÅLTORKA"
                }
            else:
                count += 1
                while (player_played_and_no_goals(player['games'][count]) and len(player['games']) > count):
                    count += 1
                    if (count >= len(player['games'])):
                        break
                bullet = {
                    'text': "IKVÄLL:  X MÅL  |  INNAN DET:  " + str(count) + " RAKA MATCHER UTAN MÅL",
                    'number': player['number'],
                    'name': player['name'],
                    'team_logo': team_logos[player['team']],
                    'color': bullet_colors['Orange'],
                    'description': "UPP. OM MÅL - BRUTIT " + str(count) + "GS MÅLTORKA"
                }
    return bullet

def player_played_and_no_points(game):
    if (game['points'] == 0 and game['played']):
        return True
    else:
        return False

def pointless_streak(player):
    bullet = {}
    teams = get_team_names()
    if (len(player['games']) > 4):
        if (player_played_and_no_points(player['games'][1]) and player_played_and_no_points(player['games'][2]) and player_played_and_no_points(player['games'][3])):
            count = 3
            if (player['games'][0]['points'] > 0):
                while (len(player['games']) > count):
                    if (player_played_and_no_points(player['games'][count])):
                        count += 1
                    else:
                        break
                bullet = {
                    'text': str(player['games'][0]['points']) + " POÄNG (" + str(player['games'][0]['goals']) + "+" + str(player['games'][0]['assists']) + ") SENAST MOT " + get_full_team_name(player['games'][0]['opponent']) + "  |  INNAN DET:  " + str(count - 1) + " MATCHER UTAN POÄNG",
                    'number': player['number'],
                    'name': player['name'],
                    'team_logo': team_logos[player['team']],
                    'color': bullet_colors['Green'],
                    'description': "BRUTIT " + str(count - 1) + "GS POÄNGTORKA"
                }
            else:
                count += 1
                while (player_played_and_no_points(player['games'][count]) and len(player['games']) > count):
                    count += 1
                    if (count > len(player['games'])):
                        break
                bullet = {
                    'text': "IKVÄLL:  Z POÄNG (X+Y)  |  INNAN DET:  " + str(count) + " MATCHER UTAN POÄNG",
                    'number': player['number'],
                    'name': player['name'],
                    'team_logo': team_logos[player['team']],
                    'color': bullet_colors['Orange'],
                    'description': "UPP. OM P - BRUTIT " + str(count) + "GS POÄNGTORKA"
                }
    return bullet

def add_XMLNS_attributes(tree, xmlns_uris_dict):
    if not ET.iselement(tree):
        tree = tree.getroot()
    for prefix, uri in xmlns_uris_dict.items():
        tree.attrib[prefix] = uri

def bullet_name_formatter(name):
    split = name.split(" ")
    if (len(split) > 1):
        return split[1]
    else:
        return name

def generate_xml_bullet(bullet, team_path, bullet_count):
    text = bullet['text']
    number = bullet['number']
    name = bullet['name']
    logo = bullet['team_logo']
    color = bullet['color']
    description = bullet['description']
    bullet_name = "#" + number + " " + bullet_name_formatter(name.upper()) + " - " + description
    xmlns_uris = {
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xmlns:xsd': 'http://www.w3.org/2001/XMLSchema',
        'Name': bullet_name,
        'Color': color,
        'SignId': "11"
    }
    snapshot = ET.Element("SnapShot")
    # Här kommer "huvuddelen"
    cache = ET.SubElement(snapshot, "Cache")
    #   Spelarnamn
    fval10 = ET.SubElement(cache, "Fval", Field="10")
    value10 = ET.SubElement(fval10, "Value").text = name
    #   Text/info
    fval100 = ET.SubElement(cache, "Fval", Field="100")
    table100 = ET.SubElement(fval100, "Table", Reverse="false")
    table100_2 = ET.SubElement(table100, "Table")
    tablerow = ET.SubElement(table100_2, "TableRow", RowNr="1")
    tablerow_row = ET.SubElement(tablerow, "Row")
    tablecell_1 = ET.SubElement(tablerow_row, "TableCell", Name="1")
    tablecell_1_value = ET.SubElement(tablecell_1, "Value").text = text
    #   OBS - Text/info-fält nummer 2
    tablecell_2 = ET.SubElement(tablerow_row, "TableCell", Name="2")
    tablecell_2_value = ET.SubElement(tablecell_2, "Value")
    #   Laglogga
    fval11 = ET.SubElement(cache, "Fval", Field="11")
    value11 = ET.SubElement(fval11, "Value").text = logo
    #   Spelarnummer
    fval12 = ET.SubElement(cache, "Fval", Field="12")
    value12 = ET.SubElement(fval12, "Value").text = number
    #   tomt
    fval13 = ET.SubElement(cache, "Fval", Field="13")
    value13 = ET.SubElement(fval13, "Value")
    #   Vet ej
    fval99 = ET.SubElement(cache, "Fval", Field="99")
    value99 = ET.SubElement(fval99, "Value").text = "1"
    #   Resten av filen
    siselect = ET.SubElement(snapshot, "SiSelect xsi:nil='true'")
    highlightqueue = ET.SubElement(snapshot, "HighlightQueue")
    groups = ET.SubElement(highlightqueue, "Groups")
    hiddenfields = ET.SubElement(snapshot, "HiddenFields", Fields="200;300;400")
    infoformatstring = ET.SubElement(snapshot, "InfoFormatString").text = '[{1}]{2}.{0} {3};10;11;12;13'
    # Dags att skjuta ut xml-filen!
    tree = ET.ElementTree(snapshot)
    filename = number + "_" + ''.join(name.split(" ")) + "_bullet" + str(bullet_count) + ".xml"
    add_XMLNS_attributes(snapshot, xmlns_uris)
    tree.write(team_path + filename, xml_declaration=True, encoding="utf-16", method="xml")

def generate_player_bullets(players, own_team, opponent, dir_path):
    bullets = []
    for player in players:
        if (player['position'] != 'Målvakt'):
            all_bullets = [
                goals_in_last_game(player),
                points_in_last_game(player),
                goal_streak(player),
                point_streak(player),
                points_recently(player),
                goals_recently(player),
                points_against_opponent(player, own_team, opponent),
                goals_against_opponent(player, own_team, opponent),
                goalless_streak(player),
                pointless_streak(player)
            ]
            for bullet in all_bullets:
                if (len(bullet) > 0):
                    if (player['flagged']):
                        bullet['color'] = bullet_colors['Yellow']
                    bullets.append(bullet)
    team_dir_path = dir_path + own_team + "/"
    os.makedirs(os.path.dirname(team_dir_path), exist_ok=True)
    txt_file = open(team_dir_path + own_team + "_bullets.txt", "w+")
    bullet_count = 0
    for bullet in bullets:
        bullet_count += 1
        generate_xml_bullet(bullet, team_dir_path, bullet_count)
        txt_file.write(bullet['number'] + " " + bullet['name'] + " - " + bullet['text'] + "\n")
    txt_file.close()

def generate_team_xml_bullet(logo, name, text1, text2, bullet_count, team_path):
    bullet_name = "STRAP - " + logo + " " + name.upper()
    xmlns_uris = {
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xmlns:xsd': 'http://www.w3.org/2001/XMLSchema',
        'Name': bullet_name,
        'Color': "#00FF40",
        'SignId': "11"
    }
    snapshot = ET.Element("SnapShot")
    # Här kommer "huvuddelen"
    cache = ET.SubElement(snapshot, "Cache")
    #   Lagnamn
    fval10 = ET.SubElement(cache, "Fval", Field="10")
    value10 = ET.SubElement(fval10, "Value").text = name
    #   Text/info
    fval100 = ET.SubElement(cache, "Fval", Field="100")
    table100 = ET.SubElement(fval100, "Table", Reverse="false")
    table100_2 = ET.SubElement(table100, "Table")
    tablerow = ET.SubElement(table100_2, "TableRow", RowNr="1")
    tablerow_row = ET.SubElement(tablerow, "Row")
    tablecell_1 = ET.SubElement(tablerow_row, "TableCell", Name="1")
    tablecell_1_value = ET.SubElement(tablecell_1, "Value").text = text1
    #   OBS - Text/info-fält nummer 2
    tablecell_2 = ET.SubElement(tablerow_row, "TableCell", Name="2")
    tablecell_2_value = ET.SubElement(tablecell_2, "Value").text = text2
    #   Laglogga
    fval11 = ET.SubElement(cache, "Fval", Field="11")
    value11 = ET.SubElement(fval11, "Value").text = logo
    #   Vet ej
    fval99 = ET.SubElement(cache, "Fval", Field="99")
    value99 = ET.SubElement(fval99, "Value").text = "1"
    #   Resten av filen
    siselect = ET.SubElement(snapshot, "SiSelect xsi:nil='true'")
    highlightqueue = ET.SubElement(snapshot, "HighlightQueue")
    groups = ET.SubElement(highlightqueue, "Groups")
    hiddenfields = ET.SubElement(snapshot, "HiddenFields", Fields="12;13;200;300;400")
    infoformatstring = ET.SubElement(snapshot, "InfoFormatString").text = '{0};10'
    # Dags att skjuta ut xml-filen!
    tree = ET.ElementTree(snapshot)
    filename = logo + "_bullet" + str(bullet_count) + ".xml"
    add_XMLNS_attributes(snapshot, xmlns_uris)
    tree.write(team_path + filename, xml_declaration=True, encoding="utf-16", method="xml")

def generate_team_bullets(filepath, home, away):
    date = datetime.today().strftime('%Y-%m-%d')
    new_dir_path = os.path.dirname(os.path.realpath(__file__)) + "/bullets/bullets_" + date + "_" + home + "-" + away + "/"
    with open(filepath, 'r') as file:
        filereader = csv.reader(file, delimiter=',')
        bullet_count = 0
        for row in filereader:
            bullet_count += 1
            generate_team_xml_bullet(row[0], row[1], row[2], row[3], bullet_count, new_dir_path)

def print_menu():
    print('Hello! What do you want to do?')
    print('1. Get team bullets for a game')
    print('2. Create bullets from a csv file')
    print('')

def team_game_bullets(home, away):
    team_urls = get_team_urls()
    date = datetime.today().strftime('%Y-%m-%d')
    home_url = get_roster_url(team_urls[home])
    away_url = get_roster_url(team_urls[away])
    print("Getting " + home + " player gamelogs...")
    home_players = get_player_stats(home_url)
    print("Got player gamelogs!")
    print("Getting " + away + " player gamelogs...")
    away_players = get_player_stats(away_url)
    print("Got player gamelogs!")
    new_dir_path = os.path.dirname(os.path.realpath(__file__)) + "/bullets/bullets_" + date + "_" + home + "-" + away + "/"
    os.makedirs(os.path.dirname(new_dir_path), exist_ok=True)
    generate_player_bullets(home_players, home, away, new_dir_path)
    generate_player_bullets(away_players, away, home, new_dir_path)
    print("Done!")

def bullets_from_file(home, away):
    filepath = input("Path to file: ")
    generate_team_bullets(filepath, home, away)

def main():
    print('Team names: LHF, ÖRE, FBK, FHC, RBK, SKE, DIF, HV71, MIF, VLH, BIF, LHC, LIF, IKO')
    home = input('Please choose home team: ').upper()
    away = input('Please choose away team: ').upper()
    print_menu()
    menu_choice = input('Choice: ')
    if (menu_choice == "1"):
        team_game_bullets(home, away)
    elif (menu_choice == "2"):
        bullets_from_file(home, away)

if __name__ == '__main__':
    main()