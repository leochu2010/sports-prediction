import csv
import sys

csv_files={
    "whoscored_1006164_1080000.csv",
    "whoscored_1080000_1085239.csv",
    "whoscored_718800_722600.csv",
    "whoscored_718800_722600_fix.csv",
    "whoscored_828500_831500.csv",
    "whoscored_957500_962000.csv",
    "whoscored.csv"
    }

with open('whoscored_all.csv', 'a') as outfile:
    # output dict needs a list for new column ordering
    fieldnames = [
        'tournament_name',
        'tournament_link',
        'country',
        'match_link',
        'match_report_link',
        'date', 
        'kick_off',
        'home_team_name',
        'away_team_name',
        'full_time',
        'half_time' ,
        'home_team_link',
        'away_team_link',
        'home_shots',
        'home_shots_on_target',
        'home_possession',
        'home_pass_success',
        'home_tackles', 
        'home_aerial_duel_success',
        'home_dribbles_won',
        'away_shots',
        'away_shots_on_target',
        'away_possession',
        'away_pass_success',
        'away_tackles',
        'away_aerial_duel_success',
        'away_dribbles_won'
        ]    
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    # reorder the header first
    writer.writeheader()
    
    for csv_file in csv_files:
        with open(csv_file, 'r') as infile:
            for row in csv.DictReader(infile):
                # writes the reordered rows to the new file
                writer.writerow(row)

