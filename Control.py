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

League_Number = 27
# Declare league object
New_League = League(n=League_Number)
# Add league data
New_League.LeagueData(weeklen=13, lanes=2 * (League_Number // 3), base=220, sdate='20/07/2016',
                      Lname = 'North City Singles', BCenter = 'North City Tenpin')
# Create a league schedule
Schedule_24 = [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
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

Schedule_27 = [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27],
               [4, 23, 27, 19, 12, 26, 22, 2, 6, 1, 14, 21, 8, 11, 17, 9, 24, 3, 7, 10, 16, 5, 15, 25, 13, 20, 18],
               [5, 8, 14, 22, 11, 18, 19, 23, 3, 2, 12, 25, 1, 20, 27, 4, 7, 13, 6, 21, 24, 16, 9, 26, 10, 17, 15],
               [11, 21, 25, 10, 5, 27, 1, 18, 26, 7, 20, 3, 4, 8, 12, 15, 6, 9, 14, 17, 23, 19, 2, 24, 13, 16, 22],
               [7, 24, 26, 17, 3, 25, 16, 11, 27, 13, 2, 9, 10, 14, 18, 19, 22, 4, 21, 12, 15, 20, 23, 5, 1, 8, 6],
               [19, 8, 15, 16, 20, 24, 23, 9, 25, 22, 17, 27, 13, 6, 26, 3, 18, 21, 2, 5, 11, 1, 4, 10, 7, 14, 12],
               [7, 2, 27, 22, 15, 26, 4, 17, 24, 1, 5, 9, 8, 18, 25, 11, 14, 20, 10, 13, 19, 12, 3, 6, 16, 23, 21],
               [14, 24, 25, 13, 8, 27, 7, 11, 15, 10, 23, 6, 4, 21, 26, 16, 19, 1, 18, 9, 12, 17, 20, 2, 22, 5, 3],
               [13, 17, 21, 20, 6, 25, 10, 3, 26, 19, 14, 27, 16, 5, 12, 23, 2, 8, 22, 1, 7, 24, 15, 18, 4, 11, 9],
               [10, 20, 9, 4, 2, 18, 1, 17, 12, 22, 8, 21, 15, 3, 27, 16, 14, 6, 11, 23, 26, 19, 7, 25, 13, 5, 24],
               [16, 4, 25, 22, 14, 9, 19, 5, 18, 13, 11, 3, 10, 2, 21, 8, 20, 26, 12, 24, 27, 1, 23, 15, 7, 17, 6],
               [19, 11, 6, 16, 2, 15, 10, 8, 24, 5, 17, 26, 4, 14, 3, 7, 23, 18, 13, 1, 25, 9, 21, 27, 22, 20, 12],
               [13, 23, 12, 7, 5, 21, 4, 20, 15, 1, 11, 24, 19, 17, 9, 10, 22, 25, 6, 18, 27, 2, 14, 26, 16, 8, 3]]

if League_Number == 24:
    New_League.Pattern = [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4]
else:
    New_League.Pattern = [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]

for week in range(1, 40): New_League.SetTotals(week, ISerW = 6, ISerD = 3)
# Add schedule to league
New_League.AddSchedule(Schedule_27 if League_Number == 27 else Schedule_24)

# Create and add bowlers to league
Names = ['Chris Haynes', 'Andy Smith', 'Susan Munro', 'Roger Tucker', 'Chris Ball',
         'Hamish McGrigor', 'Mike Gibbs', 'Leonard Reeves', 'Ash Ball', 'Kevin Foubister',
         'Kelly Wilson', 'David Brierley', 'Alan Griffin', 'Shane Forde', 'Luke Clark-Grayling',
         'Shane Devine', 'Stephanie George', 'Dyanni Ross',
         'Devan Sahayam', 'Clare Sahayam', 'Alysha Carr-Brooks',  # Post-bowlers
         'Danual Paton', 'Dayna Haylock', 'Phil Turner', 'Ian Jenkins', 'Vacant 1', 'Vacant 2']
DispNames = ['Chris H', 'Andy', 'Susan', 'Roger', 'Chris B',
             'Hamish', 'Gibby', 'Lenny', 'Ash', 'Kevin',
             'Kelly', 'David', 'Alan', 'Shane F', 'Luke',
             'Shane D', 'Steph', 'Dyanni',
             'Devan', 'Clare', 'Alysha',
             'Danual', 'Dayna', 'Phil', 'Ian', 'Vacant 1', 'Vacant 2']
Female = [False, False, True, False, False,
          False, False, False, False, False,
          True, False, False, False, False,
          False, True, True,
          False, True, True,
          False, True, False, False, False, False]
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
DB.ImportFile(r'C:\Users\Chris\Documents\League\Three Way\Source\Week_1_Postbowl_2.xls', Map,
              NewDate=(2016, 7, 20))

# Fix for week 1, Hamish's games are the last 6 of Sue's...
DB.Players.append(Player('Hamish McGrigor'))
DB.Players[-1].Games = [DB.Players[10].Games[6:][i] for i in [5, 0, 1, 2, 3, 4]]
DB.Players[10].Games = DB.Players[10].Games[:6]

DB.ImportFile(r'C:\Users\Chris\Documents\League\Three Way\Source\Week_2.xls', Map)
DB.ImportFile(r'C:\Users\Chris\Documents\League\Three Way\Source\Week_2_Postbowl_1.xls', Map,
              NewDate=(2016, 7, 27))
DB.ImportFile(r'C:\Users\Chris\Documents\League\Three Way\Source\Week_2_Postbowl_2.xls', Map,
              NewDate=(2016, 7, 27))

DB.ImportFile(r'C:\Users\Chris\Documents\League\Three Way\Source\Week_3.xls', Map)
DB.ImportFile(r'C:\Users\Chris\Documents\League\Three Way\Source\Week_3_Prebowl.xls', Map,
              NewDate=(2016, 8, 3))

DB.ImportFile(r'C:\Users\Chris\Documents\League\Three Way\Source\Week_4.xls', Map)
Map_4 = {'STEPH':'Stephanie George'}
DB.ImportFile(r'C:\Users\Chris\Documents\League\Three Way\Source\Week_4_Postbowl_1.xls', Map_4,
              NewDate=(2016, 8, 10), ByGame = True)

DB.LaneInfo()

# Add scores for week 1
Week = 1
Score_Week_Pin_Position(DB, New_League, Week,
                        Vacant=('Danual', 'Ian', 'Vacant 1', 'Vacant 2'),
                        Prebowl=('Alysha', 'Devan', 'Clare', 'Dayna', 'Phil'),
                        Calculate=False, Report=False)

Week = 2
Score_Week_Pin_Position(DB, New_League, Week,
                        Vacant=('Danual', 'Alysha', 'Vacant 1', 'Vacant 2'),
                        Prebowl=('Chris H', 'Devan'),
                        Calculate=False, Report=False)
# Backdate handicaps

for Member in New_League.League:
    Member.hcps[1] = Member.hcps[2]
    Member.hseries[1] = [G + Member.hcps[1] for G in Member.series[1]]
    Member.hseries[2] = [G + Member.hcps[2] for G in Member.series[2]]


# Calculate Weekly Scores
New_League.CalculateWeeklyPoints(1)

# Print HTML report for the week...
New_League.LaTeXWeekly(1)

# Calculate Weekly Scores
New_League.CalculateWeeklyPoints(2)

# Print HTML report for the week...
New_League.LaTeXWeekly(2)

Week = 3
Score_Week_Pin_Position(DB, New_League, Week,
                        Vacant=('Roger', 'Alysha', 'Steph', 'Vacant 1', 'Vacant 2'),
                        Prebowl = ('Shane D',))

Week = 4
Score_Week_Pin_Position(DB, New_League, Week,
                        Vacant=('Alysha', 'Vacant 1', 'Vacant 2'),
                        Prebowl = ('Chris H', 'Ash', 'Roger', 'Dayna'),
                        Calculate=False, Report=False)

New_League.AddSeries('Ash', 4, 146, 109, 140, 166, 193, 119)
New_League.AddSeries('Dayna', 4, 210, 191, 192, 151, 157, 184)
New_League.AddSeries('Roger', 4, 165, 191, 214, 189, 188, 168)
#New_League.AddSeries('Steph', 4, 175, 174, 132, 147, 125, 149)
# Calculate Weekly Scores
New_League.CalculateWeeklyPoints(4)

# Print HTML report for the week...
New_League.LaTeXWeekly(4)
# Print the schedule
New_League.CompleteSchedule()

HTMLStatistics(DB, New_League)
