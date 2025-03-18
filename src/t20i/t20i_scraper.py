import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import elo_methods

def main():
    elo_m = elo_methods.elo_methods()
    elo_m.scrape_to_file('t20i/t20s_male_json/')
    
    all_match_records = []
    
    with open('t20i/matches.txt', 'r') as file:
        for line in file:
            match_record = eval(line)
            all_match_records.append(match_record)
    
    test_playing_nations = ['Sri Lanka', 'Pakistan', 'England', 'Australia', 'India', 'West Indies', 'South Africa', 'Zimbabwe', 'New Zealand', 'Bangladesh']

    # default elo 1000 if not test playing nation, 1600 if test playing nation

    team_elo_ratings = {team: 1600 if team in test_playing_nations else 1100 for team in elo_m.countries}
    elo_history = {team: [] for team in team_elo_ratings}
    k_factor_regular = 32


    for record in all_match_records:
        match_index, team1, team2, date, winner, name, stage = record


        if winner:
            winner_elo = team_elo_ratings[team1] if winner == team1 else team_elo_ratings[team2]
            loser = team2 if winner == team1 else team1
            loser_elo = team_elo_ratings[loser]

            #print(stage)

            k_factor_winner = k_factor_regular
            k_factor_loser = k_factor_regular


            if name in ['ICC Men\'s T20 World Cup', 'World T20', 'ICC World Twenty20']:
                k_factor_winner = k_factor_winner * 2
                k_factor_loser = k_factor_loser * 2
            
            if stage == 'Final':
                k_factor_winner = k_factor_winner * 2
                k_factor_loser = k_factor_loser * 1.5

            if stage == 'Semi Final':
                k_factor_winner = k_factor_winner * 1.5
                k_factor_loser = k_factor_loser * 1.25
            
            if stage == 'Quarter Final':
                k_factor_winner = k_factor_winner * 1.5
                k_factor_loser = k_factor_loser * 1.25

            team_elo_ratings[winner], team_elo_ratings[loser] = elo_m.update_ratings(
                winner_elo, loser_elo, k_factor_winner, k_factor_loser, 1
            )

            year = elo_m.extract_year_from_date(date)
            elo_history[team1].append((year, team_elo_ratings[team1]))
            elo_history[team2].append((year, team_elo_ratings[team2]))


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


    # Elo at the end of each year
            
    print("\nElo at the end of each year:")
    
    for year in range(2002, 2025):
        print(f"\nYear {year}:")
        teams = elo_m.countries

        data = []

        for team in teams:
            elo_data = elo_history[team]

            for i in range(len(elo_data)):
                if elo_data[i][0] == year:

                    try:
                        if elo_data[i+1][0] != year:
                            data.append((team, elo_data[i][1], elo_data[i][0]))
                    except:
                        data.append((team, elo_data[i][1], elo_data[i][0]))

        data.sort(key=lambda x: x[1], reverse=True)

        for team, elo, date in data:
            print(f"{team}: {elo:.2f}")

    # Current Elo Ratings
    print("\nCurrent Elo Ratings:")

    data = []

    for team in elo_m.countries:
        elo_data = elo_history[team]
        data.append((team, elo_data[-1][1]))

    data.sort(key=lambda x: x[1], reverse=True)

    for team, elo in data:
        print(f"{team}: {elo:.2f}")
        
    # Write the data to a ts list in a file
    
    with open('../website/cricket-rankings/app/t20i/t20i_ratings.ts', 'w') as file:
        file.write("export const t20iRatings = [\n")
        for team, elo in data:
            file.write(f"\t{{team: '{team}', elo: {elo:.2f}}},\n")
        file.write("];\n")
    
if __name__ == "__main__":
    main()