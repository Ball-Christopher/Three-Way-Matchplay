"""
Author: Christopher Ball
Create Date: 29/01/2016

Purpose: To control the three-way league running
at North City Tenpin.

TODO:
3) Base64 encode pin position and pdf through webkit, see
http://stackoverflow.com/questions/24846171/how-to-convert-an-html-document-containing-an-svg-to-a-pdf-file-in-python
http://metaskills.net/2011/03/20/pdfkit-overview-and-advanced-usage/
4) Automate the league scoring, no more week variable and cut/paste.
5) Clean up the console printed output, including pdfkit output if possible.
"""
from BowlerTeamsTest import *
from Database import *
from Utilities import HTMLStatistics, Score_Week_Pin_Position

# Declare league object
New_League = League(n=24)
# Add league data
New_League.LeagueData(weeklen=11, lanes=16, base=220, sdate='20/07/2016',
                      Lname = 'North City Singles', BCenter = 'North City Tenpin')
# Create a league schedule
Schedule = [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
            [7, 18, 24, 1, 16, 9, 5, 19, 2, 8, 3, 22, 6, 11, 21, 4, 13, 12, 17, 23, 14, 10, 15, 20],
            [19, 6, 15, 23, 18, 3, 1, 14, 24, 2, 13, 21, 10, 17, 9, 16, 20, 7, 5, 8, 12, 4, 22, 11],
            [4, 23, 9, 17, 11, 1, 19, 16, 12, 18, 14, 20, 15, 8, 21, 10, 3, 24, 6, 2, 22, 5, 7, 13],
            [19, 1, 8, 2, 15, 7, 5, 18, 9, 23, 13, 10, 6, 17, 12, 22, 16, 21, 4, 20, 24, 14, 3, 11],
            [6, 10, 16, 19, 14, 9, 15, 22, 1, 5, 11, 24, 18, 8, 4, 3, 20, 13, 7, 17, 21, 2, 23, 12],
            [19, 13, 24, 20, 11, 8, 14, 16, 5, 2, 4, 17, 6, 3, 9, 1, 23, 21, 15, 18, 12, 22, 7, 10],
            [10, 18, 21, 3, 17, 19, 2, 20, 9, 6, 8, 24, 11, 13, 16, 22, 14, 12, 7, 1, 4, 15, 5, 23],
            [7, 3, 12, 1, 10, 5, 22, 19, 18, 15, 11, 9, 20, 23, 6, 13, 8, 17, 2, 16, 24, 4, 14, 21],
            [10, 4, 19, 7, 6, 14, 1, 20, 12, 8, 16, 23, 22, 13, 9, 11, 18, 2, 5, 3, 21, 15, 17, 24],
            [1, 6, 13, 18, 2, 14, 8, 10, 3, 16, 15, 4, 5, 17, 22, 20, 7, 11, 19, 23, 9, 24, 21, 12]]

New_League.Pattern = [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4]

for week in range(1, 40): New_League.SetTotals(week, ISerW = 6, ISerD = 3)
# Add schedule to league
New_League.AddSchedule(Schedule)

# Create and add bowlers to league
Names = ['Chris Haynes', 'Andy Smith', 'Susan Munro', 'Roger Tucker', 'Chris Ball',
         'Hamish McGrigor', 'Mike Gibbs', 'Leonard Reeves', 'Ash Ball', 'Kevin Foubister',
         'Kelly Wilson', 'David Brierley', 'Alan Griffin', 'Shane Forde', 'Luke',
         'Shane Devine', 'Stephanie George', 'Dyanni Ross',
         'Devan Sahayam', 'Clare Sahayam', 'Alysha Carr-Brooks',  # Post-bowlers
         'Danual Paton', 'Dayna Haylock', 'Phil Turner']
DispNames = ['Chris H', 'Andy', 'Susan', 'Roger', 'Chris B', 'Hamish', 'Gibby', 'Lenny',
             'Ash', 'Kevin', 'Kelly', 'David', 'Alan', 'Shane F', 'Luke',
             'Shane D', 'Steph', 'Dyanni',
             'Devan', 'Clare', 'Alysha',
             'Danual', 'Dayna', 'Phil']
Female = [False, False, True, False, False,
          False, False, False, False, False,
          True, False, False, False, False,
          False, True, True,
          False, True, True,
          False, True, False]
for DName, Name, F in zip([N.lower() for N in DispNames], Names, Female):
    New_League.AddNewBowler(Name, DName, Female=F)

DB = Database()
Map = {i.upper(): j for i, j in zip(DispNames, Names)}
Exclude = ['VACANT', 'vacant', 'Player', 'BYE', 'Vacant']
DB.ImportFile(r'C:\Users\Chris\Documents\League\Three Way\Source\Week_1.xls', Map)
DB.ImportFile(r'C:\Users\Chris\Documents\League\Three Way\Source\Week_1_Prebowl.xls', Map,
              NewDate=(2016, 7, 20))
DB.ImportFile(r'C:\Users\Chris\Documents\League\Three Way\Source\Week_1_Extra.xls', Map,
              NewDate=(2016, 7, 20))
DB.ImportFile(r'C:\Users\Chris\Documents\League\Three Way\Source\Week_1_Extra_2.xls', Map,
              NewDate=(2016, 7, 20))
DB.ImportFile(r'C:\Users\Chris\Documents\League\Three Way\Source\Week_1_Postbowl_1.xls', Map,
              NewDate=(2016, 7, 20))

# Fix for week 1, Hamish's games are the last 6 of Sue's...
DB.Players.append(Player('Hamish McGrigor'))
DB.Players[-1].Games = [DB.Players[10].Games[6:][i] for i in [5, 0, 1, 2, 3, 4]]
DB.Players[10].Games = DB.Players[10].Games[:6]

DB.LaneInfo()

# Add scores for week 1
Week = 1
Score_Week_Pin_Position(DB, New_League, Week, Vacant=('Danual', 'Phil'))

Week = 2

# Backdate handicaps
'''
for Member in New_League.League:
    Member.hcps[1] = Member.hcps[2]
    Member.hseries[1] = [G + Member.hcps[1] for G in Member.series[1]]
    Member.hseries[2] = [G + Member.hcps[2] for G in Member.series[2]]
'''

# Calculate Weekly Scores
# New_League.CalculateWeeklyPoints(1)

# Print HTML report for the week...
# New_League.LaTeXWeekly(1)

# Calculate Weekly Scores
#New_League.CalculateWeeklyPoints(2)

# Print HTML report for the week...
#New_League.LaTeXWeekly(2)

# Print the schedule
New_League.CompleteSchedule()

HTMLStatistics(DB, New_League)
