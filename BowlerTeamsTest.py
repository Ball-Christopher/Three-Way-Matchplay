import math
import datetime
import os
from Bowler import *
from random import *
from operator import itemgetter, attrgetter
import pdfkit
import csv as csv

def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))
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
        WeekSchedule = self.Schedule[week-1]
        for Type in ('Scratch', 'Handicap'):
            for i in range(len(WeekSchedule)):
                if i % 3 == 0:
                    self.CompareBowler(week,WeekSchedule[i]-1,WeekSchedule[i+1]-1,Type)
                    self.CompareBowler(week,WeekSchedule[i]-1,WeekSchedule[i+2]-1,Type)
                elif i % 3 == 1:
                    self.CompareBowler(week,WeekSchedule[i]-1,WeekSchedule[i-1]-1,Type)
                    self.CompareBowler(week,WeekSchedule[i]-1,WeekSchedule[i+1]-1,Type)
                elif i % 3 == 2:
                    self.CompareBowler(week,WeekSchedule[i]-1,WeekSchedule[i-2]-1,Type)
                    self.CompareBowler(week,WeekSchedule[i]-1,WeekSchedule[i-1]-1,Type)

    def BackdateHandicap(self,NumWeeks,CurrentWeek):
        #Only use after the number of weeks played is suitable for backdating.
        for Bowler in self.League:
            try:
                Handicap = Bowler.GetHandicap(self.LeagueID,CurrentWeek)
                for j in range(NumWeeks):
                    Bowler.hcps[self.LeagueID,CurrentWeek-j-1] = Handicap
            except KeyError:
                pass

    def BackdateBowlerHandicap(self,Name,NumWeeks,CurrentWeek):
        #Backdate the handicap for an individual bowler.
        Bowler = ''
        for i in self.League:
            if i.GetBowlerName()==Name:
                Bowler = i
        try:
            Handicap = Bowler.GetHandicap(self.LeagueID,CurrentWeek)
            for j in range(NumWeeks):
                Bowler.hcps[self.LeagueID,CurrentWeek-j-1] = Handicap
        except KeyError:
            pass

    def ReplaceBowler(self,OldBowler,NewBowler,Week):
        #Update mappings
        self.NameToTeamMap()
        self.NameToLocationMap()
        #Find team of the replaced bowler
        Team = self.NameTeamMap[OldBowler]
        #Add replacing bowler to the team
        self.AddBowlerToTeam(Team[0],self.League[self.NameLocationMap[NewBowler]].GetBowlerID())
        #Update team order for the week in question
        if self.RPW == 1:
            self.teamorder[Team[0],Week][self.TeamMap[Team[0]].index(self.NameLocationMap[OldBowler])] = self.TeamMap[Team[0]].index(self.NameLocationMap[NewBowler])
        else:
            for j in range(self.RPW):
                self.teamorder[Team[0],Week,j+1][self.TeamMap[Team[0]].index(self.NameLocationMap[OldBowler])] = self.TeamMap[Team[0]].index(self.NameLocationMap[NewBowler])
        #Update bowler averages, etc
        Bowler = self.League[self.NameLocationMap[OldBowler]]
        Bowler.Replaced(self.LeagueID,Week)

    def PermanentReplaceBowler(self,OldBowler,NewBowler,Week):
        ''' Still need to add change to the team mapping for name and make this consistently follow through the program.
            Also need to update the replaced bowler so he could replace other bowlers later in the season'''
        #Update mappings
        self.NameToTeamMap()
        self.NameToLocationMap()
        #Find team of the replaced bowler
        Team = self.NameTeamMap[OldBowler]
        #Add replacing bowler to the team
        self.AddBowlerToTeam(Team[0],self.League[self.NameLocationMap[NewBowler]].GetBowlerID())
        #Update team order for the week in question
        Bowler = self.League[self.NameLocationMap[OldBowler]]
        for week in range(Week,self.weeklen):
            self.teamorder[Team[0],week][self.TeamMap[Team[0]].index(self.NameLocationMap[OldBowler])] = self.TeamMap[Team[0]].index(self.NameLocationMap[NewBowler])
            Bowler.Replaced(self.LeagueID,week)

    def BlindCorrection(self,BowlerName,Week):
        #Update mappings
        self.NameToLocationMap()
        #Find bowler and assign blind.
        Bowler = self.League[self.NameLocationMap[BowlerName]]
        Bowler.Blind(Week)

    def PreBowl(self,BowlerName,Week):
        #Update mappings
        self.NameToTeamMap()
        self.NameToLocationMap()
        #Find bowler and assign blind.
        Bowler = self.League[self.NameLocationMap[BowlerName]]
        Bowler.PreBowl(self.LeagueID,Week)

    def BlindRule(self, BowlerA, BowlerB, Week, Handicap = True):
        ''' Bowler A is the active player, Bowler B is blind'''
        if Handicap:
            return(self.base - 10)
        # If blind in the first week or haven't started yet...
        if BowlerB.GetAverage(Week - 1) < 0:
            if BowlerA.GetAverage(Week) < 0:
                return(0)
            return(BowlerA.GetAverage(max(Week - 1, 1)) - 10)

        if BowlerA.GetAverage(Week - 1) > 0:
            print(BowlerA.name, BowlerB.name, BowlerB.avgs)
            return(min(BowlerB.GetAverage(Week - 1), BowlerA.GetAverage(Week - 1) - 10))
        else:
            return(min(BowlerB.GetAverage(Week - 1),BowlerA.GetAverage(Week) - 10))
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
        if len(SeriesB) == 0:
            SeriesB = [self.BlindRule(BowlerA,BowlerB,Week,Handicap = not(Type == 'Scratch'))]*self.games
            BlindB = True
        else:
            if Type == 'Scratch':
                SeriesB = [Game + 8*BowlerB.Female for Game in SeriesB]
                BlindB = False
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
                       for Member in self.League if Member.name not in self.Exclude and week in Member.Games.keys()]
        SeasonHighG = [[Member.dispname, max(max(Member.GetSeriesType(i, Type)) for i in range(1, week + 1))]
                       for Member in self.League if Member.name not in self.Exclude]
        WeeklyHighS = [[Member.dispname, sum(Member.GetSeriesType(week, Type))]
                       for Member in self.League if Member.name not in self.Exclude and week in Member.Games.keys()]
        SeasonHighS = [[Member.dispname, max(sum(Member.GetSeriesType(i, Type)) for i in range(1, week + 1))]
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
        if self.handicap: FinalH,Handicap = self.CompileStandings('Handicap',week)
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
            BowlersDataScratch.append(Member.GetSummaryData(week, 'Scratch'))
            BowlersDataHandicap.append(Member.GetSummaryData(week, 'Handicap'))
            if self.Schedule[week-1].index(i+1) % 2 == 1 and self.Schedule[week-1].index(i+1) != len(self.Schedule[week-1]):
                BowlersDataScratch.append(['\\midrule'])
                BowlersDataHandicap.append(['\\midrule'])
            continue

        #  Add the schedule
        SchedDataNam = self.SchedulePrint(week, 'Name')
        SchedDataNam.extend(self.SchedulePrint(week + 1, 'Name'))
        SchedDataNum = self.SchedulePrint(week, 'Num')
        SchedDataNum.extend(self.SchedulePrint(week + 1, 'Num'))

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
        self.WritePreambleHTML(g, week, Full = False)
        self.WritePreambleHTML(h, week, Full = False)
        #Write end of document if appropriate
        h.write('<h2 id="Standings-Scratch">Standings Scratch</h2>\n')
        self.WriteHTML(h, Scratch, self.StScP, cls = 'standtable')
        g.write('<h2 id="Standings-Handicap">Standings Handicap</h2>\n')
        self.WriteHTML(g, Handicap, self.StHcP, cls = 'standtable')
        g.write('<h2  id="Schedule-by-id">Schedule by ID</h2>\n')
        self.WriteHTML(g, SchedDataNum, self.SchedNumP, cls = 'idtable')
        h.write('<h2  id="Schedule-by-id">Schedule by ID</h2>\n')
        self.WriteHTML(h, SchedDataNum, self.SchedNumP, cls = 'idtable')
        if self.byname:
            g.write('<h2  id="Schedule-by-name">Schedule by Name</h2>\n')
            self.WriteHTML(g, SchedDataNam, self.SchedNamP, cls = 'boldtable')
            h.write('<h2  id="Schedule-by-name">Schedule by Name</h2>\n')
            self.WriteHTML(h, SchedDataNam, self.SchedNamP, cls = 'boldtable')
        if self.handicap:
            g.write('<h2 id="LWHS">Last Week\'s Individual High Scores</h2>\n')
            self.WriteHTML(g, IDataHG, self.High, cls = 'idtable')
            g.write('<h2 id="SHS">Season Individual High Scores</h2>\n')
            self.WriteHTML(g, IDataHS, self.High, cls = 'idtable')
        if self.scratch:
            h.write('<h2 id="LWSS">Last Week\'s Individual High Scores</h2>\n')
            self.WriteHTML(h, IDataSG, self.High, cls = 'idtable')
            h.write('<h2 id="SSS">Season Individual High Scores</h2>\n')
            self.WriteHTML(h, IDataSS, self.High, cls = 'idtable')
            pass
        g.write('<div style="page-break-inside:avoid;">')
        h.write('<div style="page-break-inside:avoid;">')
        self.AddHeader(g, week)
        self.AddHeader(h, week)
        g.write('<h2 id="LWBB">Last Week By Bowler</h2>\n')
        h.write('<h2 id="LWBB">Last Week By Bowler</h2>\n')
        # Some basic cleaning before HTML processing
        BowlersH = [row for row in BowlersDataHandicap if len(row) > 1]
        for i,row in enumerate(BowlersH): row.insert(0, '' if i % 3 != 0 else '{0}--{1}'.format(2*(i//3)+1, 2*(i//3+1)))
        self.WriteHTML(g, BowlersH, self.WRecapH, cls = 'maintable')
        BowlersS = [row for row in BowlersDataScratch if len(row) > 1]
        for i,row in enumerate(BowlersS): row.insert(0, '' if i % 3 != 0 else '{0}--{1}'.format(2*(i//3)+1, 2*(i//3+1)))
        self.WriteHTML(h, BowlersS, self.WRecap, cls = 'maintable')
        g.write('</div>')
        h.write('</div>')
        h.write('</div>\n</div>\n</div>\n</body>\n</html>')
        h.close()
        g.write('</div>\n</div>\n</div>\n</body>\n</html>')
        g.close()
        # Convert to pdf
        # Configure the html to pdf software.
        config = pdfkit.configuration(wkhtmltopdf=bytes(r'C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe', 'utf-8'))
        path = r'C:\Users\Chris\Documents\League\Three Way\HTML\css\\'
        css = [path + 'skeletonpdf.css']
        options = {'margin-top': '0in',
                   'margin-right': '0in',
                   'margin-bottom': '0in',
                   'margin-left': '0in',
                   'footer-right': '[page]'}
        pdfkit.from_file(gfile, os.getcwd()+r'\HTML\Week{0}RecapHandicap.pdf'.format(week),
                         configuration = config, css = css, options = options)
        pdfkit.from_file(hfile, os.getcwd()+r'\HTML\Week{0}RecapScratch.pdf'.format(week),
                         configuration = config, css = css, options = options)
        pass

    def CompleteSchedule(self):
        gfile = os.getcwd()+r'\HTML\Schedule.html'
        g = open(gfile, 'w')
        self.WritePreambleHTML(g, 1, Full = False)
        SchedDataNum = [self.SchedulePrint(week, 'Num')[0] for week in range(1, self.weeklen + 1)]
        SchedDataNam = [self.SchedulePrint(week, 'Name')[0] for week in range(1, self.weeklen + 1)]
        g.write('<h2  id="Schedule-by-id">Schedule by ID</h2>\n')
        self.WriteHTML(g, SchedDataNum, self.SchedNumP, cls = 'idtable')
        g.write('<h2  id="Schedule-by-name">Schedule by Name</h2>\n')
        self.WriteHTML(g, SchedDataNam, self.SchedNamP, cls = 'boldtable')
        g.write('</div>\n</div>\n</div>\n</body>\n</html>')
        g.close()
        # Configure the html to pdf software.
        config = pdfkit.configuration(wkhtmltopdf=bytes(r'C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe', 'utf-8'))
        path = r'C:\Users\Chris\Documents\League\Three Way\HTML\css\\'
        css = [path + 'skeletonpdf.css']
        options = {'margin-top': '0in',
                   'margin-right': '0in',
                   'margin-bottom': '0in',
                   'margin-left': '0in',
                   'footer-right': '[page]'}
        pdfkit.from_file(gfile, os.getcwd()+r'\HTML\Schedule.pdf',
                         configuration = config, css = css, options = options)

    def AddHeader(self, file, week):
        file.write('<header>\n')
        file.write('<table style="border-bottom:1pt solid black; width: 100%;">\n')
        file.write('<tr> <td style="width:20%"> {0} </td> <td style="text-align:center; width=60%"> <h4> {1} </h4> </td> <td style="width:20%"> Week {2} </td> </tr>\n'.format(
            custom_strftime('{S} of %B, %Y', self.dates[week-1]), self.Leaguename, week))
        file.write('</table>\n<table style="width: 100%;">\n')
        file.write('<tr> <td style="width:20%"> {0} </td> <td style="text-align:center; width=60%"> {1} </td> <td style="width:20%"> Lanes 1 -- {2} </td> </tr>\n'.format(
            self.dates[week-1].strftime('7:00pm %A'), self.BCenter, self.lanes))
        file.write('</table></header>')

    def SchedulePrint(self, week, Version):
        #  Pull together the schedule.
        SchedData = [['{0}/{1}/{2}'.format(self.dates[week-1].day,self.dates[week-1].month,self.dates[week-1].year)]]
        LaneCount = 0
        Count = 0
        TeamName = [Member.dispname for Member in self.League][:len(self.Schedule[week-1])]
        CurrentWeek = self.Schedule[week - 1]
        for i in range(0, len(CurrentWeek), 3):
            if LaneCount >= self.lanes:
                SchedData.append([''])
                Count += 1
                LaneCount = 0
                if Version == 'Name':
                    SchedData[Count].extend(['{0} / {1} / {2}'.format(
                            TeamName[CurrentWeek[i]-1], TeamName[CurrentWeek[i+1]-1], TeamName[CurrentWeek[i+2]-1])])
                else:
                    SchedData[Count].extend(['{0}--{1}--{2}'.format(
                            CurrentWeek[i], CurrentWeek[i+1], CurrentWeek[i+2])])
            else:
                if Version == 'Name':
                    SchedData[Count].extend(['{0} / {1} / {2}'.format(
                            TeamName[CurrentWeek[i]-1], TeamName[CurrentWeek[i+1]-1], TeamName[CurrentWeek[i+2]-1])])
                else:
                    SchedData[Count].extend(['{0}--{1}--{2}'.format(
                            CurrentWeek[i], CurrentWeek[i+1], CurrentWeek[i+2])])
                LaneCount += 2
        return(SchedData)

    def WriteHTML(self, g, Data, TableParam, cls = 'u-full-width'):
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
                    el = el.replace(r'\bf','')
                else:
                    Bold = False
                if el.count(r'\it') > 0:
                    Italic = True
                    el = el.replace(r'\it','')
                else:
                    Italic = False
                if el.count(r'\textcolor{red}{') > 0:
                    Red = True
                    el = el.replace(r'\textcolor{red}{','')
                else:
                    Red = False
                for Con in ('{','}'):
                    el = el.replace(Con,'')
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

    def WritePreambleHTML(self, g, week, Full=True, Local=False):
        g.write('<!DOCTYPE html>\n<html lang="en">\n')
        g.write('<header>\n')
        g.write('<table style="border-bottom:1pt solid black; width: 100%;">\n')
        g.write('<tr> <td style="width:20%"> {0} </td> <td style="text-align:center; width=60%"> <h4> {1} </h4> </td> <td style="width:20%"> Week {2} </td> </tr>\n'.format(
            custom_strftime('{S} of %B, %Y', self.dates[week-1]), self.Leaguename, week))
        g.write('</table>\n<table style="width: 100%;">\n')
        g.write('<tr> <td style="width:20%"> {0} </td> <td style="text-align:center; width=60%"> {1} </td> <td style="width:20%"> Lanes 1 -- {2} </td> </tr>\n'.format(
            self.dates[week-1].strftime('7:00pm %A'), self.BCenter, self.lanes))
        g.write('</table></header>')
        g.write('<head>\n<meta charset="utf-8">\n')
        g.write('<title>{1} Week {0} Recap</title>'.format(week, self.Leaguename))
        g.write('<meta name="description" content="">\n<meta name="author" content="">\n')
        g.write('<meta name="viewport" content="width=device-width, initial-scale=1">\n')
        g.write('<link rel="stylesheet" href="css/skeleton.css">\n')
        #g.write('<link href="//fonts.googleapis.com/css?family=Raleway:400,300,600" rel="stylesheet" type="text/css">\n')
        # if Local:
        #     g.write('<link rel="stylesheet" href="css/normalize.css">\n')
        #     g.write('<link rel="stylesheet" href="css/skeleton.css">\n')
        # else:
        #     g.write('<link rel="stylesheet" href="https://dl.dropboxusercontent.com/u/90265306/HTML/css/normalize.css">\n')
        #     g.write('<link rel="stylesheet" href="https://dl.dropboxusercontent.com/u/90265306/HTML/css/skeleton.css">\n')
        # g.write('<link rel="icon" type="image/png" href="images/favicon.png">\n')
        g.write('</head>\n<body>\n')
        if Full:
            g.write('<div class="container">\n<div class="row">\n<div class="six columns" style="margin-top: 15%">')
            g.write('<h4>{0}</h4>'.format(self.BCenter))
            g.write('<h4>{0}</h4>'.format(self.Leaguename))
            g.write('<h4>Week {0}</h4>'.format(week))
            g.write('<h4>{0}</h4>'.format(self.dates[week-1].strftime('7:00pm %A %d of %B, %Y')))
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

    def GetTeamNamesNumber(self,TName,Week):
        CTeamNames = []
        for i in range(self.Teams):
            #Find team name for the week in question
            TeamNames = self.teamnames[i]
            for j in range(0,len(TeamNames),2):
                if Week >= TeamNames[j]:
                    index = j+1
            CTeamNames.append(TeamNames[index])
        return(CTeamNames.index(TName))

    def ScheduleDates(self,n):
        a = self.sdate
        temp = [a]
        for i in range(n+35):#Generate many more weeks than needed, so we can delete/modify weeks as necessary.
            temp.append(temp[-1]+datetime.timedelta(weeks=1))
        self.dates = temp

    def LeagueData(self, Lname='Unknown', BCenter='Unknown', day='Unknown', games=6, alpha=100,
                   base=200, moving=0, minhandicap = 0, lanes=12, byname=True, bynum=True,
                   scratch=True, handicap=True, sdate=[], weeklen=[]):
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
        if sdate == []:
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
            self.NameLocationMap[i.GetBowlerName()] = self.League.index(i)
            self.NameLocationMap[i.GetBowlerDispName()] = self.League.index(i)

    def NameToTeamMap(self):
        self.NameTeamMap = {}
        for i in range(len(self.League)):
            for j in self.TeamMap.keys():
                for k in self.TeamMap[j]:
                    if k==i:
                        try:
                            self.NameTeamMap[self.League[i].GetBowlerName()].append(j)
                        except KeyError:
                            self.NameTeamMap[self.League[i].GetBowlerName()] = [j]

    def AddSeries(self, BowlerName, Week, *Series):
        Bowler = self.League[self.NameLocationMap[BowlerName]]
        Bowler.AddSeries(Week, Series, self.GetHandicapInfo())

    def AddSeriesS(self, BowlerName, Week, *Series):
        Bowler = self.League[self.NameLocationMap[BowlerName]]
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
        New_League.AddNewBowler(Name)

    # Add scores for week 1
    New_League.AddSeries('Art', 1, 100, 100, 100, 100, 100, 100)  # Art {1: [1, 0, 2, 1, 0, 0, 0]}
    New_League.AddSeries('Bob', 1, 200, 150, 100, 100, 150, 200)  # Bob {1: [4, 3, 2, 1, 2, 3, 4]}
    New_League.AddSeries('Chris', 1, 100, 150, 100, 200, 250, 200)  # Chris {1: [1, 3, 2, 4, 4, 3, 8]}

    # Calculate Weekly Scores
    New_League.CalculateWeeklyPoints(1)

    # Check the points for all of the bowlers
    for Bowler in New_League.League:
        print(Bowler.name, Bowler.SPoints)

    # Print HTML report for the week...
    New_League.LaTeXWeekly(1)