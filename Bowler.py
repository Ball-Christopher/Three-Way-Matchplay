import math
from statistics import mean, StatisticsError


class Bowler:

    def GetSeries(self, Week):
        return(self.series[Week])

    def GetHSeries(self, Week):
        return(self.hseries[Week])

    def GetSeriesType(self, Week, Type):
        try:
            if Type == 'Scratch' and len(self.series[Week]) > 0: return (self.series[Week])
            if Type == 'Handicap' and len(self.hseries[Week]) > 0: return (self.hseries[Week])
        except:
            pass
        return([0])

    def __init__(self, name='', info=None, dispname='', Female=False):
        self.name = name
        self.dispname = name if dispname == '' else dispname.title()
        self.nameinit = name
        self.info = info
        self.SPoints = {}
        self.HPoints = {}
        self.avgs = {}
        self.hcps = {}
        self.series = {}
        self.hseries = {}
        self.PreBowled = {}
        self.Replace = {}
        self.OppScore = {}
        self.Games = {}
        self.Female = Female

    def HeaderInformation(self, week, lane, ID):
        return(['\\multicolumn{14}{l}{\\textbf{' +
                '{0} -- {1}   $\\quad$    Average = {2} $\\quad$    Handicap = {3} $\\quad$ Lane {4}'.format(
                        ID, self.dispname, self.GetAverage(week), self.GetHandicap(week), lane)+'}}'])

    def AddHighlight(self, Games, Points, Bold, Italic, BoldS, ItS):
        Out = []
        if len(Games) == 0:
            Out = ['\\textcolor{red}{----}' for i in range(len(Points))]
            return(Out)
        for G, P in zip(Games, Points):
            if P in Bold: Out.append('\\bf{'+ str(G) + '}')
            elif P in Italic: Out.append('\\it{'+ str(G) + '}')
            else: Out.append(str(G))
        if Points[-1] in BoldS: Out.append('\\bf{'+ str(sum(Games)) + '}')
        elif Points[-1] in ItS: Out.append('\\it{'+ str(sum(Games)) + '}')
        else: Out.append(str(sum(Games)))
        return(Out)

    def GetSummaryData(self, week, Type, Bold, Italic, BoldS, ItS):
        Data = [self.name, max(self.GetAverage(week),0)]
        if Type == 'Handicap': Data.append(self.GetHandicap(week))
        # Add Blind and Win/Loss highlighting here...
        if Type == 'Scratch':
            Data.extend(self.AddHighlight(self.GetSeries(week), self.SPoints[week], Bold, Italic, BoldS, ItS))
            #Data.extend(self.SPoints[week])
            Data.append(sum(self.SPoints[week]))
            #Data.append(sum(sum(v) for k,v in self.series.items() if k <= week))
        elif Type == 'Handicap':
            Data.extend(self.AddHighlight(self.GetHSeries(week), self.HPoints[week], Bold, Italic, BoldS, ItS))
            #Data.append(sum(self.GetHSeries(week)))
            Data.append(sum(self.HPoints[week]))
            #Data.append(sum(sum(v) for k,v in self.hseries.items() if k <= week))
        return(Data)

    def GetStandingsData(self, Count, Type, week,
                         path="https://dl.dropboxusercontent.com/u/90265306/Statistics/July%202016/"):
        # Modifications for prebowls, blinds and replaced...
        Points = self.SPoints if Type == 'Scratch' else self.HPoints
        Total_Points = sum(sum(v) for k,v in Points.items() if k <= week)
        Last_Points = sum(Points[week])
        Avg = self.GetAverage(week)
        Hcp = self.GetHandicap(week)
        Series = self.series if Type == 'Scratch' else self.hseries
        try:
            High_Game = max(max(v) for k,v in Series.items() if k <= week and len(v) > 0)
            High_Series = max(sum(v) for k,v in Series.items() if k <= week and len(v) > 0)
            Total_Pins = sum(sum(v) for k,v in Series.items() if k <= week and len(v) > 0)
        except ValueError:
            High_Game = 0
            High_Series = 0
            Total_Pins = 0
        # Added average against, always interesting
        try:
            AvgAgainst = mean(it for k,v in self.OppScore.items() if k <= week for it in v)
        except StatisticsError:
            AvgAgainst = 0
        if Type == 'Scratch':
            return ([Count,
                     '<a href="{2}Stats_{1}.pdf">{0}</a>'.format(
                         self.name, '_'.join(self.name.title().split()), path),
                     Total_Points, Last_Points,
                     Avg, High_Game, High_Series, Total_Pins, math.floor(AvgAgainst)])
        else:
            return ([Count,
                     '<a href={2}Stats_{1}.pdf">{0}</a>'.format(
                         self.name, '_'.join(self.name.title().split()), path),
                     Total_Points, Last_Points,
                     Avg, Hcp, High_Game, High_Series, Total_Pins])

    def IsReplaced(self, Week):
        try:
            return(self.Replace[Week])
        except KeyError:
            return(False)

    def IsPreBowl(self, Week):
        try:
            return(self.PreBowled[Week])
        except KeyError:
            return(False)

    def GetBowlerName(self):
        return(self.name)

    def GetBowlerDispName(self):
        return(self.dispname)

    def GetBowlerNameInit(self):
        return(self.nameinit)

    def SetBowlerDispName(self,name):
        self.dispname = name

    def SetBowlerNameInit(self,name):
        self.nameinit = name

    def GetHandicap(self,Week):
        return(self.hcps[Week])

    def AddSeries(self, Week, Series, HandicapInfo, Silent = 0):
        self.Games[Week] = len(Series)
        self.series[Week] = Series
        Temp = []
        Ind = False
        if Week in self.hcps.keys(): Temp = [G + self.hcps[Week] for G in Series]
        elif Week - 1 in self.hcps.keys(): Temp = [G + self.hcps[Week - 1] for G in Series]
        else: Ind = True
        HSeries = Temp[:]
        if Silent:
            pass
        else:
            self.hseries[Week] = HSeries
        [alpha, base, moving, minhandicap] = HandicapInfo
        self.avgs[Week] = mean(it for k,v in self.series.items() if k <= Week for it in v)
        self.hcps[Week] = math.floor(max(minhandicap, alpha / 100 * (base - math.floor(self.avgs[Week]))))
        if Week == 1: Ind = True
        try:
            self.hcps[Week-1]
        except KeyError:
            self.hcps[Week-1] = self.hcps[Week]
        if Ind:
            if Week == 1:
                Temp = []
                for i in Series:
                    Temp.append(i+self.hcps[Week])
                HSeries = Temp[:]
                if Silent:
                    pass
                else:
                    self.hseries[Week] = HSeries
            else:
                Temp = []
                for i in Series:
                    Temp.append(i+self.hcps[Week])
                self.hseries[Week] = Temp[:]
                print('Fail on book average for {0} in week {1}\n Possible replacement'.format(self.name, Week))

    def AddPoints(self, Week, Points, Type):
        if Type == 'Scratch':
            if Week in self.SPoints.keys():
                self.SPoints[Week] = [i+j for i,j in zip(self.SPoints[Week],Points)]
            else: self.SPoints[Week] = Points
        else:
            if Week in self.HPoints.keys():
                self.HPoints[Week] = [i+j for i,j in zip(self.HPoints[Week],Points)]
            else: self.HPoints[Week] = Points

    def GetPoints(self, Week, Type):
        if Type == 'Scratch':
            try:
                return(self.SPoints[Week])
            except KeyError:
                return([0])
        else:
            try:
                return(self.HPoints[Week])
            except KeyError:
                return([0])

    def EditPoints(self, Week, Scratch, Points):
        if Scratch:
            self.SPoints[Week] = Points
        else:
            self.HPoints[Week] = Points

    def GetAverage(self, Week):
        try:
            return(math.floor(self.avgs[Week]))
        except KeyError:
            return(-1)

    def GetExactAverage(self, Week):
        return(self.avgs[Week])

    def Blind(self, Week):
        if Week == 1 and Week - 1 not in self.avgs.keys():
            self.avgs[Week] = -1
            self.hcps[Week] = 0
            self.series[Week] = []
            self.hseries[Week] = []
            return
        self.avgs[Week] = self.avgs[Week - 1]
        self.hcps[Week] = self.hcps[Week - 1]
        self.series[Week] = []
        self.hseries[Week] = []

    def Replaced(self, Week):
        if Week == 1:
            self.avgs[Week] = -1
            self.hcps[Week] = 0
            self.series[Week] = []
            self.Replace[Week] = True #To be used for colouring in reports.
            return
        self.avgs[Week] = self.avgs[Week - 1]
        self.hcps[Week] = self.hcps[Week - 1]
        self.series[Week] = []
        self.Replace[Week] = True #To be used for colouring in reports.

    def PreBowl(self, Week):
        self.PreBowled[Week] = True

