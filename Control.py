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
from Utilities import HTMLStatistics, Brackets_Simulation, Score_Week_Pin_Position

# Declare league object
New_League = League(n=24)
# Add league data
New_League.LeagueData(weeklen=11, lanes=16, base=220, sdate='27/04/2016',
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
            [1, 6, 13, 18, 2, 14, 8, 10, 3, 16, 15, 4, 5, 17, 22, 20, 7, 11, 19, 23, 9, 24, 21, 12],
            [16, 24, 18, 7, 20, 23, 14, 17, 11, 19, 9, 22, 6, 10, 8, 1, 15, 12, 4, 5, 13, 3, 2, 21]]

New_League.Pattern = [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 3]

for week in range(1, 40): New_League.SetTotals(week, ISerW = 6, ISerD = 3)
# Add schedule to league
New_League.AddSchedule(Schedule)
# Create and add bowlers to league
Names = ['Ash Ball', 'Devan Sahayam', 'Clare Sahayam', 'David Brierley', 'Rob Pollock',
         'Mike Gibbs', 'Roger Tucker', 'Andy Smith', 'Terry Mustchin', 'Kelly Wilson',
         'Stephanie George', 'Danual Paton', 'Kevin Foubister', 'Shane Forde', 'Hamish McGrigor',
         'Susan Munro', 'Leonard Reeves', 'Alysha Carr-Brooks', 'Chris Haynes', 'Chris Ball',
         'Vacant', 'Dayna Haylock', 'Alan Griffin', 'Daniel Simon']
DispNames = ['Ash', 'Devan', 'Clare', 'David', 'Rob', 'Gibby', 'Roger', 'Andy',
             'Terry', 'Kelly', 'Steph', 'Danual', 'Kevin', 'Shane', 'Hamish', 'Susan',
             'Leonard', 'Alysha', 'Chris H', 'Chris B', 'Vacant', 'Dayna', 'Alan', 'Daniel']
Female = [False, False, True, False, False, False, False, False,
          False, True, True, False, False, False, False, True,
          False, True, False, False, False, True, False, False, False]
for DName, Name, F in zip([N.lower() for N in DispNames], Names, Female):
    New_League.AddNewBowler(Name, DName, Female=F)

for Member in New_League.League:
    if Member.name == 'Daniel Simon':
        Member.avgs[0] = 205
        Member.hcps[0] = 15
    if Member.name == 'Alan Griffin':
        Member.avgs[0] = 173
        Member.hcps[0] = 220 - 173
    if Member.name == 'Alysha Carr-Brooks':
        Member.avgs[0] = 164
        Member.hcps[0] = 220 - 164

# Add scores for week 1
Week = 1
New_League.AddSeries('Ash', Week, 212, 130, 214, 188, 181, 190)
New_League.AddSeries('Devan', Week, 156, 192, 192, 140, 143, 159)
New_League.AddSeries('Clare', Week, 130, 147, 169, 129, 133, 136)
New_League.AddSeries('David', Week, 155, 146, 166, 142, 138, 204)
New_League.AddSeries('Rob', Week, 164, 148, 147, 225, 169, 192)
New_League.AddSeries('Gibby', Week, 209, 188, 215, 200, 201, 209)
New_League.AddSeries('Terry', Week, 172, 201, 174, 182, 182, 203)
New_League.AddSeries('Andy', Week, 170, 171, 149, 150, 175, 188)
New_League.AddSeries('Roger', Week, 194, 187, 175, 208, 182, 179)
New_League.AddSeries('Kelly', Week, 160, 180, 158, 155, 173, 193)
New_League.AddSeries('Steph', Week, 204, 200, 184, 166, 177, 159)
New_League.AddSeries('Danual', Week, 126, 212, 189, 173, 167, 218)
New_League.AddSeries('Kevin', Week, 164, 186, 179, 154, 208, 189)
New_League.AddSeries('Shane', Week, 151, 171, 167, 160, 142, 170)
New_League.AddSeries('Hamish', Week, 191, 137, 210, 183, 162, 226)
New_League.AddSeries('Susan', Week, 175, 146, 126, 156, 171, 171)
New_League.AddSeries('Leonard', Week, 200, 239, 160, 152, 206, 245)
New_League.AddSeries('Chris B', Week, 210, 179, 233, 186, 177, 204)
New_League.AddSeries('Chris H', Week, 204, 245, 275, 201, 236, 163)
New_League.AddSeries('Dayna', Week, 165, 166, 168, 166, 140, 169)

New_League.BlindCorrection('Daniel', Week)
New_League.BlindCorrection('Alan', Week)
New_League.BlindCorrection('Alysha', Week)
New_League.BlindCorrection('Vacant', Week)

Week = 2

# Initialise the database!!!
DB = Database()
Map = {i.upper(): j for i, j in zip(DispNames, Names)}
# Exclude = ['VACANT', 'vacant', 'Player', 'BYE']
DB.ImportFile(r'C:\Users\Chris\Documents\League\Three Way\Source\Week_2.xls', Map)
DB.LaneInfo()
DB.Players = [DB.Players[0]]
HTMLStatistics(DB, New_League)
STOP

Map = {i: j for i, j in zip(DispNames, Names)}
Exclude = ['VACANT', 'vacant', 'Player', 'BYE', 'Roger', 'Daniel']
DB.ImportFile(r'C:\Users\Chris\Documents\League\Three Way\Source\Week_3.xls', Map, Exclude=Exclude)
# Remove Steph's blind games
for P in DB.Players:
    if P.Name == 'Stephanie George':
        P.Games = P.Games[:9]
# And start from here...
Map = {i.upper(): j for i, j in zip(DispNames, Names)}
Map['andy'] = 'Andy Smith'
Exclude = ['VACANT', 'vacant', 'Player', 'SHANE']
# DB.ImportFile(r'C:\Users\Chris\Documents\League\Three Way\Source\Week_4.xls',Map,ByGame = True, Exclude=Exclude)
DB.ImportFile(r'C:\Users\Chris\Documents\League\Three Way\Source\Week_4_Updated.xls', Map, Exclude=Exclude,
              NewDate=(2016, 5, 18))
Map = {i.upper(): j for i, j in zip(DispNames, Names)}
# Exclude = ['VACANT', 'vacant', 'Player', 'BYE']
DB.ImportFile(r'C:\Users\Chris\Documents\League\Three Way\Source\Week_5.xls', Map)
Map['LENNY'] = 'Leonard Reeves'
Map['LUKE'] = 'Luke'
Exclude = ['VACANT', 'vacant', 'Player', 'BYE', 'Vacant', 'TERRY']
DB.ImportFile(r'C:\Users\Chris\Documents\League\Three Way\Source\Week_6.xls', Map, Exclude=Exclude)
Map = {i.upper(): j for i, j in zip(DispNames, Names) if i != 'Alysha'}
Map['LUKE'] = 'Luke'
Map['Alysha'] = 'Alysha Carr-Brooks'
Exclude = ['VACANT', 'vacant', 'Player', 'BYE', 'Vacant', 'ALYSHA']
DB.ImportFile(r'C:\Users\Chris\Documents\League\Three Way\Source\Week_7.xls', Map, ByGame=True, Exclude=Exclude)
# Exclude = ['VACANT', 'vacant', 'Player', 'BYE', 'Vacant']
print("Week 8")
Map['ALYSHA'] = 'Alysha Carr-Brooks'
Map['CHRIS BALL'] = 'Chris Ball'
DB.ImportFile(r'C:\Users\Chris\Documents\League\Three Way\Source\Week_8.xls', Map)
Exclude = ['VACANT', 'vacant', 'Player', 'BYE', 'Vacant', 'DANUAL', 'CHRIS B', 'JOSH']
DB.ImportFile(r'C:\Users\Chris\Documents\League\Three Way\Source\Week_9.xls', Map, Exclude=Exclude)
Exclude = ['VACANT', 'vacant', 'Player', 'BYE', 'Vacant', 'LEONARD']
DB.ImportFile(r'C:\Users\Chris\Documents\League\Three Way\Source\Week_10.xls', Map, Exclude=Exclude)
Exclude = ['VACANT', 'vacant', 'Player', 'BYE', 'Vacant']
DB.ImportFile(r'C:\Users\Chris\Documents\League\Three Way\Source\Week_11.xls', Map, Exclude=Exclude)
Exclude = ['VACANT', 'vacant', 'Player', 'BYE', 'Vacant']
DB.ImportFile(r'C:\Users\Chris\Documents\League\Three Way\Source\Week_12.xls', Map, Exclude=Exclude)
DB.LaneInfo()
HTMLStatistics(DB, New_League)

for P in DB.Players:
    Sc = [G.FS[-2] for G in P.Games if G.Meta[2].date() == New_League.dates[Week - 1]]
    if len(Sc) != 6:
        print(P.Name, 'has no scores for week', Week)
        continue
    New_League.AddSeries(P.Name, Week, Sc[0], Sc[1], Sc[2], Sc[3], Sc[4], Sc[5])

New_League.AddSeries('Roger', Week, 170, 157, 147, 208, 171, 178)
# Add blinds
New_League.BlindCorrection('Alan', Week)
New_League.BlindCorrection('Alysha', Week)
New_League.BlindCorrection('Vacant', Week)

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

for P in DB.Players:
    Sc = [G.FS[-2] for G in P.Games if G.Meta[2].date() == New_League.dates[Week - 1]]
    if P.Name == 'Stephanie George': continue
    if len(Sc) != 6:
        print(P.Name, 'has no scores for week', Week)
        continue
    New_League.AddSeries(P.Name, Week, Sc[0], Sc[1], Sc[2], Sc[3], Sc[4], Sc[5])

New_League.BlindCorrection('Roger', Week)
New_League.BlindCorrection('Daniel', Week)
New_League.BlindCorrection('Steph', Week)
New_League.BlindCorrection('Vacant', Week)
# Correction for Steph.
New_League.League[10].AddPoints(Week, [2, 0, 0, 0, 0, 0, 0], 'Scratch')
New_League.League[10].AddPoints(Week, [2, 0, 0, 0, 0, 0, 0], 'Handicap')

# Calculate Weekly Scores
New_League.CalculateWeeklyPoints(3)

# Print HTML report for the week...
New_League.LaTeXWeekly(3)

Score_Week_Pin_Position(DB, New_League, 4, Vacant=('Vacant', 'Shane'))

Week = 5
New_League.AddSeries('Clare', Week, 139, 140, 134, 164, 137, 210)
Score_Week_Pin_Position(DB, New_League, 5, Vacant=('Vacant', 'Roger'))

Brackets_Simulation(New_League, 3)
Brackets_Simulation(New_League, 5)

# Luke joins us in place of Daniel...

SP = New_League.League[-1].SPoints.copy()
HP = New_League.League[-1].HPoints.copy()
New_League.League[-1] = Bowler('Luke', dispname='Luke', Female=False)
New_League.League[-1].SPoints = SP
New_League.League[-1].HPoints = HP
New_League.NameToLocationMap()

New_League.AddSeries('Terry', 6, 198, 157, 197, 188, 194, 146)

Score_Week_Pin_Position(DB, New_League, 6, Vacant=('Vacant',))
Score_Week_Pin_Position(DB, New_League, 7, Vacant=('Vacant', 'Alan'))
Score_Week_Pin_Position(DB, New_League, 8, Vacant=('Vacant', 'Gibby', 'Kelly', 'Danual'))
Score_Week_Pin_Position(DB, New_League, 9, Vacant=('Vacant', 'Chris B', 'Danual'))
Score_Week_Pin_Position(DB, New_League, 10, Vacant=('Vacant', 'Chris B', 'Danual', 'Leonard'))
Score_Week_Pin_Position(DB, New_League, 11,
                        Vacant=('Vacant', 'Chris B', 'Rob Pollock', 'Roger Tucker', 'Stephanie George'))

for week in range(1, 40): New_League.SetTotals(week, ISerW=12, ISerD=6, IWinP=4, IDrawP=2)

Score_Week_Pin_Position(DB, New_League, 12, Vacant=('Vacant', 'Rob Pollock', 'Leonard'))
# Print the schedule
New_League.CompleteSchedule()

Brackets_Simulation(New_League, 7)
Brackets_Simulation(New_League, 9)
Brackets_Simulation(New_League, 11)
