import os
import json
from datetime import datetime

def calculate_probability(rating1, rating2):
    return 1 / (1 + 10**((rating2 - rating1) / 400))

def update_ratings(rating1, rating2, k_factor, k_factor_loser, result):
    p = calculate_probability(rating1, rating2)
    rating1_new = rating1 + k_factor * (result - p)
    rating2_new = rating2 + k_factor_loser * ((1 - result) - (1 - p))
    return rating1_new, rating2_new

def extract_year_from_date(date):
    return datetime.strptime(date, "%Y-%m-%d").year

def changed_team_names(team, old_names, new_names):
    for old, new in zip(old_names, new_names):
        if team!=None:
            team = team.replace(old, new)
    return team

def extract_match_info(json_data):
    event_info = json_data['info']['event']
    stage = event_info.get('stage', 'Unknown')
    team1 = json_data['info']['teams'][0]
    team2 = json_data['info']['teams'][1]

    old_names = ['Daredevils', 'Bangalore', 'Supergiants']
    new_names = ['Capitals', 'Bengaluru', 'Supergiant']

    team1 = changed_team_names(team1, old_names, new_names)
    team2 = changed_team_names(team2, old_names, new_names)

    winner = json_data['info']['outcome'].get('winner', None)
    winner = changed_team_names(winner, old_names, new_names)

    # Have to handle 'Kings XI Punjab' manually
    # Replace Kings XI Punjab with Punjab Kings [cannot use the change_team_names function here]
    if team1 == 'Kings XI Punjab':
        team1 = 'Punjab Kings'
    if team2 == 'Kings XI Punjab':
        team2 = 'Punjab Kings'
    if winner == 'Kings XI Punjab':
        winner = 'Punjab Kings'


    match_info = (
        team1,
        team2,
        json_data['info']['dates'][0],
        winner,
        stage
    )
    return match_info

def scrape_match_records(folder_path):
    match_records = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)

            with open(file_path, 'r') as file:
                match_data = json.load(file)
                match_info = extract_match_info(match_data)
                match_records.append(match_info)

    sorted_records = sorted(match_records, key=lambda x: extract_year_from_date(x[2]))
    numbered_records = [(index + 1,) + record[0:] for index, record in enumerate(sorted_records)]

    return numbered_records

def scrape_to_file():
    folder_path = "ipl_json/"
    all_match_records = scrape_match_records(folder_path)
    with open('matches.txt', 'w') as file:
        for record in all_match_records:
            file.write(f"{record}\n")

def main():
    scrape_to_file()
    
    all_match_records = []
    
    with open('matches.txt', 'r') as file:
        for line in file:
            match_record = eval(line)
            all_match_records.append(match_record)


    team_elo_ratings = {team: 1600 for team in set(record[1] for record in all_match_records)}
    elo_history = {team: [] for team in team_elo_ratings}
    peak_elo_ratings = {team: 1600 for team in team_elo_ratings}
    k_factor_regular = 32
    k_factor_playoffs = k_factor_regular * 1.5
    k_factor_finals = k_factor_regular * 2

    db = {
        "Chennai Super Kings": [],
        "Delhi Capitals": [],
        "Kolkata Knight Riders": [],
        "Mumbai Indians": [],
        "Punjab Kings": [],
        "Rajasthan Royals": [],
        "Royal Challengers Bengaluru": [],
        "Sunrisers Hyderabad": [],
        "Deccan Chargers": [],
        "Gujarat Lions": [],
        "Kochi Tuskers Kerala": [],
        "Pune Warriors": [],
        "Rising Pune Supergiant": [],
        "Gujarat Titans": [],
        "Lucknow Super Giants": [],
    }

    for record in all_match_records:
        match_index, team1, team2, date, winner, stage = record

        team_elo_ratings.setdefault(team1, 1600)
        team_elo_ratings.setdefault(team2, 1600)

        if winner:
            winner_elo = team_elo_ratings[team1] if winner == team1 else team_elo_ratings[team2]
            loser = team2 if winner == team1 else team1
            loser_elo = team_elo_ratings[loser]

            print(stage)

            k_factor_winner = k_factor_regular
            k_factor_loser = k_factor_regular

            if stage == 'Final':
                k_factor_winner = k_factor_finals
                k_factor_loser = k_factor_playoffs
            
            elif stage == 'Qualifier 1' or stage == 'Qualifier 2' or stage == 'Eliminator':
                k_factor_winner = k_factor_playoffs
                k_factor_loser = k_factor_playoffs
                
            

            team_elo_ratings[winner], team_elo_ratings[loser] = update_ratings(
                winner_elo, loser_elo, k_factor_winner, k_factor_loser, 1
            )

            year = extract_year_from_date(date)
            elo_history[team1].append((year, team_elo_ratings[team1]))
            elo_history[team2].append((year, team_elo_ratings[team2]))

            team1db = [date, team_elo_ratings[team1]]
            team2db = [date, team_elo_ratings[team2]]

            db[team1].append(team1db)
            db[team2].append(team2db)

    #print("\nPeak Elo Ratings for Each Team:")
    peak = []
    for team in elo_history:
        peak_elo, peak_elo_date = max((elo, date) for date, elo in elo_history[team])
        res = team, peak_elo, peak_elo_date
        peak.append(res)
    # Sort the teams by their peak Elo rating
        
    print("\nPeak Elo Ratings for Each Team:")
    peak.sort(key=lambda x: x[1], reverse=True)
    for team, peak_elo, peak_elo_date in peak:
        print(f"{team}: {peak_elo:.2f} in {peak_elo_date}")

        
    elo_data = db['Royal Challengers Bengaluru']

    matches_by_year = {}

    # Iterate through elo_data and organize matches by year
    for date, elo in elo_data:
        year = date.split('-')[0]
        if year not in matches_by_year:
            matches_by_year[year] = []
    
        matches_by_year[year].append({'date': date, 'elo': elo})
    
    # Sort matches within each year by date
    for year, matches in matches_by_year.items():
        matches_by_year[year] = sorted(matches, key=lambda x: x['date'])
    
    # Print the organized data
    for year, matches in matches_by_year.items():
        print(f"\nYear {year}:")
        for index, match in enumerate(matches, start=1):
            print(f"Match {index}: Date {match['date']}, Elo {match['elo']:.2f}")
            

    # Elo at the end of each year
            
    print("\nElo at the end of each year:")
    
    for year in range(2008, 2025):
        print(f"\nYear {year}:")
        teams = []

        for i in range(len(db)):
            team = list(db.keys())[i]
            teams.append(team)

        data = []

        for team in teams:
            elo_data = db[team]

            n = 0

            for i in range(len(elo_data)):
                if elo_data[i][0].split('-')[0] == str(year):
                    n += 1
                    try:
                        if elo_data[i+1][0].split('-')[0] != str(year):
                            data.append((team, elo_data[i][1], elo_data[i][0]))
                    except:
                        data.append((team, elo_data[i][1], elo_data[i][0]))

            #if n == 0:
            #    data.append((team, elo_data[-1][1], elo_data[-1][0]))

        data.sort(key=lambda x: x[1], reverse=True)

        for team, elo, date in data:
            print(f"{team}: {elo:.2f}")

    # Current Elo Ratings
    print("\nCurrent Elo Ratings:")

    data = []

    for team in teams:
        elo_data = db[team]
        data.append((team, elo_data[-1][1]))

    data.sort(key=lambda x: x[1], reverse=True)

    for team, elo in data:
        print(f"{team}: {elo:.2f}")

            
        
    with open('../website/cricket-rankings/app/ipl/ipl_ratings.ts', 'w') as file:
        file.write("export const iplRatings = [\n")
        for team, elo in data:
            if team in ['Kochi Tuskers Kerala', 'Pune Warriors', 'Rising Pune Supergiant', 'Gujarat Lions', 'Deccan Chargers']:
                continue
            file.write(f"\t{{team: '{team}', elo: {elo:.2f}}},\n")
        file.write("];\n")

if __name__ == "__main__":
    main()
