import os
import json
from datetime import datetime

from country_city_mapping import country_city_mapping


class elo_methods:
    def __init__(self):        
        self.cities = set()
        self.countries = set()
    
    def calculate_probability(self, rating1, rating2):
        return 1 / (1 + 10**((rating2 - rating1) / 400))


    
    def update_ratings(self, rating1, rating2, k_factor, k_factor_loser, result):
        p = self.calculate_probability(rating1, rating2)  # Probability that team1 wins
        
        # New ratings for team1 and team2 after the match
        rating1_new = rating1 + k_factor * (result - p)
        rating2_new = rating2 + k_factor_loser * ((1 - result) - (1 - p))
        return rating1_new, rating2_new

    def extract_year_from_date(self, date):
        return datetime.strptime(date, "%Y-%m-%d").year
    
    def changed_team_names(self, team, old_names, new_names):
        for old, new in zip(old_names, new_names):
            if team!=None:
                team = team.replace(old, new)
        return team

    # Method to extract key match information from the JSON file and format
    def extract_match_info(self, json_data, format):
        team1 = json_data['info']['teams'][0]  # First team
        team2 = json_data['info']['teams'][1]  # Second team
        # If one of the teams is a World "XI" team, we skip processing the match
        if 'XI' in team1 or 'XI' in team2:
            return None
        
        winner = json_data['info']['outcome'].get('winner', None)  # Match winner, if available
        city = json_data['info'].get('city', 'Unknown')  # Match city
        
        # Add city and countries to sets for future reference
        self.cities.add(city)
        self.countries.add(team1)
        self.countries.add(team2)

        event = json_data['info'].get('event', {})  # Match event details
        name = event.get('name', 'Unknown')  # Event name
        stage = event.get('stage', 'Unknown')  # Event stage

        # Tuple with match information (team1, team2, date, winner)
        match_info = (
            team1,
            team2,
            json_data['info']['dates'][0],
            winner,
        )

        # Additional processing for non-T20 formats (like Test and ODI)
        if 't20' not in format and 'ipl' not in format:
            away = False  # Flag to track if the match is an away match for the winner

            if team1 == winner:
                loser = team2
            else:
                loser = team1

            # If the winner's city doesn't match and the loser's city does, mark it as an away game
            if winner != None and city not in country_city_mapping[winner] and city in country_city_mapping[loser]:
                away = True
        
            match_info = match_info + (away,)  # Append away status to match info

        match_info = match_info + (name, )  # Append event name

        # For non-Test formats, append the event stage
        if 'test' not in format:
            match_info = match_info + (stage, )

        if 'ipl' in format:
            old_names = ['Daredevils', 'Bangalore', 'Supergiants']
            new_names = ['Capitals', 'Bengaluru', 'Supergiant']

            team1 = self.changed_team_names(team1, old_names, new_names)
            team2 = self.changed_team_names(team2, old_names, new_names)

            winner = json_data['info']['outcome'].get('winner', None)
            winner = self.changed_team_names(winner, old_names, new_names)

            # Have to handle 'Kings XI Punjab' manually
            # Replace Kings XI Punjab with Punjab Kings [cannot use the change_team_names function here]
            if team1 == 'Kings XI Punjab':
                team1 = 'Punjab Kings'
            if team2 == 'Kings XI Punjab':
                team2 = 'Punjab Kings'
            if winner == 'Kings XI Punjab':
                winner = 'Punjab Kings'

            match_info = (team1, team2, json_data['info']['dates'][0], winner, stage)

        return match_info

    # Method to scrape match records from a folder of JSON files
    def scrape_match_records(self, folder_path, format):
        match_records = []

        # Loop through each file in the specified folder
        for filename in os.listdir(folder_path):
            # Skip a specific file based on the format
            if filename == '221840.json' and format == 'test':
                continue
            elif filename.endswith(".json"):  # Process only JSON files
                file_path = os.path.join(folder_path, filename)
    
                # Load the JSON data from the file
                with open(file_path, 'r') as file:
                    match_data = json.load(file)
                    # Extract match info using the helper method
                    match_info = self.extract_match_info(match_data, format)
                    if match_info == None:  # Skip if match info is None
                        continue
                    match_records.append(match_info)

        # Sort records by match date
        sorted_records = sorted(match_records, key=lambda x: self.extract_year_from_date(x[2]))
        # Add match numbering
        numbered_records = [(index + 1,) + record[0:] for index, record in enumerate(sorted_records)]

        return numbered_records

    # Method to scrape data from a folder and write it to a text file
    def scrape_to_file(self, folder_name):
        folder_path = folder_name
        format = ''
        # Determine format based on the folder name
        if 'test' in folder_name:
            format = 'test'
        if 't20' in folder_name:
            format = 't20'
        if 'odi' in folder_name:
            format = 'odi'
        if 'ipl' in folder_name:
            format = 'ipl'
        
        # Scrape match records and write to a file
        all_match_records = self.scrape_match_records(folder_path, format)
        with open('matches.txt', 'w') as file:
            for record in all_match_records:
                file.write(f"{record}\n")
