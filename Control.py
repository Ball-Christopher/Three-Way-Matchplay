"""
Author: Christopher Ball
Create Date: 29/01/2016

Purpose: To control the three-way league running
at North City Tenpin.

TODO:
1) Gather all of the utilities, particularly HTML, in the same place.
2) Brackets and against the field utilities.
3) Base64 encode pin position and pdf through webkit, see
http://stackoverflow.com/questions/24846171/how-to-convert-an-html-document-containing-an-svg-to-a-pdf-file-in-python
4) Automate the league scoring, no more week variable and cut/paste.
5) Clean up the console printed output, including pdfkit output if possible.
"""
from BowlerTeamsTest import *
from Database import *


def HTMLStatistics(DB, League):
    config = pdfkit.configuration(wkhtmltopdf=bytes(r'C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe', 'utf-8'))
    path = r'C:\Users\Chris\Documents\League\Three Way\HTML\css\\'
    css = [path + 'skeleton.css']
    for P in DB.Players:
        # Get the player's first name (assume unique for now)
        F = '_'.join(P.Name.title().split())
        hfile = os.getcwd() + '/HTML/Stats_{0}.html'.format(F)
        h = open(hfile, 'w')
        New_League.WritePreambleHTML(h, F, Full=False, Script=False)
        Span = [2] * 9
        Span.append(3)
        # Span.extend([3,3])
        Head = list(range(1, 11))
        # Head.append('Total')
        LastDate = ''
        # Extract dates for table of contents
        Dates = []
        for G in P.Games:
            if G.Meta[2].date() in Dates:
                continue
            Dates.append(G.Meta[2].date())
        # Add navigation to the page.
        h.write('<div class="container">\n<div class="row">\n<div class="six columns" style="margin-top: 15%">')
        h.write('<h4>Pin Position Game Stats for {0}</h4>\n'.format(P.Name.title()))
        h.write(
            'Orange background denotes open frames, Red background denotes splits.  Pin position details for each game can be found by clicking on the frame scores.  These results will be progressively improved over the season.')
        h.write('</div>\n<div class="six columns" style="margin-top: 15%">\n<h4>On this page</h4>\n<ol>\n')
        h.write('<li><a href="#Comparison">Detailed League Statistics</a></li>\n')
        h.write('<li><a href="#Common">Spare Effectiveness by Combination Left</a></li>\n')
        for Date in Dates:
            h.write('<li><a href="#{0}">{1}{0}</a></li>\n'.format(custom_strftime('{S} of %B, %Y', Date),
                                                                  'Series bowled on '))
        h.write('</ol>\n</div>\n</div>\n</div>')
        # Section comparing bowler to others
        Head_Comp = ["Name", "200 Games", "Avg", "High", "Spares", "Strikes", "Open",
                     "Splits", "Splits Converted", "Single Pins Missed", "Single Pins Left", "Errors", "Avg Game Time"]
        Text = []
        for Pl in DB.Players:
            Text.append(Pl.SummaryStats(1))
        Text.sort(key=lambda key: -key[2])
        h.write('<h2 id="Comparison">Detailed League Statistics</h2>\n')
        h.write('Note that only series bowled with the new computer system (installed in Week 2) will be counted here.')
        Comp = {'Names': Head_Comp,
                'TParams': ['l'] * len(Head_Comp),
                'HeadFormatB': ['{\\tiny{\\bf '] * len(Head_Comp), 'HeadFormatE': ['}}'] * len(Head_Comp),
                'Size': -1, 'Guide': True, 'TwoColumn': False}
        League.WriteHTML(h, Text, Comp, cls='standtable')
        # Spare effectiveness by combinations
        P.MostCommonLeaves()
        Pairs = sorted(P.Left.items(), key=lambda x: -x[1])
        count = 0
        Cols = 5
        h.write('<h2 id="Common">Spare Effectiveness by Combination Left</h2>\n')
        h.write('<table class="sparetable" border="1">\n')
        h.write('<tbody>\n')
        h.write('<tr>\n')
        for (key, value) in Pairs:
            if count == Cols:
                h.write('</tr>\n')
                h.write('<tr>\n')
                count = 0
            h.write('<td>\n<center>\n')
            h.write('<svg width="100%" height="auto" viewBox="0 0 8 8" >\n')
            X = [4, 3, 5, 2, 4, 6, 1, 3, 5, 7]
            Y = [7, 5, 5, 3, 3, 3, 1, 1, 1, 1]
            for i in range(1, 11):
                h.write('<circle cx="{0}" cy="{1}" r="0.75" fill = "{2}"></circle>\n'.format(
                    X[i - 1], Y[i - 1], 'black' if i in key else 'gray'))
                h.write('<circle cx="{0}" cy="{1}" r="{2}" fill = "white"></circle>\n'.format(
                    X[i - 1], Y[i - 1], 0.7 if i not in key else 0.65))
                if i in key:
                    h.write('<text x="{0}" y="{1}" font-size="1"> {2} </text>\n'.format(
                        X[i - 1] - (0.3 if i != 10 else 0.55), Y[i - 1] + 0.35, i))
                h.write('<text x="{0}" y="{1}" font-size="0.8"> {2} </text>\n'.format(
                    5.5, 7, str(round(100 * P.Spared[key] / P.Left[key])) + '%'))
                h.write('<text x="{0}" y="{1}" font-size="0.8"> {2} </text>\n'.format(
                    0.5, 7, str(P.Spared[key]) + '/' + str(P.Left[key])))

            h.write('</svg>\n</center>\n</td>\n')
            count += 1
        h.write('</tbody>\n</table>\n')
        # Section outputting frame-by-frame
        for G in P.Games:
            if G.Meta[2].date() != LastDate:
                if LastDate != '':
                    h.write('</tbody>\n</table>\n')
                h.write(
                    '<h2 id="{0}">Frame-by-frame {0}</h2>'.format(custom_strftime('{S} of %B, %Y', G.Meta[2].date())))
                h.write('<table class="frametable" border="1" id="report">\n<thead>\n')
                for i, j in zip(Span, Head):
                    h.write('<th colspan = "{0}"><center>{1}</center></th>\n'.format(i, j))
                h.write('</thead>\n<tbody>')
                h.write('<tr>\n')
                LastDate = G.Meta[2].date()
            # style="background-color: rgba(255,0,0,0.5)
            for i, j in enumerate(G.NormalScore):
                # Correction for 10th frames...
                if i < 19 and i // 2 < len(G.SplitFrames) and G.SplitFrames[i // 2] and i % 2 == 0:
                    h.write('<td style="background-color: rgba(255,0,0,0.5)">{0}</td>\n'.format(j))
                elif i == 19 and G.NormalScore[-3] == 'X' and len(G.SplitFrames) == 11 and G.SplitFrames[-1] == 1:
                    h.write('<td style="background-color: rgba(255,0,0,0.5)">{0}</td>\n'.format(j))
                elif i == 20 and G.NormalScore[-2] == 'X' and len(G.SplitFrames) == 12 and G.SplitFrames[-1] == 1:
                    h.write('<td style="background-color: rgba(255,0,0,0.5)">{0}</td>\n'.format(j))
                elif i < 19 and i % 2 and j not in ('/', 'X'):
                    # Highlight open frames.
                    h.write('<td style="background-color: rgba(255,165,0,0.5)">{0}</td>\n'.format(j))
                elif i == 19 and G.NormalScore[-1] == '':
                    h.write('<td style="background-color: rgba(255,165,0,0.5)">{0}</td>\n'.format(j))
                elif i == 20 and G.NormalScore[-2] not in ('/', 'X') and j not in ('/'):
                    h.write('<td style="background-color: rgba(255,165,0,0.5)">{0}</td>\n'.format(j))
                else:
                    h.write('<td>{0}</td>\n'.format(j))
            h.write('</tr>\n')
            h.write('<tr>\n')
            for i, j in zip(G.FSTest, Span):
                h.write('<td colspan = "{1}"><center>{0}</center></td>\n'.format(i, j))
            h.write('</tr>\n')
            h.write('<tr>\n')
            for Frame in range(1, 11):
                if Frame == 10:
                    h.write('<td colspan = "3"><center>\n')
                    h.write('<svg width="100%" height="auto" viewBox="0 0 24 16" >')
                else:
                    h.write('<td colspan = "2"><center>\n')
                    h.write('<svg width="auto" height = "100%" viewBox="0 0 8 8" >')
                # Now create svg images of each shot dynamically
                if Frame == 10:
                    # Slightly different
                    if 11 not in G.PinPos:
                        Shots = 1
                    elif 12 not in G.PinPos:
                        Shots = 2
                    else:
                        Shots = 3
                    if Shots == 3:
                        Mult = 1
                    else:
                        Mult = 1.5
                    for S in range(Shots):
                        [First, Second] = G.PinPos[Frame + S]
                        X = [4, 3, 5, 2, 4, 6, 1, 3, 5, 7]
                        Y = [7, 5, 5, 3, 3, 3, 1, 1, 1, 1]
                        for i in range(1, 11):
                            h.write('<circle cx="{0}" cy="{1}" r="0.75" fill = "{2}"></circle>\n'.format(
                                Mult * (X[i - 1] + 8 * S), 2 * Y[i - 1], 'black' if i in First else 'gray'))
                            if i not in Second:
                                h.write('<circle cx="{0}" cy="{1}" r="{2}" fill = "white"></circle>\n'.format(
                                    Mult * (X[i - 1] + 8 * S), 2 * Y[i - 1], 0.6 if i not in First else 0.4))
                    if Shots == 2:
                        h.write('<line x1="12" y1="0" x2="12" y2="16" style="stroke:rgb(0,0,0);stroke-width:0.1"/>\n')
                    if Shots == 3:
                        h.write('<line x1="8" y1="0" x2="8" y2="16" style="stroke:rgb(0,0,0);stroke-width:0.1"/>\n')
                        h.write('<line x1="16" y1="0" x2="16" y2="16" style="stroke:rgb(0,0,0);stroke-width:0.1" />\n')
                    pass
                else:
                    [First, Second] = G.PinPos[Frame]
                    X = [4, 3, 5, 2, 4, 6, 1, 3, 5, 7]
                    Y = [7, 5, 5, 3, 3, 3, 1, 1, 1, 1]
                    for i in range(1, 11):
                        h.write('<circle cx="{0}" cy="{1}" r="0.5" fill = "{2}"></circle>\n'.format(
                            X[i - 1], Y[i - 1], 'black' if i in First else 'gray'))
                        if i not in Second:
                            h.write('<circle cx="{0}" cy="{1}" r="{2}" fill = "white"></circle>\n'.format(
                                X[i - 1], Y[i - 1], 0.45 if i not in First else 0.4))
                h.write('</svg></center></td>')
            h.write('</tr>\n')
        h.write('</tbody>\n</table>\n')
        h.write('</div>\n</div>\n</div>\n</body>\n</html>')
        h.close()
        options = {'margin-top': '0in',
                   'margin-right': '0in',
                   'margin-bottom': '0in',
                   'margin-left': '0in',
                   'footer-right': '[page]'}
        # pdfkit.from_file(hfile, os.getcwd()+r'\HTML\Stats_{0}.pdf'.format(F),
        #                 configuration = config, css = css, options = options)

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
            [1, 6, 13, 18, 2, 14, 8, 10, 3, 16, 15, 4, 5, 17, 22, 20, 7, 11, 19, 23, 9, 24, 21, 12]]

New_League.Pattern = [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4]

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
# New_League.League[New_League.NameLocationMap['Lil']].avgs[0] = 145
# New_League.League[New_League.NameLocationMap['Lil']].hcps[0] = 220 - 145
# New_League.BlindCorrection('Lil', Week)

Week = 2

# Initialise the database!!!
DB = Database()
Map = {i.upper(): j for i, j in zip(DispNames, Names)}
# Exclude = ['VACANT', 'vacant', 'Player', 'BYE']
DB.ImportFile(r'C:\Users\Chris\Documents\League\Three Way\Source\Week_2.xls', Map)
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
DB.LaneInfo()
HTMLStatistics(DB, New_League)

for Player in DB.Players:
    print(Player.Name)
    Sc = [G.FS[-2] for G in Player.Games if G.Meta[2].date() == New_League.dates[Week - 1]]
    if len(Sc) != 6:
        print(Player.Name, 'has no scores for week', Week)
        continue
    New_League.AddSeries(Player.Name, Week, Sc[0], Sc[1], Sc[2], Sc[3], Sc[4], Sc[5])

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

for Player in DB.Players:
    Sc = [G.FS[-2] for G in Player.Games if G.Meta[2].date() == New_League.dates[Week - 1]]
    if Player.Name == 'Stephanie George': continue
    if len(Sc) != 6:
        print(Player.Name, 'has no scores for week', Week)
        continue
    New_League.AddSeries(Player.Name, Week, Sc[0], Sc[1], Sc[2], Sc[3], Sc[4], Sc[5])

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

Week = 4

for Player in DB.Players:
    Sc = [G.FS[-2] for G in Player.Games if G.Meta[2].date() == New_League.dates[Week - 1]]
    if Player.Name == 'Stephanie George': print(Sc)
    if len(Sc) != 6:
        print(Player.Name, 'has no scores for week', Week)
        continue
    New_League.AddSeries(Player.Name, Week, Sc[0], Sc[1], Sc[2], Sc[3], Sc[4], Sc[5])

# New_League.AddSeries('Hamish', Week, 186, 109, 134, 196, 201, 154)
# New_League.AddSeries('Andy', Week, 156, 184, 187, 184, 150, 152)
New_League.BlindCorrection('Vacant', Week)
New_League.BlindCorrection('Shane', Week)

# Calculate Weekly Scores
New_League.CalculateWeeklyPoints(Week)

# Print HTML report for the week...
New_League.LaTeXWeekly(Week)

Week = 5

for Player in DB.Players:
    Sc = [G.FS[-2] for G in Player.Games if G.Meta[2].date() == New_League.dates[Week - 1]]
    if len(Sc) != 6:
        print(Player.Name, 'has no scores for week', Week)
        continue
    New_League.AddSeries(Player.Name, Week, Sc[0], Sc[1], Sc[2], Sc[3], Sc[4], Sc[5])

New_League.BlindCorrection('Vacant', Week)
New_League.AddSeries('Clare', Week, 139, 140, 134, 164, 137, 210)
New_League.BlindCorrection('Roger', Week)

# Calculate Weekly Scores
New_League.CalculateWeeklyPoints(Week)

# Print HTML report for the week...
New_League.LaTeXWeekly(Week)

Week = 6

# Luke joins us in place of Daniel...

SP = New_League.League[-1].SPoints.copy()
HP = New_League.League[-1].HPoints.copy()
New_League.League[-1] = Bowler('Luke', dispname='Luke', Female=False)
New_League.League[-1].SPoints = SP
New_League.League[-1].HPoints = HP
New_League.NameToLocationMap()

for Player in DB.Players:
    Sc = [G.FS[-2] for G in Player.Games if G.Meta[2].date() == New_League.dates[Week - 1]]
    if len(Sc) != 6:
        print(Player.Name, 'has no scores for week', Week)
        continue
    New_League.AddSeries(Player.Name, Week, Sc[0], Sc[1], Sc[2], Sc[3], Sc[4], Sc[5])

New_League.BlindCorrection('Vacant', Week)
# New_League.BlindCorrection('Daniel', Week)
New_League.AddSeries('Terry', Week, 198, 157, 197, 188, 194, 146)

# Calculate Weekly Scores
New_League.CalculateWeeklyPoints(Week)

# Print HTML report for the week...
New_League.LaTeXWeekly(Week)

Week = 7

for Player in DB.Players:
    Sc = [G.FS[-2] for G in Player.Games if G.Meta[2].date() == New_League.dates[Week - 1]]
    if len(Sc) != 6:
        print(Player.Name, 'has no scores for week', Week)
        continue
    New_League.AddSeries(Player.Name, Week, Sc[0], Sc[1], Sc[2], Sc[3], Sc[4], Sc[5])

New_League.BlindCorrection('Vacant', Week)
New_League.BlindCorrection('Alan', Week)
# New_League.BlindCorrection('Daniel', Week)

# Calculate Weekly Scores
New_League.CalculateWeeklyPoints(Week)

Week = 8

for Player in DB.Players:
    Sc = [G.FS[-2] for G in Player.Games if G.Meta[2].date() == New_League.dates[Week - 1]]
    if len(Sc) != 6:
        print(Player.Name, 'has no scores for week', Week)
        continue
    New_League.AddSeries(Player.Name, Week, Sc[0], Sc[1], Sc[2], Sc[3], Sc[4], Sc[5])

New_League.BlindCorrection('Vacant', Week)
New_League.BlindCorrection('Gibby', Week)
New_League.BlindCorrection('Kelly', Week)
New_League.BlindCorrection('Danual', Week)
# New_League.BlindCorrection('Alan', Week)
# New_League.BlindCorrection('Daniel', Week)

# Calculate Weekly Scores
New_League.CalculateWeeklyPoints(Week)
# Print HTML report for the week...
New_League.LaTeXWeekly(Week)

Week = 9

for Player in DB.Players:
    Sc = [G.FS[-2] for G in Player.Games if G.Meta[2].date() == New_League.dates[Week - 1]]
    if len(Sc) != 6:
        print(Player.Name, 'has no scores for week', Week)
        continue
    New_League.AddSeries(Player.Name, Week, Sc[0], Sc[1], Sc[2], Sc[3], Sc[4], Sc[5])

New_League.BlindCorrection('Vacant', Week)
New_League.BlindCorrection('Chris B', Week)
New_League.BlindCorrection('Danual', Week)
# New_League.BlindCorrection('Alan', Week)
# New_League.BlindCorrection('Daniel', Week)

# Calculate Weekly Scores
New_League.CalculateWeeklyPoints(Week)
# Print HTML report for the week...
New_League.LaTeXWeekly(Week)
# Print the schedule
New_League.CompleteSchedule()