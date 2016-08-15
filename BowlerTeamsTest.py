import datetime
import os
from operator import itemgetter

import pdfkit

from Bowler import *
from Utilities import WriteHTML, WritePreambleHTML, custom_strftime

'''
Author: Christopher Ball
Date Created: 24/01/2016

Purpose:
To simplify my horribly complicated scoring program for extension to
three-way match play.

Key Changes:
Uses HTML as the default output and converts from that to pdf using
import pdfkit
pdfkit.from_url('http://google.com', 'out.pdf')
No concept of teams, three-way matchplay is really an individual thing.
No more code for multiple rounds per week.

pdfkit and wkhtmltopdf underneath require true type font encoded into the css. See link below.
Font encoding http://blog.shaharia.com/use-google-web-fonts-for-wkhtmltopdf-tools-to-convert-html-to-pdf/
'''

class League:

    def CalculateWeeklyPoints(self, week):
        WeekSchedule = self.Schedule[week - 1]
        Num_To_Process = self.Pattern[week - 1]
        for Type in ('Scratch', 'Handicap'):
            for i in range(0, len(WeekSchedule), Num_To_Process):
                Bowlers = WeekSchedule[i:(i + Num_To_Process)]
                for B1 in Bowlers:
                    for B2 in Bowlers:
                        if B1 == B2: continue
                        self.CompareBowler(week, B1 - 1, B2 - 1, Type)

    def BlindCorrection(self, BowlerName, Week):
        #Update mappings
        self.NameToLocationMap()
        #Find bowler and assign blind.
        Bowler = self.League[self.NameLocationMap[BowlerName.lower()]]
        Bowler.Blind(Week)

    def Prebowl(self, BowlerName, Week):
        # Update mappings
        self.NameToLocationMap()
        # Find bowler and assign blind.
        Bowler = self.League[self.NameLocationMap[BowlerName.lower()]]
        Bowler.PreBowl(Week)

    def BlindRule(self, BowlerA, BowlerB, Week, Handicap = True):
        ''' Bowler A is the active player, Bowler B is blind'''
        # If blind in the first week or haven't started yet...
        if Handicap:
            return (self.base - 10)

        if BowlerB.GetAverage(Week - 1) <= 0:
            if BowlerA.GetAverage(Week - 1) <= 0:
                return BowlerA.GetAverage(Week) - 10
            BowlerA.GetAverage(Week - 1) - 10

        if BowlerA.GetAverage(Week - 1) >= 0:
            return (min(BowlerB.GetAverage(Week - 1) - 10, BowlerA.GetAverage(Week - 1) - 10))
        else:
            return (min(BowlerB.GetAverage(Week - 1) - 10, BowlerA.GetAverage(Week) - 10))
        pass

    def CompareBowler(self,Week,BowlerNumA,BowlerNumB,Type):
        # Find the bowlers
        BowlerA = self.League[BowlerNumA]
        BowlerB = self.League[BowlerNumB]
        # Get the series
        SeriesA = BowlerA.GetSeries(Week) if Type == 'Scratch' else BowlerA.GetHSeries(Week)
        # Make a correction if they are blind.
        if len(SeriesA) == 0:
            # Set points for the week to 0
            TempSPA = [self.PointsAllocated[Week]['GameL']]*self.games
            TempSPA.append(self.PointsAllocated[Week]['SerL'])
            BowlerA.AddPoints(Week, TempSPA, Type)
            return
        SeriesB = BowlerB.GetSeries(Week) if Type == 'Scratch' else BowlerB.GetHSeries(Week)
        # Blind correction for inactive player.
        BlindB = False
        if len(SeriesB) == 0:
            SeriesB = [self.BlindRule(BowlerA,BowlerB,Week,Handicap = not(Type == 'Scratch'))]*self.games
            BlindB = True
        else:
            if Type == 'Scratch':
                SeriesB = [Game + 8*BowlerB.Female for Game in SeriesB]
                try:
                    BowlerB.OppScore[Week].extend(BowlerA.GetSeries(Week))
                except KeyError:
                    BowlerB.OppScore[Week] = list(BowlerA.GetSeries(Week))
        # Modify for 8 pin bonus female
        if Type == 'Scratch' and not BlindB:
            SeriesA = [Game + 8*BowlerA.Female for Game in SeriesA]
        # Calculate the points for the week by game.
        TempSPA = [self.PointsAllocated[Week]['GameW'] if i > j else
                   (self.PointsAllocated[Week]['GameD'] if i == j else
                    self.PointsAllocated[Week]['GameL'])
                   for i, j in zip(SeriesA, SeriesB)]
        # Add the points for the series
        TempSPA.append(self.PointsAllocated[Week]['SerW'] if sum(SeriesA) > sum(SeriesB) else
                       (self.PointsAllocated[Week]['SerD'] if sum(SeriesA) == sum(SeriesB) else
                        self.PointsAllocated[Week]['SerL']))
        # Add the points to the bowler...
        BowlerA.AddPoints(Week, TempSPA, Type)

    def CompileStandings(self, Type, week):
        Out = []
        Scratch = True if Type == 'Scratch' else False
        for Bowler in self.League:
            Data = Bowler.GetStandingsData(self.League.index(Bowler) + 1, Type, week)
            Out.append(Data)
        #  Sort the data set by points then by total pins, possibility for improvement here...
        if Scratch: SortedOut = sorted(Out,key=itemgetter(2,7),reverse=True)
        else: SortedOut = sorted(Out,key=itemgetter(2,8),reverse=True)
        #  As list is sorted we can insert the position (assuming no ties). Fixed for ties under current system.
        #  Needs to be fixed to allow unusual tie breakers.
        Offset = 0 if Scratch else 1
        for i in range(len(SortedOut)):
            if i != 1 and SortedOut[i][2] == SortedOut[i-1][3] and SortedOut[i][7+Offset] == SortedOut[i-1][8+Offset]:
                SortedOut[i].insert(0,SortedOut[i-1][0])
            else: SortedOut[i].insert(0,i+1)
        return(Out, SortedOut)

    def Awards(self,Type,week):
        WeeklyHighG = [[Member.dispname, max(Member.GetSeriesType(week, Type))]
                       for Member in self.League if Member.name not in self.Exclude and
                       week in Member.Games.keys() and
                       not Member.IsPreBowl(week)]
        SeasonHighG = [[Member.dispname, max([max(Member.GetSeriesType(i, Type))
                                              for i in range(1, week + 1)
                                              if not Member.IsPreBowl(i)], default=0)]
                       for Member in self.League if Member.name not in self.Exclude]
        WeeklyHighS = [[Member.dispname, sum(Member.GetSeriesType(week, Type))]
                       for Member in self.League if Member.name not in self.Exclude and
                       week in Member.Games.keys() and
                       not Member.IsPreBowl(week)]
        SeasonHighS = [[Member.dispname, max([sum(Member.GetSeriesType(i, Type))
                                              for i in range(1, week + 1)
                                              if not Member.IsPreBowl(i)], default=0)]
                       for Member in self.League if Member.name not in self.Exclude]
        #  Extract to a data matrix that can be LaTeX'd
        DataSSG = self.SortByGroup(SeasonHighG, Type + ' Game')
        DataSSS = self.SortByGroup(SeasonHighS, Type + ' Series')
        DataWSG = self.SortByGroup(WeeklyHighG, Type + ' Game')
        DataWSS = self.SortByGroup(WeeklyHighS, Type + ' Series')
        #  Stick the components together
        DataSSG.extend(DataSSS)
        DataWSG.extend(DataWSS)
        return(DataSSG,DataWSG)

    def LaTeXWeekly(self, week, file = '', verbose=True):
        #  Must be called after calculate weekly points!!!! This could be added as a check later...
        #  First step get a data matrix together.
        if self.scratch: FinalS, Scratch = self.CompileStandings('Scratch',week)
        else:
            Scratch = None
        if self.handicap: FinalH,Handicap = self.CompileStandings('Handicap',week)
        else:
            Handicap = None
        #  Now for the weekly and season high scores for each team.
        IDataSS, IDataSG = self.Awards('Scratch', week)
        IDataHS, IDataHG = self.Awards('Handicap', week)
        #  Finally the team breakdown...
        BowlersDataScratch = []
        BowlersDataHandicap = []
        #We can get the team info from FinalS and FinalH
        for i in [el-1 for el in self.Schedule[week-1]]:
            #  Find reference to bowler information
            Member = self.League[i]
            #  Get header information for each bowler.
            Lane = 1
            BowlersDataScratch.append(Member.HeaderInformation(week, Lane, i + 1))
            BowlersDataHandicap.append(Member.HeaderInformation(week, Lane, i + 1))
            BowlersDataScratch.append(Member.GetSummaryData(week, 'Scratch',
                                                            [self.PointsAllocated[week]['GameD'] +
                                                             self.PointsAllocated[week]['GameW'],
                                                             2 * self.PointsAllocated[week]['GameW']],
                                                            [self.PointsAllocated[week]['GameD'],
                                                             self.PointsAllocated[week]['GameW']],
                                                            [self.PointsAllocated[week]['SerD'] +
                                                             self.PointsAllocated[week]['SerW'],
                                                             2 * self.PointsAllocated[week]['SerW']],
                                                            [self.PointsAllocated[week]['SerD'],
                                                             self.PointsAllocated[week]['SerW']]))
            BowlersDataHandicap.append(Member.GetSummaryData(week, 'Handicap',
                                                             [self.PointsAllocated[week]['GameD'] +
                                                              self.PointsAllocated[week]['GameW'],
                                                              2 * self.PointsAllocated[week]['GameW']],
                                                             [self.PointsAllocated[week]['GameD'],
                                                              self.PointsAllocated[week]['GameW']],
                                                             [self.PointsAllocated[week]['SerD'] +
                                                              self.PointsAllocated[week]['SerW'],
                                                              2 * self.PointsAllocated[week]['SerW']],
                                                             [self.PointsAllocated[week]['SerD'],
                                                              self.PointsAllocated[week]['SerW']]))
            if self.Schedule[week-1].index(i+1) % 2 == 1 and self.Schedule[week-1].index(i+1) != len(self.Schedule[week-1]):
                BowlersDataScratch.append(['\\midrule'])
                BowlersDataHandicap.append(['\\midrule'])
            continue

        #  Add the schedule
        SchedDataNam = self.SchedulePrint(week, 'Name')
        SchedDataNum = self.SchedulePrint(week, 'Num')
        try:
            SchedDataNam.extend(self.SchedulePrint(week + 1, 'Name'))
            SchedDataNum.extend(self.SchedulePrint(week + 1, 'Num'))
        except TypeError:
            pass

        #Now for the actual LaTeX output (the fun part)
        #Each section has a header (the blue part) with a title, a table header and table data (none of this stuff has midlines except Schedule).
        #Need optionals for line colouring and optional selection of various parameters.
        #Store the league reports in a specific league folder under the path.
        try:
            #file = os.getcwd()+'/TestOutput/MondaySingles_{2}_{1}_{0}.tex'.format(self.dates[week-1].day,self.dates[week-1].month,self.dates[week-1].year)
            gfile = os.getcwd()+r'\HTML\Week{0}RecapHandicap.html'.format(week)
            hfile = os.getcwd()+r'\HTML\Week{0}RecapScratch.html'.format(week)
            g = open(gfile, 'w')
            h = open(hfile, 'w')
        except IOError:
            #os.mkdir(os.getcwd()+'/TestOutput'.format(week,self.LeagueID))
            os.mkdir(os.getcwd() + r'\HTML')
            gfile = os.getcwd()+r'\HTML\Week{0}RecapHandicap.html'.format(week)
            hfile = os.getcwd()+r'\HTML\Week{0}RecapScratch.html'.format(week)
            g = open(gfile, 'w')
            h = open(hfile, 'w')
        #Write header to document if appropriate
        WritePreambleHTML(g, week, Full=False, Leaguename=self.Leaguename,
                          BCenter=self.BCenter, dates=self.dates, lanes=self.lanes, header = False)
        WritePreambleHTML(h, week, Full=False, Leaguename=self.Leaguename,
                          BCenter=self.BCenter, dates=self.dates, lanes=self.lanes, header = False)
        #Write end of document if appropriate
        Bowlers = self.Pattern[week - 1]
        h.write('<div class="container">\n<h2 id="Standings-Scratch">Standings Scratch</h2>\n')
        WriteHTML(h, Scratch, self.StScP, cls='standtable')
        h.write('</div>')
        g.write('<div class="container">\n<h2 id="Standings-Handicap">Standings Handicap</h2>\n')
        WriteHTML(g, Handicap, self.StHcP, cls='standtable')
        g.write('</div>')
        if self.byname:
            g.write('<div class="container">\n<h2 id="Schedule-by-name">Schedule by Name</h2>\n')
            WriteHTML(g, SchedDataNam, self.SchedNamP, cls='boldtable')
            g.write('</div>')
            h.write('<div class="container">\n<h2 id="Schedule-by-name">Schedule by Name</h2>\n')
            WriteHTML(h, SchedDataNam, self.SchedNamP, cls='boldtable')
            h.write('</div>')
        if self.handicap:
            g.write('<div class="container">\n<h2 id="LWHS">Last Week\'s Individual High Scores</h2>\n')
            WriteHTML(g, IDataHG, self.High, cls='idtable')
            g.write('</div>')
            g.write('<div class="container">\n<h2 id="SHS">Season Individual High Scores</h2>\n')
            WriteHTML(g, IDataHS, self.High, cls='idtable')
            g.write('</div>')
        if self.scratch:
            h.write('<div class="container">\n<h2 id="LWSS">Last Week\'s Individual High Scores</h2>\n')
            WriteHTML(h, IDataSG, self.High, cls='idtable')
            h.write('</div>')
            h.write('<div class="container">\n<h2 id="SSS">Season Individual High Scores</h2>\n')
            WriteHTML(h, IDataSS, self.High, cls='idtable')
            h.write('</div>')
            pass
        g.write('<div class="container">\n<h2 id="LWBB">Last Week By Bowler</h2>\n')
        h.write('<div class="container">\n<h2 id="LWBB">Last Week By Bowler</h2>\n')
        # Some basic cleaning before HTML processing
        BowlersH = [row for row in BowlersDataHandicap if len(row) > 1]
        for i, row in enumerate(BowlersH): row.insert(0, '' if i % self.Pattern[week - 1] != 0 else '{0}--{1}'.format(
            2 * (i // self.Pattern[week - 1]) + 1, 2 * (i // self.Pattern[week - 1] + 1)))
        WriteHTML(g, BowlersH, self.WRecapH, cls='maintable', line_skip=Bowlers, font_change=(Bowlers == 3))
        BowlersS = [row for row in BowlersDataScratch if len(row) > 1]
        for i, row in enumerate(BowlersS): row.insert(0, '' if i % self.Pattern[week - 1] != 0 else '{0}--{1}'.format(
            2 * (i // self.Pattern[week - 1]) + 1, 2 * (i // self.Pattern[week - 1] + 1)))
        WriteHTML(h, BowlersS, self.WRecap, cls='maintable', line_skip=Bowlers, font_change=(Bowlers == 3))
        g.write('</div>')
        h.write('</div>')
        h.write('</body>\n</html>')
        h.close()
        g.write('</body>\n</html>')
        g.close()
        # Convert to pdf
        # Configure the html to pdf software.
        config = pdfkit.configuration(wkhtmltopdf=bytes(r'C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe', 'utf-8'))
        path = r'C:\Users\Chris\Documents\League\Three Way\HTML\css\\'
        css = [path + 'skeletonpdf.css']
        options = {'margin-top': '0.5in',
                   'margin-right': '0in',
                   'margin-bottom': '0.2in',
                   'margin-left': '0in',
                   'header-html': r'C:\Users\Chris\Documents\League\Three Way\HTML\testhead.html'}
        pdfkit.from_file(gfile, os.getcwd()+r'\HTML\Week{0}RecapHandicap.pdf'.format(week),
                         configuration = config, css = css, options = options)
        pdfkit.from_file(hfile, os.getcwd()+r'\HTML\Week{0}RecapScratch.pdf'.format(week),
                         configuration = config, css = css, options = options)
        pass

    def CompleteSchedule(self):
        gfile = os.getcwd()+r'\HTML\Schedule.html'
        g = open(gfile, 'w')
        WritePreambleHTML(g, 1, Full=False, Leaguename=self.Leaguename,
                          BCenter=self.BCenter, dates=self.dates, lanes=self.lanes)
        SchedDataNum = [self.SchedulePrint(week, 'Num')[0] for week in range(1, self.weeklen + 1)]
        SchedDataNam = [self.SchedulePrint(week, 'Name')[0] for week in range(1, self.weeklen + 1)]
        g.write('<h2  id="Schedule-by-id">Schedule by ID</h2>\n')
        WriteHTML(g, SchedDataNum, self.SchedNumP, cls='idtable')
        g.write('<h2  id="Schedule-by-name">Schedule by Name</h2>\n')
        WriteHTML(g, SchedDataNam, self.SchedNamP, cls='boldtable')
        g.write('</div>\n</div>\n</div>\n</body>\n</html>')
        g.close()
        # Configure the html to pdf software.
        config = pdfkit.configuration(wkhtmltopdf=bytes(r'C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe', 'utf-8'))
        path = r'C:\Users\Chris\Documents\League\Three Way\HTML\css\\'
        css = [path + 'skeletonpdf.css']
        options = {'margin-top': '0in',
                   'margin-right': '0in',
                   'margin-bottom': '0in',
                   'margin-left': '0in'}
        pdfkit.from_file(gfile, os.getcwd()+r'\HTML\Schedule.pdf',
                         configuration = config, css = css, options = options)

    def AddHeader(self, file, week):
        file.write('<header>\n')
        file.write('<table style="border-bottom:1pt solid black; width: 100%;">\n')
        file.write('<tr> <td style="width:20%"> {0} </td> <td style="text-align:center; width=60%"> <h4> {1} </h4> </td> <td style="width:20%"> Week {2} </td> </tr>\n'.format(
            custom_strftime('{S} of %B, %Y', self.dates[week-1]), self.Leaguename, week))
        file.write('</table>\n<table style="width: 100%;">\n')
        file.write('<tr> <td style="width:20%"> {0} </td> <td style="text-align:center; width=60%"> {1} </td> <td style="width:20%"> Lanes 1 -- {2} </td> </tr>\n'.format(
            self.dates[week - 1].strftime('6:45pm %A'), self.BCenter, self.lanes))
        file.write('</table></header>')

    def SchedulePrint(self, week, Version):
        #  Pull together the schedule.
        if week - 1 >= len(self.Schedule):
            return
        SchedData = [['{0}/{1}/{2}'.format(self.dates[week-1].day,self.dates[week-1].month,self.dates[week-1].year)]]
        LaneCount = 0
        Count = 0
        TeamName = [Member.dispname for Member in self.League][:len(self.Schedule[week-1])]
        CurrentWeek = self.Schedule[week - 1]
        for i in range(0, len(CurrentWeek), self.Pattern[week - 1]):
            if LaneCount >= self.lanes:
                SchedData.append([''])
                Count += 1
                LaneCount = 0
                if Version == 'Name':
                    SchedData[Count].extend(
                        [' / '.join(TeamName[j - 1] for j in CurrentWeek[i:(i + self.Pattern[week - 1])])])
                else:
                    SchedData[Count].extend(['--'.join(str(j) for j in CurrentWeek[i:(i + self.Pattern[week - 1])])])
            else:
                if Version == 'Name':
                    SchedData[Count].extend(
                        [' / '.join(TeamName[j - 1] for j in CurrentWeek[i:(i + self.Pattern[week - 1])])])
                else:
                    SchedData[Count].extend(['--'.join(str(j) for j in CurrentWeek[i:(i + self.Pattern[week - 1])])])
                LaneCount += 2

        return(SchedData)

    def CompileHigh(self,Data,Title):
        #Used for compiling the high game and series info...
        DataMat = [[]]
        Count = 0
        for i in range(len(Data)):
            if i == 0:
                DataMat[Count] = [Data[i][2],Data[i][1]]
                Count += 1
                continue
            else:
                if Data[i][0] > Data[i-1][0]:
                    Count = 0
                    if Data[i][0] > 3:
                        break
                else:
                    Count += 1
            if Data[i][0] == 1:
                DataMat.extend([[Data[i][2],Data[i][1]]])
            elif Data[i][0] == 2:
                try:
                    if len(DataMat[Count]) == 2:
                        DataMat[Count].extend([Data[i][2],Data[i][1]])
                except IndexError:
                    DataMat.extend([['','',Data[i][2],Data[i][1]]])
            elif Data[i][0] == 3:
                try:
                    if len(DataMat[Count]) == 4:
                        DataMat[Count].extend([Data[i][2],Data[i][1]])
                except IndexError:
                    DataMat.extend([['','','','',Data[i][2],Data[i][1]]])
        for i in range(len(DataMat)):
            if i == 0:
                DataMat[i].insert(0,Title)
            else:
                DataMat[i].insert(0,'')
        return(DataMat)

    def SortByGroup(self, Series, Type):
        Series = sorted(Series, key=itemgetter(1), reverse=True)
        Count = 0
        for i in range(len(Series)):
            if i == 0:
                Series[i].insert(0,Count+1)
            elif Series[i][1] < Series[i-1][2]:
                Count += 1
                Series[i].insert(0,Count+1)
            else:
                Series[i].insert(0,Count+1)
        Series = self.CompileHigh(Series, Type)
        return(Series)

    def SetTotals(self,week,IWinP=2,IDrawP=1,ILossP=0,ISerW=4,ISerD=2,ISerL=0):
        # This needs to be included as a static unless you want to change it type approach.
        self.PointsAllocated[week] = {'GameW':IWinP, 'GameD':IDrawP, 'GameL':ILossP, 'SerW':ISerW, 'SerD':ISerD, 'SerL':ISerL}

    def SpaceDelimited(self,data,sep=','):
        temp = ''
        try:
            k = len(data)
        except TypeError:
            return(data)
        for i in range(k):
            temp += '{0}'.format(data[i])+sep
        return(temp)

    def __init__(self, n = 0):
        self.SPoints = {}  # Key is week, points per bowler per game.
        self.HPoints = {}
        self.PointsAllocated = {}
        self.Bowlers = []  # Bowler ID of every bowler who has bowled in the league.
        self.League = []  # All the bowlers currently in the league.
        self.Pattern = []

    def ScheduleDates(self,n):
        a = self.sdate
        temp = [a]
        for i in range(n+35):#Generate many more weeks than needed, so we can delete/modify weeks as necessary.
            temp.append(temp[-1]+datetime.timedelta(weeks=1))
        self.dates = temp

    def LeagueData(self, Lname='Unknown', BCenter='Unknown', day='Unknown', games=6, alpha=100,
                   base=200, moving=0, minhandicap = 0, lanes=12, byname=True, bynum=True,
                   scratch=True, handicap=True, sdate=None, weeklen=None):
        self.Excluded([])
        self.Leaguename = Lname
        self.BCenter = BCenter
        self.day = day
        self.games = games
        self.alpha = alpha
        self.base = base
        self.moving = moving
        self.minhandicap = minhandicap
        self.lanes = lanes
        self.byname = byname
        self.bynumber = bynum
        self.scratch = scratch
        self.handicap = handicap
        if sdate is None:
            self.sdate = datetime.date(2011,1,27)
        else:
            temp = sdate.split('/')
            self.sdate = datetime.date(int(temp[2]),int(temp[1]),int(temp[0]))
        self.weeklen = weeklen
        self.ScheduleDates(self.weeklen)
        for i in range(1, weeklen + 1): self.SetTotals(i)
        #Create the default table definition files.
        self.StScP = {'Names':['Place','ID','Name','Points','Points Last','Avg','High Game','High Series','Total Pins', 'Avg Against'],
                      'TParams':['l','l','l','l','b{0.05\\textwidth}','l','b{0.05\\textwidth}','b{0.05\\textwidth}','b{0.05\\textwidth}','b{0.05\\textwidth}'],
                      'HeadFormatB':['{\\tiny{\\bf ']*10,'HeadFormatE':['}}']*10,'Size':-1,'Guide':True,'TwoColumn':False}
        self.StHcP = {'Names':['Place','ID','Name','Points','Points Last','Avg','Hdcp','High Game','High Series','Total Pins'],'TParams':['l','l','l','l','b{0.05\\textwidth}','l','l','b{0.05\\textwidth}','b{0.05\\textwidth}','b{0.05\\textwidth}'],
                      'HeadFormatB':['{\\tiny{\\bf ']*10,'HeadFormatE':['}}']*10,'Size':-1,'Guide':True,'TwoColumn':False}
        Name = ['Lane']
        for i in range(0,self.lanes,2):
            Name.append('{0}--{1}'.format(i+1,i+2))
        self.SchedNumP = {'Names':Name,'TParams':['l']*(math.ceil(self.lanes/2)+1),
                          'HeadFormatB':['{\\tiny{\\bf ']*10,'HeadFormatE':['}}']*10,'Size':-1,'Guide':True,'TwoColumn':False}
        self.SchedNamP = {'Names':Name,'TParams':['l']*(math.ceil(self.lanes/2)+1),
                          'HeadFormatB':['{\\tiny{\\bf ']*10,'HeadFormatE':['}}']*10,'Size':-4,'Guide':True,'TwoColumn':False}
        TempS = ['Week','Date','Name','Avg','Total Pins','High Game','High Series','Series','Points']
        TempWS = ['Lanes', 'Name', 'New Avg', 'Series', 'Points']
        TempWSH = ['Lanes', 'Name', 'New Avg', 'New Hcap', 'Hcap Series', 'Hcap Points']
        TempH = ['Week','Date','Name','Avg','Hcap','Total Pins','High Game','High Series','Series','Points']
        TempPS = ['l','l','l','l''b{0.05\\textwidth}','b{0.05\\textwidth}','b{0.05\\textwidth}','l','l']
        TempPWS = ['l','b{0.03\\textwidth}','b{0.03\\textwidth}','b{0.03\\textwidth}','b{0.05\\textwidth}','b{0.055\\textwidth}','b{0.05\\textwidth}','b{0.04\\textwidth}','b{0.05\\textwidth}','b{0.05\\textwidth}']
        TempPWSH = ['l','b{0.03\\textwidth}','b{0.03\\textwidth}','b{0.05\\textwidth}','b{0.055\\textwidth}','b{0.05\\textwidth}','b{0.05\\textwidth}','b{0.05\\textwidth}']
        TempPH = ['l','l','l','l','l','b{0.05\\textwidth}','b{0.05\\textwidth}','b{0.05\\textwidth}','l','l']
        for i in range(self.games):
            TempS.insert(7+i,'-{0}-'.format(i+1))
            TempPS.insert(7+i,'c')
            TempPWS.insert(4+i,'c')
            TempPWSH.insert(3+i,'c')
            TempH.insert(8+i,'-{0}-'.format(i+1))
            TempPH.insert(8+i,'c')
        for i in range(self.games):
            TempWS.insert(3+i, '-G{0}-'.format(i+1))
            TempWSH.insert(4+i,'-{0}-'.format(i+1))
            TempPWSH.insert(8+i,'c')
        self.TScB = {'Names':TempS,
                     'TParams':TempPS,
                     'HeadFormatB':['{\\tiny{\\bf ']*(9+self.games),'HeadFormatE':['}}']*(9+self.games),'Size':-2,'Guide':True,'TwoColumn':False}
        self.WRecap = {'Names':TempWS,
                       'TParams':TempPWS,
                       'HeadFormatB':['{\\tiny{\\bf ']*(10+self.games),'HeadFormatE':['}}']*(10+self.games),'Size':-3,'Guide':True,'TwoColumn':False}
        self.WRecapH = {'Names':TempWSH,
                        'TParams':TempPWSH,
                        'HeadFormatB':['{\\tiny{\\bf ']*(8+2*self.games),'HeadFormatE':['}}']*(8+2*self.games),'Size':-3,'Guide':True,'TwoColumn':False}
        self.THcB = {'Names':TempH,
                     'TParams':TempPH,
                     'HeadFormatB':['{\\tiny{\\bf ']*(10+self.games),'HeadFormatE':['}}']*(10+self.games),'Size':-2,'Guide':True,'TwoColumn':False}
        #Table files for the high weekly and season scores
        self.High = {'Names':[],'TParams':['l','r','p{0.2\\textwidth}','r','p{0.2\\textwidth}','r','p{0.2\\textwidth}'],
                     'HeadFormatB':[],'HeadFormatE':[],'Size':-2,'Guide':False,'TwoColumn':False}

    def AddNewBowler(self, name, dispname, Female = False):
        Temp = Bowler(name, dispname = dispname, Female = Female)
        self.League.append(Temp)
        self.NameToLocationMap()

    def GetHandicapInfo(self):
        return([self.alpha, self.base, self.moving, self.minhandicap])

    def NameToLocationMap(self):
        self.NameLocationMap = {}
        for i in self.League:
            self.NameLocationMap[i.GetBowlerName().lower()] = self.League.index(i)
            self.NameLocationMap[i.GetBowlerDispName().lower()] = self.League.index(i)

    def AddSeries(self, BowlerName, Week, *Series):
        Bowler = self.League[self.NameLocationMap[BowlerName.lower()]]
        Bowler.AddSeries(Week, Series, self.GetHandicapInfo())

    def AddSeriesS(self, BowlerName, Week, *Series):
        Bowler = self.League[self.NameLocationMap[BowlerName.lower()]]
        Bowler.AddSeries(Week, Series, self.GetHandicapInfo(),Silent=1)

    def ListToCSVFormat(self,List,depth=1):
        Temp = ''
        if depth == 2:
            for i in List:
                for j in i:
                    Temp += str(j)+','
            return(Temp)
        else:
            for i in List:
                Temp += str(i)+','
            return(Temp)

    def Excluded(self,Names):
        self.Exclude = Names

    def AddSchedule(self, Schedule):
        self.Schedule = Schedule

if __name__ == '__main__':
    # Declare league object
    New_League = League(n = 3)
    # Add league data
    New_League.LeagueData(weeklen = 10)
    # Create a league schedule
    Schedule = [[1,2,3],[3,2,1]]
    # Add schedule to league
    New_League.AddSchedule(Schedule)
    # Create and add bowlers to league
    Names = ['Art', 'Bob', 'Chris']
    for Name in Names:
        New_League.AddNewBowler(Name, Name)

    # Add scores for week 1
    New_League.AddSeries('Art', 1, 100, 100, 100, 100, 100, 100)  # Art {1: [1, 0, 2, 1, 0, 0, 0]}
    New_League.AddSeries('Bob', 1, 200, 150, 100, 100, 150, 200)  # Bob {1: [4, 3, 2, 1, 2, 3, 4]}
    New_League.AddSeries('Chris', 1, 100, 150, 100, 200, 250, 200)  # Chris {1: [1, 3, 2, 4, 4, 3, 8]}

    # Calculate Weekly Scores
    New_League.CalculateWeeklyPoints(1)

    # Check the points for all of the bowlers
    for B in New_League.League:
        print(B.name, B.SPoints)

    # Print HTML report for the week...
    New_League.LaTeXWeekly(1)