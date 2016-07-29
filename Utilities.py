import os
import random
from base64 import b64encode

import pdfkit


def Score_Week_Pin_Position(DB, League, Week, Vacant=(), Prebowl=(), Calculate=True, Report=True):
    # Add scores from pin position data to league
    for P in DB.Players:
        Sc = [G.FS[-2] for G in P.Games if G.Meta[2].date() == League.dates[Week - 1]]
        if len(Sc) != 6:
            print(P.Name, 'has no scores for week', Week)
            continue
        League.AddSeries(P.Name, Week, Sc[0], Sc[1], Sc[2], Sc[3], Sc[4], Sc[5])

    for P in Vacant:
        League.BlindCorrection(P, Week)

    for P in Prebowl:
        League.Prebowl(P, Week)
    # Calculate Weekly Scores
    if Calculate: League.CalculateWeeklyPoints(Week)
    # Print HTML report for the week...
    if Report: League.LaTeXWeekly(Week)


def Brackets_Simulation(League, Week):
    Winners = {}
    for i in range(10000):
        Br = Brackets(League, Week)
        Name = Br[-1][0][1]
        if Name in Winners:
            Winners[Name] += 1
        else:
            Winners[Name] = 1

    for key, value in Winners.items():
        print(key, value)
    print("===============//===============")


def Brackets(League, Week):
    # Get references to each member of the league.
    L = League.League

    # Get scores for the week in question.
    Scores = [P.GetHSeries(Week) if len(P.GetHSeries(Week)) == 6 else [0] * 6 for P in L]
    Names = [P.name for P in L]

    # Shuffle
    Bind = list(zip(Scores, Names))
    random.shuffle(Bind)
    Scores, Names = zip(*Bind)

    OUT = []
    for Round in range(5):
        Next = []
        Next_Name = []

        if Round == 0:
            Top = 16
        else:
            Top = len(Scores)

        OUT.append([[S[Round], N] for S, N in zip(Scores, Names)])

        for Game in range(0, Top, 2):
            if Scores[Game][Round] > Scores[Game + 1][Round]:
                Next.append(Scores[Game])
                Next_Name.append(Names[Game])
            elif Scores[Game][Round] < Scores[Game + 1][Round]:
                Next.append(Scores[Game + 1])
                Next_Name.append(Names[Game + 1])
            else:
                if Scores[Game][Round + 1] > Scores[Game + 1][Round + 1]:
                    Next.append(Scores[Game])
                    Next_Name.append(Names[Game])
                elif Scores[Game][Round + 1] < Scores[Game + 1][Round + 1]:
                    Next.append(Scores[Game + 1])
                    Next_Name.append(Names[Game + 1])
                else:
                    Next.append(Scores[Game])
                    Next_Name.append(Names[Game])

        if Round == 0:
            Next.extend(Scores[-8:])
            Next_Name.extend(Names[-8:])

        Scores = Next
        Names = Next_Name

    OUT.append([[S[4], N] for S, N in zip(Scores, Names)])
    return (OUT)


def suffix(d):
    return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')


def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))


def WriteHTML(g, Data, TableParam, cls='u-full-width', line_skip=3, font_change=True):
    TableHead = TableParam['Names']
    if cls == 'maintable':
        g.write('<table class="{0}" rules="groups" frame="hsides">\n<thead>\n'.format(cls))
    else:
        g.write('<table class="{0}">\n<thead>\n'.format(cls))
    for el in TableHead:
        g.write('<th>{0}</th>'.format(el))
    g.write('\n')
    g.write('</thead>\n<tbody>\n')
    Count = 0
    for row in Data:
        if cls == 'maintable' and Count % line_skip == 0 and Count > 0:
            g.write('</tbody>\n<tbody>\n')
        if len(row) == 1: continue
        Count += 1
        g.write('<tr>\n')
        for el, al in zip(row, TableParam['TParams']):
            if al == 'r':
                Align = 'style="text-align:right"'
            elif al == 'r':
                Align = 'style="text-align:left"'
            elif al[0] == 'p':
                Align = 'style="text-align:left"'
            else:
                Align = ''
            el = str(el)
            if el.count(r'\bf') > 0:
                Bold = True
                el = el.replace(r'\bf', '')
            else:
                Bold = False
            if el.count(r'\it') > 0:
                Italic = True
                el = el.replace(r'\it', '')
            else:
                Italic = False
            if el.count(r'\textcolor{red}{') > 0:
                Red = True
                el = el.replace(r'\textcolor{red}{', '')
            else:
                Red = False
            for Con in ('{', '}'):
                el = el.replace(Con, '')
            if Bold and font_change:
                g.write('<td style="font-weight:bold" {1}>{0}</td>'.format(el, Align))
            elif Italic and font_change:
                g.write('<td style="text-decoration: underline" {1}>{0}</td>'.format(el, Align))
            elif Red:
                g.write('<td style="color:red" {1}>{0}</td>'.format(el, Align))
            else:
                g.write('<td {1}>{0}</td>'.format(el, Align))
        g.write('</tr>\n')
    g.write('</tbody>\n</table>\n')


def WritePreambleHTML(g, week, Full=True, Script=False, header=True,
                      Leaguename='', BCenter='', dates=(), lanes=0):
    g.write('<!DOCTYPE html>\n<html lang="en">\n')
    if header:
        g.write('<header>\n')
        g.write('<table style="border-bottom:1pt solid black; width: 100%;">\n')
        if type(week) == int:
            g.write(
                '<tr> <td style="width:20%"> {0} </td> <td style="text-align:center; width=60%"> <h4> {1} </h4> </td> <td style="width:20%"> Week {2} </td> </tr>\n'.format(
                    custom_strftime('{S} of %B, %Y', dates[week - 1]), Leaguename, week))
        else:
            g.write(
                '<tr> <td style="width:20%"> {0} </td> <td style="text-align:center; width=60%"> <h4> {1} </h4> </td> <td style="width:20%"> {2} </td> </tr>\n'.format(
                    "", Leaguename, ""))
        g.write('</table>\n<table style="width: 100%;">\n')
        g.write(
            '<tr> <td style="width:20%"> {0} </td> <td style="text-align:center; width=60%"> {1} </td> <td style="width:20%"> Lanes 1 -- {2} </td> </tr>\n'.format(
                dates[0].strftime('6:45pm %A'), BCenter, lanes))
        g.write('</table>\n')
        g.write('</header>\n')
    g.write('<head>\n<meta charset="utf-8">\n')
    g.write('<title>{1} Week {0} Recap</title>'.format(week, Leaguename))
    g.write('<meta name="description" content="">\n<meta name="author" content="">\n')
    g.write('<meta name="viewport" content="width=device-width, initial-scale=1">\n')
    g.write('<link rel="stylesheet" href="css/skeletonpdf.css">\n')
    g.write('</head>\n<body>\n')
    if Full:
        g.write('<h4>{0}</h4>'.format(BCenter))
        g.write('<h4>{0}</h4>'.format(Leaguename))
        g.write('<h4>Week {0}</h4>'.format(week))
        g.write('<h4>{0}</h4>'.format(dates[week - 1].strftime('6:45pm %A %d of %B, %Y')))
        g.write('<h4>On this page</h4>\n')
        g.write('<ol>\n<li><a href="#Standings-Handicap">Standings Handicap</a></li>\n')
        g.write('<li><a href="#Schedule-by-id">Schedule by ID</a></li>\n')
        g.write('<li><a href="#Schedule-by-name">Schedule by Name</a></li>\n')
        g.write('<li><a href="#LWHS">Last Week\'s High Scores</a></li>\n')
        g.write('<li><a href="#SHS">Season High Scores</a></li>\n')
        g.write('<li><a href="#LWBB">Last Week By Bowler</a></li>\n')
        g.write('</ol>\n')
    pass


def Spare_Effectiveness(key, P, debug=False):
    svg_text = '<svg xmlns="http://www.w3.org/2000/svg" width="2500" height="2500" viewBox="0 0 8 8" >'
    X = [4, 3, 5, 2, 4, 6, 1, 3, 5, 7]
    Y = [7, 5, 5, 3, 3, 3, 1, 1, 1, 1]
    for i in range(1, 11):
        svg_text += '<circle cx="{0}" cy="{1}" r="0.75" fill = "{2}"></circle>\n'.format(
            X[i - 1], Y[i - 1], 'black' if i in key else 'gray')
        svg_text += '<circle cx="{0}" cy="{1}" r="{2}" fill = "white"></circle>\n'.format(
            X[i - 1], Y[i - 1], 0.7 if i not in key else 0.65)
        if i in key:
            svg_text += '<text x="{0}" y="{1}" font-size="1" style="font-family: Raleway, san serif; font-weight: 400"> {2} </text>\n'.format(
                X[i - 1] - (0.3 if i != 10 else 0.55), Y[i - 1] + 0.35, i)
        svg_text += '<text x="{0}" y="{1}" font-size="0.8" style="font-family: Raleway, san serif; font-weight: 300"> {2} </text>\n'.format(
            5.5, 7, str(round(100 * P.Spared[key] / P.Left[key])) + '%')
        svg_text += '<text x="{0}" y="{1}" font-size="0.8" style="font-family: Raleway, san serif; font-weight: 300"> {2} </text>\n'.format(
            0.5, 7, str(P.Spared[key]) + '/' + str(P.Left[key]))

    svg_text += '</svg>'

    if debug:
        print(svg_text)
    encoded_string = b64encode(svg_text.encode('utf-8'))
    b64 = encoded_string.decode('utf-8')

    return b64


def Pin_Position_Frame(Frame, G):
    if Frame == 10:
        svg_text = '<svg xmlns="http://www.w3.org/2000/svg" width="2400" height="1600" viewBox="0 0 24 16" >'
    else:
        svg_text = '<svg xmlns="http://www.w3.org/2000/svg" width="2500" height="2500" viewBox="0 0 8 8" >'
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
                svg_text += '<circle cx="{0}" cy="{1}" r="0.75" fill = "{2}"></circle>\n'.format(
                    Mult * (X[i - 1] + 8 * S), 2 * Y[i - 1], 'black' if i in First else 'gray')
                if i not in Second:
                    svg_text += '<circle cx="{0}" cy="{1}" r="{2}" fill = "white"></circle>\n'.format(
                        Mult * (X[i - 1] + 8 * S), 2 * Y[i - 1], 0.6 if i not in First else 0.4)
        if Shots == 2:
            svg_text += '<line x1="12" y1="0" x2="12" y2="16" style="stroke:rgb(0,0,0);stroke-width:0.1"/>\n'
        if Shots == 3:
            svg_text += '<line x1="8" y1="0" x2="8" y2="16" style="stroke:rgb(0,0,0);stroke-width:0.1"/>\n'
            svg_text += '<line x1="16" y1="0" x2="16" y2="16" style="stroke:rgb(0,0,0);stroke-width:0.1" />\n'
        pass
    else:
        [First, Second] = G.PinPos[Frame]
        X = [4, 3, 5, 2, 4, 6, 1, 3, 5, 7]
        Y = [7, 5, 5, 3, 3, 3, 1, 1, 1, 1]
        for i in range(1, 11):
            svg_text += '<circle cx="{0}" cy="{1}" r="0.5" fill = "{2}"></circle>\n'.format(
                X[i - 1], Y[i - 1], 'black' if i in First else 'gray')
            if i not in Second:
                svg_text += '<circle cx="{0}" cy="{1}" r="{2}" fill = "white"></circle>\n'.format(
                    X[i - 1], Y[i - 1], 0.45 if i not in First else 0.4)
    svg_text += '</svg>'

    encoded_string = b64encode(svg_text.encode('utf-8'))
    b64 = encoded_string.decode('utf-8')

    return b64


def HTMLStatistics(DB, League):
    path = r'C:\Users\Chris\Documents\League\Three Way\HTML\css\\'
    for P in DB.Players:
        # Get the player's first name (assume unique for now)
        F = '_'.join(P.Name.title().split())
        hfile = os.getcwd() + '/HTML/Stats_{0}.html'.format(F)
        h = open(hfile, 'w')
        WritePreambleHTML(h, F, Full=False, Script=False, Leaguename=League.Leaguename,
                          BCenter=League.BCenter, dates=League.dates, lanes=League.lanes, header=False)
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
        h.write(
            '<div class="container">\n<div class="rTable">\n<div class="rTableRow">\n<div class="rTableCell" width = "50%">\n')
        h.write('<h4>Pin Position Game Stats for {0}</h4>\n'.format(P.Name.title()))
        h.write(
            'Orange background denotes open frames, Red background denotes splits.  Pin position details for each game can be found by clicking on the frame scores.  These results will be progressively improved over the season.')
        h.write('</div>\n<div class="rTableCell" width = "50%">\n')
        h.write('<h4>On this page</h4>\n<ol>\n')
        h.write('<li><a href="#Comparison">Detailed League Statistics</a></li>\n')
        h.write('<li><a href="#Common">Spare Effectiveness by Combination Left</a></li>\n')
        for Date in Dates:
            h.write('<li><a href="#{0}">{1}{0}</a></li>\n'.format(custom_strftime('{S} of %B, %Y', Date),
                                                                  'Series bowled on '))
        h.write('</ol>\n')
        h.write('</div>\n</div>\n</div>\n</div>\n')
        # Section comparing bowler to others
        Head_Comp = ["Name", "Games", "200 Games", "Average", "High Game", "Spare %", "Strike %", "Open %",
                     "Split %", "Splits Converted %", "Single Pins Missed %", "Error %"]
        Text = []
        for Pl in DB.Players:
            Text.append(Pl.SummaryStats(1))
        Text.sort(key=lambda key: -key[3])
        h.write('<div class="container">\n')
        h.write('<h2 id="Comparison">Detailed League Statistics</h2>\n')
        Comp = {'Names': Head_Comp,
                'TParams': ['l'] * len(Head_Comp),
                'HeadFormatB': ['{\\tiny{\\bf '] * len(Head_Comp), 'HeadFormatE': ['}}'] * len(Head_Comp),
                'Size': -1, 'Guide': True, 'TwoColumn': False}
        WriteHTML(h, Text, Comp, cls='standtable')
        h.write('</div>\n')
        # Spare effectiveness by combinations
        P.MostCommonLeaves()
        Pairs = sorted(P.Left.items(), key=lambda x: -x[1])
        count = 0
        Cols = 5
        h.write('<div class="container">\n')
        h.write('<h2 id="Common">Spare Effectiveness by Combination Left</h2>\n')
        h.write('<table class="sparetable" border="1">\n')
        h.write('<tbody>\n')
        h.write('<tr>\n')
        for (key, value) in Pairs:
            if count == Cols:
                h.write('</tr>\n</tbody>\n</table>\n')
                h.write('<table class="sparetable" border="1">\n<tbody>\n<tr>\n')
                count = 0
            h.write('<td>\n<center>\n')
            h.write('<p><img width = "100%" alt="" src="data:image/svg+xml;base64,' +
                    Spare_Effectiveness(key, P) + '" /></p>')
            # Spare_Effectiveness(key, P, debug = True)
            h.write('</center>\n</td>\n')
            count += 1

        svg_text = '<svg xmlns="http://www.w3.org/2000/svg" width="2500" height="2500" viewBox="0 0 8 8">'
        svg_text += '<rect width="8" height="8" style="fill:rgb(255,255,255);stroke:rgb(255,255,255)" /></svg>'
        encoded_string = b64encode(svg_text.encode('utf-8'))
        b64 = encoded_string.decode('utf-8')
        for x in range(count, 5):
            h.write('<td> <p><img width = "100%" alt="" src="data:image/svg+xml;base64,' +
                    b64 + '" /></p></td>')
            # h.write('<td> <p><img width = "100%" alt="" /></p> </td>\n')
        h.write('</tbody>\n</table>\n')
        h.write('</div>\n')
        # Section outputting frame-by-frame
        for G in P.Games:
            if G.Meta[2].date() != LastDate:
                if LastDate != '':
                    h.write('</tbody>\n</table>\n</div>\n')
                h.write('<div class="container">\n')
                h.write(
                    '<h2 id="{0}">Frame-by-frame {0}</h2>'.format(custom_strftime('{S} of %B, %Y', G.Meta[2].date())))
                h.write('<table class="frametable" border="1" id="report">\n<thead>\n')
                for i, j in zip(Span, Head):
                    h.write('<th colspan = "{0}"><center>{1}</center></th>\n'.format(i, j))
                h.write('</thead>\n<tbody>')
                h.write('<tr>\n')
                LastDate = G.Meta[2].date()
            else:
                h.write('<table class="frametable" border="1" id="report">\n<thead>\n')
                for i, j in zip(Span, Head):
                    h.write('<th colspan = "{0}"><center>{1}</center></th>\n'.format(i, j))
                h.write('</thead>\n<tbody>')
                h.write('<tr>\n')
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
                else:
                    h.write('<td colspan = "2"><center>\n')
                h.write('<p><img width = "100%" alt="" src="data:image/svg+xml;base64,' +
                        Pin_Position_Frame(Frame, G) + '" /></p>')
                h.write('</center></td>')
            h.write('</tr>\n</tbody>\n</table>\n')
        h.write('</tbody>\n</table>\n</div>\n')
        h.write('</body>\n</html>')
        h.close()
        options = {'margin-top': '0.75in',
                   'margin-right': '0in',
                   'margin-bottom': '0in',
                   'margin-left': '0in',
                   'header-html': r'C:\Users\Chris\Documents\League\Three Way\HTML\testhead.html'}
        config = pdfkit.configuration(wkhtmltopdf=bytes(r'C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe', 'utf-8'))
        css = [path + 'skeletonpdf.css']
        pdfkit.from_file(hfile, os.getcwd() + r'\HTML\Stats_{0}.pdf'.format(F),
                         configuration=config, css=css, options=options)
