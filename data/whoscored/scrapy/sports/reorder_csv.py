import csv
import sys

csv_file=sys.argv[1]

with open(csv_file, 'r') as infile, open('reordered/'+csv_file, 'a') as outfile:
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
    for row in csv.DictReader(infile):
        # writes the reordered rows to the new file
        writer.writerow(row)




