import os
import json
from datetime import datetime

cities = set()
countries = set()

country_city_mapping = {
    'United Arab Emirates': ['Abu Dhabi', 'Dubai'],
    'Sri Lanka': ['Colombo', 'Kandy', 'Dambulla', 'Galle', 'Hambantota', 'Kathmandu'],
    'Papua New Guinea': ['Port Moresby'],
    'South Africa': ['Cape Town', 'Potchefstroom', 'St Kitts', 'Hamilton', 'Benoni', 'Johannesburg', 'Dharmasala', 'Durban', 'Bloemfontein', 'Port Elizabeth', 'Centurion', 'Gqeberha'],
    'Kenya': ['Nairobi'],
    'England': ['Ayr', 'Nottingham', 'Cardiff', 'Leeds', 'Birmingham', 'Southampton', 'London', 'Chester-le-Street', 'Manchester', 'Belfast', 'Taunton', 'Bristol', 'Leeds', 'Chelmsford', 'Edinburgh'],
    'Oman': ['Al Amarat'],
    'Zimbabwe': ['Harare', 'Bulawayo'],
    'Afghanistan': [],
    'United States of America': ['Providence', 'Toronto', 'Lauderhill'],
    'West Indies': ['Dominica', 'Trinidad', 'Gros Islet', 'King City', 'Tarouba', 'Paarl', "St George's", 'St Lucia', 'Chester-le-Street', 'Jamaica', 'Antigua', 'Kingston', 'North Sound', 'Bridgetown', 'Grenada'],
    'Hong Kong': ['Hong Kong'],
    'Jersey': [],
    'New Zealand': ['Nelson', 'Queenstown', 'Whangarei', 'Dunedin', 'Mount Maunganui', 'Lincoln'],
    'Bangladesh': ['Chittagong', 'Mirpur', 'Sylhet', 'Bogra', 'Dhaka', 'Chattogram', 'Fatullah', 'Khulna'],
    'Netherlands': ['Rotterdam', 'Utrecht', 'Deventer', 'Amstelveen'],
    'Scotland': ['Glasgow', 'Aberdeen', 'Edinburgh'],
    'Bermuda': [],
    'Ireland': ['Dublin'],
    'India': ['Vadodara', 'Faridabad', 'Ahmedabad', 'Kolkata', 'Rajkot', 'Dharamsala', 'Kochi', 'Ranchi', 'Guwahati', 'Chandigarh', 'Lucknow', 'Indore', 'Delhi', 'Thiruvananthapuram', 'Jamshedpur', 'Visakhapatnam', 'Greater Noida', 'Cuttack', 'Mumbai', 'Pune', 'Guwahati', 'Jaipur', 'Kolkata'],
    'Australia': ['Perth', 'Adelaide', 'Brisbane', 'Sydney', 'Melbourne', 'Canberra', 'Hobart', 'Townsville', 'Cairns'],
    'Nepal': ['Kirtipur', 'Kathmandu'],
    'Namibia': ['Windhoek'],
    'Canada': ['King City', 'Toronto'],
    'Pakistan': ['Peshawar', 'Faisalabad', 'Lahore', 'Karachi', 'Multan'],
}


def calculate_probability(rating1, rating2):
    return 1 / (1 + 10**((rating2 - rating1) / 400))

def update_ratings(rating1, rating2, k_factor, k_factor_loser, result):
    p = calculate_probability(rating1, rating2)
    rating1_new = rating1 + k_factor * (result - p)
    rating2_new = rating2 + k_factor_loser * ((1 - result) - (1 - p))
    return rating1_new, rating2_new

def extract_year_from_date(date):
    return datetime.strptime(date, "%Y-%m-%d").year

def extract_match_info(json_data):
    #stage = event_info.get('stage', 'Unknown')
    team1 = json_data['info']['teams'][0]
    team2 = json_data['info']['teams'][1]
    if 'XI' in team1 or 'XI' in team2:
        return None
    winner = json_data['info']['outcome'].get('winner', None)
    city = json_data['info'].get('city', 'Unknown')
    cities.add(city)
    countries.add(team1)
    countries.add(team2)

    away = False
    if team1 == winner:
        loser = team2
    else:
        loser = team1

    if winner != None and city not in country_city_mapping[winner] and city in country_city_mapping[loser]:
        away = True

    event = json_data['info'].get('event', {})
    name = event.get('name', 'Unknown')
    
    stage = event.get('stage', 'Unknown')


    match_info = (
        team1,
        team2,
        json_data['info']['dates'][0],
        winner,
        away,
        name,
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
                if match_info == None:
                    continue
                match_records.append(match_info)

    sorted_records = sorted(match_records, key=lambda x: extract_year_from_date(x[2]))
    numbered_records = [(index + 1,) + record[0:] for index, record in enumerate(sorted_records)]

    return numbered_records

def scrape_to_file():
    folder_path = "odis_male_json/"
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

    #print(cities)
    #print(countries)


    test_playing_nations = ['Sri Lanka', 'Pakistan', 'England', 'Australia', 'India', 'West Indies', 'South Africa', 'Zimbabwe', 'New Zealand', 'Bangladesh']

    #default elo 1000 if not test playing nation, 1600 if test playing nation

    team_elo_ratings = {team: 1600 if team in test_playing_nations else 1100 for team in countries}
    elo_history = {team: [] for team in team_elo_ratings}
    peak_elo_ratings = {team: 1600 if team in test_playing_nations else 1100 for team in team_elo_ratings}
    k_factor_regular = 32

    db = {}

    for country in countries:
        db[country] = []

    for record in all_match_records:
        match_index, team1, team2, date, winner, away, name, stage = record


        if winner:
            winner_elo = team_elo_ratings[team1] if winner == team1 else team_elo_ratings[team2]
            loser = team2 if winner == team1 else team1
            loser_elo = team_elo_ratings[loser]

            #print(stage)

            k_factor_winner = k_factor_regular
            k_factor_loser = k_factor_regular

            if away:
                k_factor_winner = k_factor_winner * 1.25
                k_factor_loser = k_factor_loser * 1.25

            if 'ICC World Cup' in name:
                k_factor_winner = k_factor_winner* 2
                k_factor_loser = k_factor_loser * 2
            
            if 'ICC Champions Trophy' in name:
                k_factor_winner = k_factor_winner * 1.5
                k_factor_loser = k_factor_loser * 1.5

            if stage == 'Final':
                k_factor_winner = k_factor_winner * 2
                k_factor_loser = k_factor_loser * 1.5

            if stage == 'Semi Final':
                k_factor_winner = k_factor_winner * 1.5
                k_factor_loser = k_factor_loser * 1.25
            
            if stage == 'Quarter Final':
                k_factor_winner = k_factor_winner * 1.5
                k_factor_loser = k_factor_loser * 1.25

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

    # Sort db[team] by date
    
    for team in db:
        db[team] = sorted(db[team], key=lambda x: x[0])

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

    elo_data = db['Australia']

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
    #for year, matches in matches_by_year.items():
    #    print(f"\nYear {year}:")
    #    for index, match in enumerate(matches, start=1):
    #        print(f"Match {index}: Date {match['date']}, Elo {match['elo']:.2f}")


    # Elo at the end of each year
            
    print("\nElo at the end of each year:")
    
    for year in range(2002, 2025):
        print(f"\nYear {year}:")
        teams = countries

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

    for team in countries:
        elo_data = db[team]
        data.append((team, elo_data[-1][1]))

    data.sort(key=lambda x: x[1], reverse=True)

    for team, elo in data:
        print(f"{team}: {elo:.2f}")

    
if __name__ == "__main__":
    main()