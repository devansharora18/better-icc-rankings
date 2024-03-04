import os
import json
import matplotlib.pyplot as plt
from datetime import datetime

def calculate_probability(rating1, rating2):
    return 1 / (1 + 10**((rating2 - rating1) / 400))

def update_ratings(rating1, rating2, k_factor, result):
    p = calculate_probability(rating1, rating2)
    rating1_new = rating1 + k_factor * (result - p)
    rating2_new = rating2 + k_factor * ((1 - result) - (1 - p))
    return rating1_new, rating2_new

def plot_elo_history_by_team(elo_history, team):
    plt.figure(figsize=(8, 4))
    years, elo_values = zip(*elo_history[team])  # Unzip the years and elo_values
    plt.plot(years, elo_values, label=team, marker='o', linestyle='-')
    plt.title(f'Elo Ratings Over Time for {team}')
    plt.xlabel('Year')
    plt.ylabel('Elo Rating')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def extract_year_from_date(date):
    return datetime.strptime(date, "%Y-%m-%d").year

def extract_match_info(json_data):
    event_info = json_data['info']['event']
    stage = event_info.get('stage', None)
    match_info = (
        json_data['info']['teams'][0],
        json_data['info']['teams'][1],
        json_data['info']['dates'][0],  # Assuming the date is present in the 'dates' list
        json_data['info']['outcome'].get('winner', None),
        stage if stage else "Unknown"
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

    # Sort the match records by date
    sorted_records = sorted(match_records, key=lambda x: x[2])

    # Number the matches based on the sorted order
    numbered_records = [(index + 1,) + record[0:] for index, record in enumerate(sorted_records)]

    return numbered_records

if __name__ == "__main__":
    folder_path = "ipl_json/"  # Replace with the actual path to your folder
    all_match_records = scrape_match_records(folder_path)

    team_elo_ratings = {}  # Dictionary to store Elo ratings for each team
    elo_history = {team: [] for team in team_elo_ratings.keys()}
    peak_elo_ratings = {team: 1400 for team in team_elo_ratings.keys()}  # Initialize with default peak rating
    k_factor_regular = 16  # Initial K-factor for regular matches
    k_factor_knockout = k_factor_regular * 2  # Adjusted K-factor for knockout matches

    for record in all_match_records:
        match_index, team1, team2, date, winner, stage = record
    
        team_elo_ratings.setdefault(team1, 1400 if team1 == 'Gujarat Titans' or team1 == 'Lucknow Super Giants' else 1400)
        team_elo_ratings.setdefault(team2, 1400 if team2 == 'Gujarat Titans' or team2 == 'Lucknow Super Giants' else 1400)
    
        if team1 not in elo_history:
            elo_history[team1] = []
        if team2 not in elo_history:
            elo_history[team2] = []
    
        if winner is not None:
            winner_elo = team_elo_ratings[team1] if winner == team1 else team_elo_ratings[team2]
            loser = team2 if winner == team1 else team1
            loser_elo = team_elo_ratings[loser]
    
            k_factor_winner = k_factor_knockout if stage.lower() in ['qualifier 1', 'eliminator', 'qualifier 2', 'final'] else k_factor_regular
            k_factor_loser = k_factor_knockout if stage.lower() in ['qualifier 1', 'eliminator', 'qualifier 2', 'final'] else k_factor_regular
    
            team_elo_ratings[winner], team_elo_ratings[loser] = update_ratings(
                winner_elo, loser_elo, k_factor_winner, 1
            )
    
            # Update elo_history for each team
            year = extract_year_from_date(date)
            elo_history[team1].append((year, team_elo_ratings[team1]))
            elo_history[team2].append((year, team_elo_ratings[team2]))
    
            # Update peak_elo_ratings for each team
            if team1 in peak_elo_ratings:
                peak_elo_ratings[team1] = max(peak_elo_ratings[team1], team_elo_ratings[team1])
                print(f"Updated peak_elo_ratings for {team1}: {peak_elo_ratings[team1]}")
            if team2 in peak_elo_ratings:
                peak_elo_ratings[team2] = max(peak_elo_ratings[team2], team_elo_ratings[team2])
                print(f"Updated peak_elo_ratings for {team2}: {peak_elo_ratings[team2]}")

    # Print Peak Elo ratings for each team
    print("\nPeak Elo Ratings:")
    for team, peak_elo in peak_elo_ratings.items():
        print(f"{team}: {peak_elo:.2f}")

    # Print Elo ratings for each team after every year
    print("\nTeam Elo Ratings After Each Year:")
    for year in sorted(set(year for team_history in elo_history.values() for year, _ in team_history)):
        print(f"\nYear {year}:")
        for team, history in elo_history.items():
            ratings_for_year = [elo for elo_year, elo in history if elo_year <= year]
            if ratings_for_year:
                print(f"{team}: {ratings_for_year[-1]:.2f}")

    # Plot Elo ratings over time for each team
    team_to_check = 'Mumbai Indians'
    if team_to_check in elo_history:
        plot_elo_history_by_team(elo_history, team_to_check)
    else:
        print(f"No data available for {team_to_check}")