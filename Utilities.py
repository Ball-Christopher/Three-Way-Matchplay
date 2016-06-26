import os

import pdfkit


def suffix(d):
    return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')


def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))


def WriteHTML(g, Data, TableParam, cls='u-full-width'):
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
        if cls == 'maintable' and Count % 3 == 0 and Count > 0:
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
            if Bold:
                g.write('<td style="font-weight:bold" {1}>{0}</td>'.format(el, Align))
            elif Italic:
                g.write('<td style="text-decoration: underline" {1}>{0}</td>'.format(el, Align))
            elif Red:
                g.write('<td style="color:red" {1}>{0}</td>'.format(el, Align))
            else:
                g.write('<td {1}>{0}</td>'.format(el, Align))
        g.write('</tr>\n')
    g.write('</tbody>\n</table>\n')


def WritePreambleHTML(g, week, Full=True, Script=False,
                      Leaguename='', BCenter='', dates=(), lanes=0):
    g.write('<!DOCTYPE html>\n<html lang="en">\n')
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
    g.write('</table></header>')
    g.write('<head>\n<meta charset="utf-8">\n')
    g.write('<title>{1} Week {0} Recap</title>'.format(week, Leaguename))
    g.write('<meta name="description" content="">\n<meta name="author" content="">\n')
    g.write('<meta name="viewport" content="width=device-width, initial-scale=1">\n')
    g.write('<link rel="stylesheet" href="css/skeleton.css">\n')
    if Script:
        pass
        '''
        g.write('<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js" type="text/javascript"></script>\n')
        g.write('<script type="text/javascript">\n')
        g.write('$(document).ready(function(){\n')
        g.write('$("#report tr:nth-child(3n+1)").addClass("odd");\n')
        g.write('$("#report tr:nth-child(3n+2)").addClass("odd");\n')
        g.write('$("#report tr:not(.odd)").hide();\n')
        g.write('$("#report tr:first-child").show();\n')
        g.write('$("#report tr.odd").click(function(){\n')
        g.write('$(this).next("tr").toggle();\n')
        g.write('$(this).find(".arrow").toggleClass("up");\n')
        g.write('});\n')
        g.write('//$("#report").jExpand();\n')
        g.write("});\n")
        g.write("</script>\n")
        '''
    g.write('</head>\n<body>\n')
    if Full:
        g.write('<div class="container">\n<div class="row">\n<div class="six columns" style="margin-top: 15%">')
        g.write('<h4>{0}</h4>'.format(BCenter))
        g.write('<h4>{0}</h4>'.format(Leaguename))
        g.write('<h4>Week {0}</h4>'.format(week))
        g.write('<h4>{0}</h4>'.format(dates[week - 1].strftime('6:45pm %A %d of %B, %Y')))
        g.write('</div>\n<div class="six columns" style="margin-top: 15%">\n<h4>On this page</h4>\n')
        g.write('<ol>\n<li><a href="#Standings-Handicap">Standings Handicap</a></li>\n')
        g.write('<li><a href="#Schedule-by-id">Schedule by ID</a></li>\n')
        g.write('<li><a href="#Schedule-by-name">Schedule by Name</a></li>\n')
        g.write('<li><a href="#LWHS">Last Week\'s High Scores</a></li>\n')
        g.write('<li><a href="#SHS">Season High Scores</a></li>\n')
        g.write('<li><a href="#LWBB">Last Week By Bowler</a></li>\n')
        g.write('</ol>\n</div>\n</div>\n</div>')
    g.write('<div class="container">\n<div class="row">\n<div class="twelve columns">\n')
    pass


def HTMLStatistics(DB, League):
    config = pdfkit.configuration(wkhtmltopdf=bytes(r'C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe', 'utf-8'))
    path = r'C:\Users\Chris\Documents\League\Three Way\HTML\css\\'
    css = [path + 'skeleton.css']
    for P in DB.Players:
        # Get the player's first name (assume unique for now)
        F = '_'.join(P.Name.title().split())
        hfile = os.getcwd() + '/HTML/Stats_{0}.html'.format(F)
        h = open(hfile, 'w')
        WritePreambleHTML(h, F, Full=False, Script=False)
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