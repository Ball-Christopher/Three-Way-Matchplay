'''
Author: Christopher Ball
Create Date: 29/01/2016

Purpose: To control the three-way league running
at North City Tenpin.
'''

from BowlerTeamsTest import *

# Declare league object
New_League = League(n = 21)
# Add league data
New_League.LeagueData(weeklen = 10, lanes = 14, base = 220, sdate = '27/01/2016',
                      Lname = 'North City Singles', BCenter = 'North City Tenpin')
# Create a league schedule
Schedule = [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21],
            [11, 7, 13, 16, 12, 1, 20, 2, 5, 4, 14, 21, 10, 19, 8, 17, 9, 3, 6, 18, 15],
            [8, 3, 18, 11, 2, 14, 16, 4, 15, 19, 7, 17, 12, 9, 6, 10, 5, 21, 13, 1, 20],
            [12, 19, 4, 7, 14, 6, 1, 21, 18, 16, 3, 5, 8, 13, 17, 11, 20, 15, 10, 9, 2],
            [19, 5, 15, 12, 8, 21, 16, 13, 6, 20, 4, 9, 7, 2, 18, 10, 14, 3, 11, 1, 17],
            [16, 10, 7, 13, 9, 21, 12, 17, 5, 8, 2, 15, 20, 3, 6, 19, 1, 14, 11, 4, 18],
            [17, 21, 6, 10, 20, 18, 1, 9, 15, 8, 14, 5, 11, 16, 19, 12, 13, 2, 7, 4, 3],
            [16, 14, 9, 10, 17, 15, 19, 2, 6, 7, 12, 20, 11, 21, 3, 1, 8, 4, 13, 5, 18],
            [11, 9, 5, 19, 13, 3, 12, 14, 18, 10, 1, 6, 4, 17, 2, 7, 21, 15, 16, 8, 20],
            [17, 20, 14, 19, 9, 18, 10, 13, 4, 16, 2, 21, 7, 1, 5, 11, 8, 6, 12, 3, 15]]

for week in range(1, 40): New_League.SetTotals(week, ISerW = 6, ISerD = 3)
# Add schedule to league
New_League.AddSchedule(Schedule)
# Create and add bowlers to league
Names = ['Annabelle Swain', 'Tim Swain', 'Wink Mustchin', 'Andy Smith', 'Terry Mustchin',
         'David Brierley', 'Chris Ball', 'Hamish McGrigor', 'Leonard Reeves',
         'Danual Paton', 'Kelly Wilson', 'Chris Haynes', 'Ash Ball', 'Roger Tucker',
         'Susan Munro', 'Dayna Haylock', 'Kevin Foubister', 'Alan Griffin', 'Clare Sahayam',
         'Mike Gibbs', 'Lil Plunket']
DispNames = ['Belle', 'Tim', 'Wink', 'Andy', 'Terry', 'David',
         'Chris B', 'Hamish', 'Leonard', 'Danual', 'Kelly', 'Chris H',
         'Ash', 'Roger', 'Susan', 'Dayna', 'Kevin', 'Alan', 'Clare', 'Gibby', 'Lil']
Female = [True, False, True, False, False, False,
          False, False, False, False, True, False,
          False, False, True, True, False, False, True, False, True]
for DName, Name, F in zip(DispNames, Names, Female):
    New_League.AddNewBowler(Name, DName, Female = F)

# Add scores for week 1
Week = 1
New_League.AddSeries('Belle', Week, 180, 173, 169, 138, 209, 180) #1049
New_League.AddSeries('Tim', Week, 224, 187, 171, 163, 172, 182) #1099
New_League.AddSeries('Wink', Week, 196, 154, 148, 147, 138, 138) #921
New_League.AddSeries('Andy', Week, 140, 192, 118, 190, 204, 197) #1041
New_League.AddSeries('Terry', Week, 198, 221, 181, 223, 177, 210) #1210
New_League.AddSeries('David', Week, 145, 224, 138, 171, 154, 204) #1036
New_League.AddSeries('Chris B', Week, 183, 170, 181, 172, 200, 197) #1103
New_League.AddSeries('Hamish', Week, 166, 120, 170, 188, 209, 135) #988
New_League.AddSeries('Leonard', Week, 179, 164, 158, 165, 215, 180) #1061
New_League.AddSeries('Danual', Week, 126, 174, 156, 172, 156, 183) #967
New_League.AddSeries('Kelly', Week, 165, 158, 203, 200, 148, 187) #1061
New_League.AddSeries('Chris H', Week, 222, 175, 221, 221, 240, 187) #1266
New_League.AddSeries('Ash', Week, 144, 142, 170, 201, 199, 149) #1005
New_League.AddSeries('Roger', Week, 170, 184, 207, 179, 178, 241) #1159
New_League.AddSeries('Susan', Week, 169, 164, 129, 190, 175, 212) #1039
New_League.AddSeries('Dayna', Week, 146, 177, 191, 202, 166, 178) #1060
New_League.AddSeries('Kevin', Week, 162, 188, 210, 177, 158, 224) #1119
New_League.AddSeries('Clare', Week, 201, 120, 104, 146, 149, 127) #847
New_League.AddSeries('Gibby', Week, 154, 126, 218, 153, 179, 160) #990
New_League.AddSeries('Alan', Week, 154, 190, 194, 210, 166, 170)

New_League.League[New_League.NameLocationMap['Lil']].avgs[0] = 145
New_League.League[New_League.NameLocationMap['Lil']].hcps[0] = 220 - 145
New_League.BlindCorrection('Lil', Week)

Week = 2
New_League.AddSeries('Belle', Week, 167, 196, 192, 178, 196, 167)
New_League.AddSeries('Tim', Week, 202, 190, 158, 201, 211, 190)
New_League.AddSeries('Wink', Week, 171, 161, 159, 169, 128, 170)
New_League.AddSeries('Andy', Week, 172, 163, 160, 177, 144, 146)
New_League.AddSeries('Terry', Week, 197, 189, 181, 213, 166, 182)
New_League.AddSeries('David', Week, 190, 171, 141, 207, 211, 180)
New_League.AddSeries('Chris B', Week, 202, 211, 222, 215, 234, 169)
New_League.AddSeries('Hamish', Week, 150, 192, 198, 173, 206, 153)
New_League.AddSeries('Leonard', Week, 213, 211, 158, 163, 201, 222)
New_League.AddSeries('Danual', Week, 181, 199, 190, 155, 182, 194)
New_League.AddSeries('Kelly', Week, 165, 156, 184, 169, 145, 178)
New_League.AddSeries('Chris H', Week, 232, 269, 220, 203, 221, 227)
New_League.AddSeries('Ash', Week, 140, 180, 166, 146, 140, 180)
New_League.AddSeries('Roger', Week, 190, 190, 230, 213, 221, 177)
New_League.AddSeries('Susan', Week, 158, 151, 152, 162, 158, 155)
New_League.AddSeries('Dayna', Week, 144, 168, 184, 173, 160, 159)
New_League.AddSeries('Kevin', Week, 219, 211, 165, 204, 252, 183)
New_League.AddSeries('Clare', Week, 109, 165, 165, 157, 149, 157)
New_League.AddSeries('Gibby', Week, 205, 202, 195, 210, 149, 190)
New_League.AddSeries('Alan', Week, 159, 139, 187, 149, 160, 169)

New_League.BlindCorrection('Lil', Week)

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

# Print the schedule
New_League.CompleteSchedule()