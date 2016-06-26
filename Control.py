'''
Author: Christopher Ball
Create Date: 29/01/2016

Purpose: To control the three-way league running
at North City Tenpin.
'''
import numpy as np
import pandas as pd

from BowlerTeamsTest import *


class Game:
    def __init__(self, FS, Meta, FbF, Name):
        self.FS = FS
        self.Meta = Meta.copy()
        self.raw = FbF
        self.Left = {}
        self.Spared = {}
        self.PinPos = {}
        self.Name = Name
        self.NormalScore = []
        self.ProcessRaw()

    def LaneStat(self, Lane):
        if Lane == self.Meta[0]:
            # Get 1st, 3rd, etc
            Strikes = sum(1 for Shot in self.Frames[::4][:5] if Shot == 10)
            Spares = sum(1 for (Shot, Spare) in zip(self.Frames[::4][:5], self.Frames[1::4][:5]) if
                         Shot != 10 and Shot + Spare == 10)
            SpareAttempts = 5 - Strikes
            First = [self.PinPos[Shot][0] for Shot in self.PinPos.keys() if Shot in (1, 3, 5, 7, 9)]
            Splits = sum(self.SplitFrames[::2])
            return (Strikes, 5, Spares, SpareAttempts, First, Splits)
        elif (Lane % 2 == 1 and Lane == self.Meta[0] - 1) or (Lane % 2 == 0 and Lane == self.Meta[0] + 1):
            # Only gets first shot of the 10th...
            Frames = self.Frames[2::4][:5]
            FramesS = self.Frames[3::4][:5]
            if Frames[-1] == 10:
                Frames.extend(self.Frames[20::2])
                FramesS.append(self.Frames[21])
            elif Frames[-1] + FramesS[-1] == 10:
                Frames.append(self.Frames[20])
            Strikes = sum(1 for Shot in Frames if Shot == 10)
            FirstShots = len(Frames)
            Spares = sum(1 for (Shot, Spare) in zip(Frames, FramesS) if Shot != 10 and Shot + Spare == 10)
            SpareAttempts = sum(1 for Shot in Frames[:5] if Shot < 10) + (
                1 if self.Frames[18] == 10 and self.Frames[20] <= 10 else 0)
            First = [self.PinPos[Shot][0] for Shot in self.PinPos.keys() if Shot in (2, 4, 6, 8, 10, 11, 12)]
            Splits = sum(self.SplitFrames[1::2])
            return (Strikes, FirstShots, Spares, SpareAttempts, First, Splits)
        else:
            return (None)

    def GetSS(self):
        return (self.FS[-2])

    def GetHS(self):
        return (self.FS[-1])

    def ProcessRaw(self):
        # First work out how many shots there are
        raw = self.raw
        Shots = len(raw[3])
        self.Shots = Shots
        self.FirstDist = [0] * 11
        self.Splits = 0
        self.SplitsC = 0
        self.SplitFrames = []
        Frames = []
        Pins = []
        for Rack in range(Shots):
            L4 = raw[0][4 * Rack:(4 * Rack + 4)]
            L3 = raw[1][3 * Rack:(3 * Rack + 3)]
            L2 = raw[2][2 * Rack:(2 * Rack + 2)]
            L1 = raw[3][Rack]
            if len(L4) < 4: print(self.Name, '\n', self.Meta, '\n', raw[0], '\n', raw[1], '\n', raw[2], '\n', raw[3])
            # Append the number of pins in the first shot
            First = L1.count('¡') + L2.count('¡') + L3.count('¡') + L4.count('¡')
            Second = L1.count('£') + L2.count('£') + L3.count('£') + L4.count('£')
            Frames.append(First)
            self.FirstDist[First] += 1
            if First == 10:
                self.PinPos[Rack + 1] = [[], []]
                self.SplitFrames.append(0)
            if First < 10:
                Pins = []
                if L1[0] in ('£', 'l'): Pins.append(1)
                if L2[0] in ('£', 'l'): Pins.append(2)
                if L2[1] in ('£', 'l'): Pins.append(3)
                if L3[0] in ('£', 'l'): Pins.append(4)
                if L3[1] in ('£', 'l'): Pins.append(5)
                if L3[2] in ('£', 'l'): Pins.append(6)
                if L4[0] in ('£', 'l'): Pins.append(7)
                if L4[1] in ('£', 'l'): Pins.append(8)
                if L4[2] in ('£', 'l'): Pins.append(9)
                if L4[3] in ('£', 'l'): Pins.append(10)
                Stand = []
                if L1[0] == 'l': Stand.append(1)
                if L2[0] == 'l': Stand.append(2)
                if L2[1] == 'l': Stand.append(3)
                if L3[0] == 'l': Stand.append(4)
                if L3[1] == 'l': Stand.append(5)
                if L3[2] == 'l': Stand.append(6)
                if L4[0] == 'l': Stand.append(7)
                if L4[1] == 'l': Stand.append(8)
                if L4[2] == 'l': Stand.append(9)
                if L4[3] == 'l': Stand.append(10)
                self.PinPos[Rack + 1] = [Pins, Stand]
                if Rack < 10:
                    try:
                        self.Left[tuple(Pins)] += 1
                    except KeyError:
                        self.Left[tuple(Pins)] = 1
                    if First + Second == 10:
                        Ind = 1
                    else:
                        Ind = 0
                    try:
                        self.Spared[tuple(Pins)] += Ind
                    except KeyError:
                        self.Spared[tuple(Pins)] = Ind
                elif Rack == 10:
                    # Second shot of the 10th only if there are two shots...
                    if len(self.PinPos[Rack][0]) == 0:
                        try:
                            self.Left[tuple(Pins)] += 1
                        except KeyError:
                            self.Left[tuple(Pins)] = 1
                        if First + Second == 10:
                            Ind = 1
                        else:
                            Ind = 0
                        try:
                            self.Spared[tuple(Pins)] += Ind
                        except KeyError:
                            self.Spared[tuple(Pins)] = Ind
                            # This needs to be corrected later for open frames...
                # Splits
                if 1 in Pins:
                    self.SplitFrames.append(0)
                else:
                    TEMP = Pins[:]
                    # Prune back row.
                    if 7 in TEMP and 4 in TEMP: TEMP.remove(7)
                    if 8 in TEMP and (4 in TEMP or 5 in TEMP): TEMP.remove(8)
                    if 9 in TEMP and (6 in TEMP or 5 in TEMP): TEMP.remove(9)
                    if 10 in TEMP and 6 in TEMP: TEMP.remove(10)
                    # Prune second row.
                    if 4 in TEMP and 2 in TEMP: TEMP.remove(4)
                    if 5 in TEMP and (2 in TEMP or 3 in TEMP): TEMP.remove(5)
                    if 6 in TEMP and 3 in TEMP: TEMP.remove(6)
                    # Finally double-wood
                    if 8 in TEMP and 2 in TEMP: TEMP.remove(8)
                    if 9 in TEMP and 3 in TEMP: TEMP.remove(9)
                    if len(TEMP) > 1:
                        if Rack < 10 or Frames[-2] == 10:
                            self.Splits += 1
                            self.SplitFrames.append(1)
                            if First + Second == 10: self.SplitsC += 1
                        elif Rack == 10 and Frames[18] == 10:
                            self.Splits += 1
                            self.SplitFrames.append(1)
                            if First + Second == 10: self.SplitsC += 1
                        else:
                            self.SplitFrames.append(0)
                    else:
                        self.SplitFrames.append(0)
            # Now for the second shot
            Frames.append(Second)
            # Now for the scores
        FS = [0]
        self.St = 0
        self.Op = 0
        self.Run = {}
        for i in range(1, 13): self.Run[i] = 0
        Run = 0
        for i in range(0, 20, 2):
            if Frames[i] == 10:  # Strike
                self.St += 1
                self.NormalScore.extend(['', 'X'])
                Run += 1
                if Frames[i + 2] == 10:
                    FS.append(FS[-1] + 20 + Frames[i + 4])
                else:
                    FS.append(FS[-1] + 10 + Frames[i + 2] + Frames[i + 3])
            elif Frames[i] + Frames[i + 1] == 10:
                if Run > 0:
                    self.Run[Run] += 1
                    Run = 0
                self.NormalScore.extend([str(Frames[i]), '/'])
                FS.append(FS[-1] + 10 + Frames[i + 2])
            else:
                if Run > 0:
                    self.Run[Run] += 1
                    Run = 0
                FS.append(FS[-1] + Frames[i] + Frames[i + 1])
                self.NormalScore.extend([str(Frames[i]), str(Frames[i + 1])])
                self.Op += 1
        del FS[0]
        self.FSTest = FS
        diff = 0
        if self.FSTest[-1] != self.FS[-2]:
            # Opening the second rack of the 10th (after a strike) kills the program.
            diff = self.FSTest[-1] - self.FS[-2]
            # self.FSTest = 1#-= diff #= self.FS[-2]
            FS[-1] = FS[-1] - diff
            Frames[-1] = Frames[-1] - diff
            # Correct pin position
            self.PinPos[max(self.PinPos.keys())][1].extend(self.PinPos[max(self.PinPos.keys())][0][diff:])
            self.Spared[tuple(Pins)] -= 1
            self.Op += 1
        # Correct for strikes at the end of the 10th
        if len(Frames) >= 21:
            if Frames[20] == 10 and Frames[18] + Frames[19] == 10:
                self.St += 1
                self.NormalScore.append('X')
                Run += 1
            elif Frames[18] == 10 and Frames[20] + Frames[21] == 10 and Frames[20] < 10 and diff == 0:
                self.NormalScore.extend([str(Frames[20]), '/'])
                if Run > 0:
                    self.Run[Run] += 1
                    Run = 0
            elif Frames[18] == 10 and Frames[20] + Frames[21] == 10 and Frames[20] < 10 and diff != 0:
                self.NormalScore.extend([str(Frames[20]), str(Frames[21] - diff)])
                if Run > 0:
                    self.Run[Run] += 1
                    Run = 0
            elif Frames[18] == 10 and Frames[20] + Frames[21] < 10 and diff != 0:
                self.NormalScore.extend([str(Frames[20]), str(Frames[21])])
                if Run > 0:
                    self.Run[Run] += 1
                    Run = 0
            elif Frames[18] == 10 and Frames[20] + Frames[21] < 10 and diff == 0:
                self.NormalScore.extend([str(Frames[20]), str(Frames[21])])
                if Run > 0:
                    self.Run[Run] += 1
                    Run = 0
            elif Frames[18] + Frames[19] == 10:
                if Frames[20] == 10:
                    self.NormalScore.append('X')
                else:
                    self.NormalScore.append(str(Frames[20]))
                    # Show pins you don't shoot at as a miss???
                    self.PinPos[11][1].extend(self.PinPos[11][0])
            if len(Frames) >= 23:
                if Frames[22] == 10:
                    self.St += 1
                    Run += 1
                    self.NormalScore.append('X')
                else:
                    self.NormalScore.append(str(Frames[22]))
        # if Frames[18] + Frames[19] < 10: del self.PinPos[max(self.PinPos.keys())]
        if Run > 0:
            self.Run[Run] += 1
            Run = 0
        self.Frames = Frames
        self.G200 = 1 if FS[-1] >= 200 else 0
        self.G300 = 1 if FS[-1] >= 300 else 0
        self.SPM = sum([self.Left[Key] - self.Spared[Key] for Key in self.Left.keys() if len(Key) == 1])
        self.Errors = self.Op - self.Splits + self.SplitsC
        self.FirstDist[-1] = self.St
        self.NormalScore = ['-' if el == '0' else el for el in self.NormalScore]
        if self.NormalScore[18] == '': del self.NormalScore[18]
        if len(self.NormalScore) == 20: self.NormalScore.append('')


class Player:
    def __init__(self, Name):
        self.Name = Name
        self.Games = []

    def AddGame(self, FrameScores, Meta, FbF):
        self.Games.append(Game(FrameScores, Meta, FbF, self.Name))

    def GetScratchScores(self):
        return ([Game.GetSS() for Game in self.Games])

    def LaneStatistics(self):
        # I'm guessing that first shot carry/strike/split and spare % are the
        # important ones.
        Lanes = set(Game.Meta[0] for Game in self.Games)
        Lanes.update(set(Game.Meta[0] + 1 if Game.Meta[0] % 2 else Game.Meta[0] - 1 for Game in self.Games))
        self.LStrikes = {}
        self.LFS = {}
        self.LSpares = {}
        self.LGSpares = {}
        self.LSpareAttempts = {}
        self.LGSpareAttempts = {}
        self.LFirst = {}
        self.LSplits = {}
        self.GSplits = {}
        for Game in self.Games:
            for Lane in Lanes:
                A = Game.LaneStat(Lane)
                if A is not None:
                    (St, FS, Sp, Sa, F, Splits) = A
                else:
                    continue
                try:
                    self.GSplits[self.Games.index(Game) + 1] += Splits
                except KeyError:
                    self.GSplits[self.Games.index(Game) + 1] = Splits
        for Lane in Lanes:
            for Game in self.Games:
                A = Game.LaneStat(Lane)
                if A is not None:
                    (St, FS, Sp, Sa, F, Splits) = A
                else:
                    continue
                if Sp > Sa or St > FS:
                    print(self.Name, A, Lane, Sp > Sa, St > FS, self.Games.index(Game))
                try:
                    self.LStrikes[Lane] += St
                except KeyError:
                    self.LStrikes[Lane] = St
                try:
                    self.LFS[Lane] += FS
                except KeyError:
                    self.LFS[Lane] = FS
                try:
                    self.LSpares[Lane] += Sp
                except KeyError:
                    self.LSpares[Lane] = Sp
                try:
                    self.LGSpares[Game.Meta[1], Lane] += Sp
                except KeyError:
                    self.LGSpares[Game.Meta[1], Lane] = Sp
                try:
                    self.LSpareAttempts[Lane] += Sa
                except KeyError:
                    self.LSpareAttempts[Lane] = Sa
                try:
                    self.LGSpareAttempts[Game.Meta[1], Lane] += Sa
                except KeyError:
                    self.LGSpareAttempts[Game.Meta[1], Lane] = Sa
                try:
                    self.LFirst[Lane].extend(F)
                except KeyError:
                    self.LFirst[Lane] = F
                try:
                    self.LSplits[Lane] += Splits
                except KeyError:
                    self.LSplits[Lane] = Splits

    def SummaryStats(self, Type):
        self.Strikes = sum(Game.St for Game in self.Games)
        self.Spares = sum(self.LGSpares.values())
        self.Scores = [Game.FS[-2] for Game in self.Games]
        self.Open = sum(Game.Op for Game in self.Games)
        self.G200 = sum(Game.G200 for Game in self.Games)
        self.G300 = sum(Game.G300 for Game in self.Games)
        self.Chain = [sum(Game.Run[i] for Game in self.Games) for i in range(1, 13)]
        self.MaxStrike = max(Game.St for Game in self.Games)
        self.FirstDist = [sum(Game.FirstDist[i] for Game in self.Games) for i in range(11)]
        self.SPM = sum(Game.SPM for Game in self.Games)
        self.Splits = sum(Game.Splits for Game in self.Games)
        self.SplitsC = sum(Game.SplitsC for Game in self.Games)
        self.Errors = sum(Game.Errors for Game in self.Games)
        self.FShots = sum(Game.Shots for Game in self.Games)
        self.SShots = 10 * sum(1 for Game in self.Games)
        self.GameTimes = [G.Meta[3] - G.Meta[2] for G in self.Games]
        AvgTime = sorted(self.GameTimes)[len(self.GameTimes) // 2]
        # AvgTime = sum(self.GameTimes, timedelta(0))/len(self.GameTimes)
        m, s = divmod(AvgTime.seconds, 60)
        self.AvgTime = '{0}:{1:02d}'.format(m, s)
        if Type == 1:
            return (self.Name, self.G200, round(sum(self.Scores) / len(self.Scores), 2), max(self.Scores), self.Spares,
                    self.Strikes, self.Open,
                    self.Splits, self.SplitsC, self.SPM, sum(Game.FirstDist[9] for Game in self.Games), self.Errors,
                    self.AvgTime)
        elif Type == 2:
            A = [self.Name]
            A.extend(self.Chain)
            return (A)
        else:
            A = [self.Name]
            A.extend(self.FirstDist)
            return (A)

    def MostCommonLeaves(self):
        self.Left = {}
        self.Spared = {}
        for Game in self.Games:
            for key in Game.Left.keys():
                try:
                    self.Left[key] += Game.Left[key];
                    self.Spared[key] += Game.Spared[key]
                except KeyError:
                    self.Left[key] = Game.Left[key];
                    self.Spared[key] = Game.Spared[key]
        Carry = [0] * 10
        Convert = [0] * 10
        for i in range(1, 11):
            Carry[i - 1] = sum(key.count(i) for key in self.Left.keys())
            Convert[i - 1] = sum(key.count(i) for key in self.Spared.keys())
        self.Carry = Carry
        self.Convert = Convert

    def GenerateReport(self, f):
        # Start with the preamble
        self.MostCommonLeaves()
        Pairs = sorted(self.Left.items(), key=lambda x: -x[1])
        count = 0
        Cols = 4
        for (key, value) in Pairs:
            if count % Cols == 0:
                f.write(r'\centerline{\begin{tabular}{ccccc}')
            f.write(r'\resizebox{' + str(1 / Cols))
            f.write(r'''\textwidth}{!}{
\begin{tikzpicture}[framed]
\begin{scope}[node distance = 40,minimum size = 1cm]''')
            f.write(r'\node[' + '{0}'.format('hit' if 1 not in key else 'miss') + '] (1) {1};' + '\n')
            f.write(r'\node[' + '{0}'.format('hit' if 2 not in key else 'miss') + ',above left of = 1] (2) {2};' + '\n')
            f.write(
                r'\node[' + '{0}'.format('hit' if 3 not in key else 'miss') + ',above right of = 1] (3) {3};' + '\n')
            f.write(r'\node[' + '{0}'.format('hit' if 4 not in key else 'miss') + ',above left of = 2] (4) {4};' + '\n')
            f.write(
                r'\node[' + '{0}'.format('hit' if 5 not in key else 'miss') + ',above right of = 2] (5) {5};' + '\n')
            f.write(
                r'\node[' + '{0}'.format('hit' if 6 not in key else 'miss') + ',above right of = 3] (6) {6};' + '\n')
            f.write(r'\node[' + '{0}'.format('hit' if 7 not in key else 'miss') + ',above left of = 4] (7) {7};' + '\n')
            f.write(
                r'\node[' + '{0}'.format('hit' if 8 not in key else 'miss') + ',above right of = 4] (8) {8};' + '\n')
            f.write(
                r'\node[' + '{0}'.format('hit' if 9 not in key else 'miss') + ',above right of = 5] (9) {9};' + '\n')
            f.write(
                r'\node[' + '{0}'.format('hit' if 10 not in key else 'miss') + ',above right of = 6] (10) {10};' + '\n')
            f.write(
                r'\node[anchor=south east,scale=2,inner sep=0pt,outer sep=0pt] at (current bounding box.south east) {' + str(
                    round(100 * self.Spared[key] / self.Left[key])) + '\\%};\n')
            f.write(
                r'\node[anchor=south west,scale=2,inner sep=0pt,outer sep=0pt] at (current bounding box.south west) {' + str(
                    self.Spared[key]) + '/' + str(self.Left[key]) + '};\n')
            f.write(r'\end{scope}\end{tikzpicture}}&' + '\n')
            if count % Cols == Cols - 1:
                f.write(r'\end{tabular}}' + '\n')
            count += 1
        if count % Cols != 0: f.write(r'\end{tabular}}' + '\n')

    def GeneratePinPosTikz(self, f):
        for Game in self.Games:
            f.write(r'\centerline{\begin{tabular}{ccccccccccccc}')
            for Shot in range(12):
                f.write(r'\resizebox{0.08\textwidth}{!}{' + Game.NormalScore[2 * Shot] + Game.NormalScore[
                    2 * Shot + 1] + '}&')
            f.write(r'\\')
            for Shot in range(1, 13):
                try:
                    [First, Second] = Game.PinPos[Shot]
                except KeyError:
                    continue
                f.write(r'''\resizebox{0.08\textwidth}{!}{
\begin{tikzpicture}[framed]
\begin{scope}[node distance = 40]''')
                f.write(r'\node[' + '{0}'.format(
                    'hit' if 1 not in First else 'miss2' if 1 not in Second else 'missed') + '] (1) {1};' + '\n')
                f.write(r'\node[' + '{0}'.format(
                    'hit' if 2 not in First else 'miss2' if 2 not in Second else 'missed') + ',above left of = 1] (2) {2};' + '\n')
                f.write(r'\node[' + '{0}'.format(
                    'hit' if 3 not in First else 'miss2' if 3 not in Second else 'missed') + ',above right of = 1] (3) {3};' + '\n')
                f.write(r'\node[' + '{0}'.format(
                    'hit' if 4 not in First else 'miss2' if 4 not in Second else 'missed') + ',above left of = 2] (4) {4};' + '\n')
                f.write(r'\node[' + '{0}'.format(
                    'hit' if 5 not in First else 'miss2' if 5 not in Second else 'missed') + ',above right of = 2] (5) {5};' + '\n')
                f.write(r'\node[' + '{0}'.format(
                    'hit' if 6 not in First else 'miss2' if 6 not in Second else 'missed') + ',above right of = 3] (6) {6};' + '\n')
                f.write(r'\node[' + '{0}'.format(
                    'hit' if 7 not in First else 'miss2' if 7 not in Second else 'missed') + ',above left of = 4] (7) {7};' + '\n')
                f.write(r'\node[' + '{0}'.format(
                    'hit' if 8 not in First else 'miss2' if 8 not in Second else 'missed') + ',above right of = 4] (8) {8};' + '\n')
                f.write(r'\node[' + '{0}'.format(
                    'hit' if 9 not in First else 'miss2' if 9 not in Second else 'missed') + ',above right of = 5] (9) {9};' + '\n')
                f.write(r'\node[' + '{0}'.format(
                    'hit' if 10 not in First else 'miss2' if 10 not in Second else 'missed') + ',above right of = 6] (10) {10};' + '\n')
                f.write(r'\end{scope}\end{tikzpicture}}&' + '\n')
            if len(Game.PinPos) < 12:
                f.write(r'''\resizebox{0.08\textwidth}{!}{
\begin{tikzpicture}[framed]
\begin{scope}[node distance = 40]''')
                f.write(r'\node[empty] (1) {};' + '\n')
                f.write(r'\node[empty,above left of = 1] (2) {};' + '\n')
                f.write(r'\node[empty,above right of = 1] (3) {};' + '\n')
                f.write(r'\node[empty,above left of = 2] (4) {};' + '\n')
                f.write(r'\node[empty,above right of = 2] (5) {};' + '\n')
                f.write(r'\node[empty,above right of = 3] (6) {};' + '\n')
                f.write(r'\node[empty,above left of = 4] (7) {};' + '\n')
                f.write(r'\node[empty,above right of = 4] (8) {};' + '\n')
                f.write(r'\node[empty,above right of = 5] (9) {};' + '\n')
                f.write(r'\node[empty,above right of = 6] (10) {};' + '\n')
                f.write(r'\end{scope}\end{tikzpicture}}&' + '\n')
            f.write('\end{tabular}}\n')

    def GeneratePinPosLatex(self, f):
        for Game in self.Games:
            f.write('Lane ' + str(Game.Meta[0]) + '\hfill Game ' + str(Game.Meta[1]) + '\hfill ' + str(
                Game.Meta[2]) + '\hfill ' + str(Game.Meta[3]) + r'\hfill\\' + '\n')
            f.write(r'\begin{tabular}{*{12}{|m{0.08\textwidth}}|}')
            f.write(r'\hline' + '\n')  # Delete for booktabs
            for Shot in range(9):
                try:
                    if Game.SplitFrames[Shot] == 1:
                        Start = r'\raisebox{.5pt}{\textcircled{\raisebox{-.9pt} {'
                        End = '}}}'
                    else:
                        Start = ''
                        End = ''
                except IndexError:
                    Start = ''
                    End = ''
                f.write('{2}{4}{0}{5}{3}{2}{1}{3}&'.format(Game.NormalScore[2 * Shot], Game.NormalScore[2 * Shot + 1],
                                                           r'\framebox[0.04\textwidth]{', r'\vphantom{/}}', Start, End))
            try:
                if Game.SplitFrames[9] == 1 or Game.SplitFrames[10] == 1:
                    Start = r'\raisebox{.5pt}{\textcircled{\raisebox{-.9pt} {'
                    End = '}}}'
                    if Game.NormalScore[18] == 'X':
                        f.write('{2}{0}{3}{2}{5}{1}{6}{3}{2}{4}{3}&'.format(Game.NormalScore[18], Game.NormalScore[19],
                                                                            r'\framebox[0.02666666666666667\textwidth]{',
                                                                            r'\vphantom{/}}', Game.NormalScore[20],
                                                                            Start, End))
                    else:
                        f.write('{2}{5}{0}{6}{3}{2}{1}{3}{2}{4}{3}&'.format(Game.NormalScore[18], Game.NormalScore[19],
                                                                            r'\framebox[0.02666666666666667\textwidth]{',
                                                                            r'\vphantom{/}}', Game.NormalScore[20],
                                                                            Start, End))
                else:
                    f.write('{2}{0}{3}{2}{1}{3}{2}{4}{3}&'.format(Game.NormalScore[18], Game.NormalScore[19],
                                                                  r'\framebox[0.02666666666666667\textwidth]{',
                                                                  r'\vphantom{/}}', Game.NormalScore[20]))
            except IndexError:
                print(self.Name)
            # f.write('{2}{0}{3}{2}{1}{3}{2}{4}{3}&'.format(Game.NormalScore[18],Game.NormalScore[19],'',r'\vphantom{/}',Game.NormalScore[20]))
            try:
                f.write(str(Game.NormalScore[2 * 12]))
            except IndexError:
                pass
            f.write(r'\\' + '\n')
            f.write(r'\cline{1-10}' + '\n')  # Delete for booktabs
            for Frame in Game.FSTest[:10]:
                # f.write('{1}{0}{2}&'.format(Frame,r'\framebox[0.08\textwidth]{',r'}'))
                if Frame == Game.FSTest[9]:
                    f.write('{1}{0}{2}'.format(Frame, r'\framebox[0.08\textwidth]{', r'}') + r'& {1}{0}{2}'.format(
                        Game.FSTest[-1], r'\hfil{\bf', r'}'))
                else:
                    f.write('{1}{0}{2}&'.format(Frame, r'\framebox[0.08\textwidth]{', r'}'))
            f.write(r'\\' + '\n')
            f.write(r'\hline' + '\n')  # Delete for booktabs
            for Shot in range(1, 13):
                try:
                    [First, Second] = Game.PinPos[Shot]
                except KeyError:
                    continue
                Sym1 = r'\textcolor{dark-gray}{\textopenbullet}'
                Sym2 = r'\textopenbullet'
                # f.write(r'\framebox[0.08\textwidth]{\begin{tabular}{@{\hskip 6pt}c@{\hskip -3pt}c@{\hskip -3pt}c@{\hskip -3pt}c@{\hskip -3pt}c@{\hskip -3pt}c@{\hskip -3pt}c@{\hskip 6pt}}'+'\n')
                if Shot == 10:
                    f.write(r'\multicolumn{2}{|p{0.16\textwidth}|}{')
                elif Shot < 10:
                    f.write(r'\centering')
                f.write(
                    r'\begin{tabular}{@{\hskip 3pt}c@{\hskip -3pt}c@{\hskip -3pt}c@{\hskip -3pt}c@{\hskip -3pt}c@{\hskip -3pt}c@{\hskip -3pt}c@{\hskip 3pt}}' + '\n')
                f.write('{0}'.format(Sym1 if 7 not in First else Sym2 if 7 not in Second else r'\textbullet') + '&&')
                f.write('{0}'.format(Sym1 if 8 not in First else Sym2 if 8 not in Second else r'\textbullet') + '&&')
                f.write('{0}'.format(Sym1 if 9 not in First else Sym2 if 9 not in Second else r'\textbullet') + '&&')
                f.write('{0}'.format(
                    Sym1 if 10 not in First else Sym2 if 10 not in Second else r'\textbullet') + r'\\[-0.75em]' + '\n' + '&')
                f.write('{0}'.format(Sym1 if 4 not in First else Sym2 if 4 not in Second else r'\textbullet') + '&&')
                f.write('{0}'.format(Sym1 if 5 not in First else Sym2 if 5 not in Second else r'\textbullet') + '&&')
                f.write('{0}'.format(
                    Sym1 if 6 not in First else Sym2 if 6 not in Second else r'\textbullet') + r'\\[-0.75em]' + '\n' + '&&')
                f.write('{0}'.format(Sym1 if 2 not in First else Sym2 if 2 not in Second else r'\textbullet') + '&&')
                f.write('{0}'.format(
                    Sym1 if 3 not in First else Sym2 if 3 not in Second else r'\textbullet') + r'\\[-0.75em]' + '\n' + '&&&')
                f.write('{0}'.format(Sym1 if 1 not in First else Sym2 if 1 not in Second else r'\textbullet') + '\n')
                f.write(r'\end{tabular}')
                if Shot < 10:
                    f.write('&')
                elif Shot == max(Game.PinPos.keys()):
                    f.write('}')
            f.write(r'\\\hline' + '\n')  # Delete for booktabs
            f.write(r'\end{tabular}' + r'\\~\\')


class Database:
    def __init__(self):
        self.Players = []

    def LaneInfo(self):
        self.StbyL = {}
        self.FSbyL = {}
        self.StRbyL = {}
        self.SpbyL = {}
        self.SpAbyL = {}
        self.SpRbyL = {}
        self.SplitbyL = {}
        self.SplitRbyL = {}
        for P in self.Players:
            P.LaneStatistics()
            for Lane in P.LStrikes.keys():
                # Strikes
                try:
                    self.StbyL[Lane] += P.LStrikes[Lane]
                except KeyError:
                    self.StbyL[Lane] = P.LStrikes[Lane]
                # First shots
                try:
                    self.FSbyL[Lane] += P.LFS[Lane]
                except KeyError:
                    self.FSbyL[Lane] = P.LFS[Lane]
                # Spares
                try:
                    self.SpbyL[Lane] += P.LSpares[Lane]
                except KeyError:
                    self.SpbyL[Lane] = P.LSpares[Lane]
                # Spare attempts
                try:
                    self.SpAbyL[Lane] += P.LSpareAttempts[Lane]
                except KeyError:
                    self.SpAbyL[Lane] = P.LSpareAttempts[Lane]
                # Spare attempts
                try:
                    self.SplitbyL[Lane] += P.LSplits[Lane]
                except KeyError:
                    self.SplitbyL[Lane] = P.LSplits[Lane]
        # Calculate rates by lane
        for Lane in self.StbyL.keys():
            self.StRbyL[Lane] = self.StbyL[Lane] / self.FSbyL[Lane]
            self.SpRbyL[Lane] = self.SpbyL[Lane] / self.SpAbyL[Lane]
            self.SplitRbyL[Lane] = self.SplitbyL[Lane] / self.FSbyL[Lane]

    def GenerateReport(self, file=''):
        if file == '': file = r'C:\Users\Chris\Documents\Report.tex'
        with open(file, 'w') as f:
            f.write(r'''\documentclass[12pt]{report}
\usepackage{tikz}
\usetikzlibrary{backgrounds,calc,positioning}
\usepackage{graphicx}
%\usepackage{booktabs}
\newcommand{\toprule}{\hline}
\newcommand{\midrule}{\hline}
\newcommand{\bottomrule}{\hline}
\usepackage{textcomp}
\usepackage{amsmath}
\usepackage{array}
\usepackage{multirow}
\usepackage[margin=1cm]{geometry}
\usepackage{hyperref}
\definecolor{dark-gray}{gray}{0.9}
\setlength{\parindent}{0em}
\let\oldodot\odot
\renewcommand{\odot}[1][0pt]{%
  \mathrel{\raisebox{#1}{$\oldodot$}}%
}
\renewcommand{\tabcolsep}{0pt}
\tikzset{%
    miss/.style={%
        circle,fill=blue!20,draw,font=\sffamily\small\bfseries,minimum size = 1cm
    }
}
\tikzset{%
    missed/.style={%
        circle,fill=black,draw,font=\sffamily\small\bfseries,minimum size = 1cm
    }
}
\tikzset{%
    hit/.style={%
        circle,fill=white,draw,font=\sffamily\small\bfseries,minimum size = 1cm
    }
}
\tikzset{%
    miss2/.style={%
        circle,fill=green!80,draw,font=\sffamily\small\bfseries,minimum size = 1cm
    }
}
\tikzset{%
    empty/.style={minimum size = 1cm
    }
}
\begin{document}
\tableofcontents''')
            Head = ["Name", "200 Games", "Avg", "High", "Spares", "Strikes", "Open",
                    "Splits", "Splits Converted", "Single Pins Missed", "Errors", "Avg Game Time"]
            Text = []
            for P in self.Players: Text.append(P.SummaryStats(1))
            Text.sort(key=lambda key: -key[2])
            Text.insert(0, Head)
            f.write(r'\chapter{Summary Statistics}' + '\n')
            f.write(r'\section{Bowler Statistics}' + '\n')
            WriteTable(Text, f)
            Text = [["Name", '1X', '2X', '3X', '4X', '5X', '6X', '7X', '8X', '9X', '10X', '11X', '12X']]
            for P in self.Players: Text.append(P.SummaryStats(2))
            f.write(r'\newpage')
            f.write(r'\section{Strike Chains by Bowler}' + '\n')
            WriteTable(Text, f, IgnoreZeros=True)
            Text = [["Name", "0", "1", "2", "3", "4", "5",
                     "6", "7", "8", "9", "X"]]
            for P in self.Players: Text.append(P.SummaryStats(3))
            f.write(r'\newpage')
            f.write(r'\section{First Ball Count by Bowler}' + '\n')
            WriteTable(Text, f, IgnoreZeros=True)
            f.write(r'\chapter{Spare Effectiveness By Combination Left}' + '\n')
            for P in self.Players:
                f.write(r'\section{' + P.Name + '}\n')
                P.GenerateReport(f)
                f.write(r'\clearpage')
            f.write(r'\chapter{Pin Position by Game}' + '\n')
            for P in self.Players:
                f.write(r'\section{' + P.Name + '}\n')
                P.GeneratePinPosLatex(f)
                f.write(r'\clearpage')
            f.write(r'\end{document}')

    def ImportFile(self, file, Map, Exclude=(), ByGame=False, NewDate=None):
        # Import file
        xl = pd.ExcelFile(file)
        # Get sheets
        dfs = {sheet_name: xl.parse(sheet_name) for sheet_name in xl.sheet_names}
        # Extract the sheet of interest
        df = dfs['Sheet1']
        Clean = []
        for index, row in df.iterrows():
            TEMP = [el for el in row.name if type(el) is not float or np.isfinite(el)]
            if len(TEMP) > 0: Clean.append(TEMP)
            pass
        self.Clean = Clean
        FbF = []

        if ByGame:
            count = 1
        else:
            count = 5
        L = 0
        G = 0
        Start = 0
        End = 0
        HCAP = False
        Process = False
        for row in Clean:
            if Process and ByGame and type(row[0]) == str and row[0] not in ("Hdcp", "Player", '£', 'l', '¡') and len(
                    row) > 10:
                Name = row[0]
                if Name in Map.keys(): Name = Map[Name]
                if Name in Exclude: Name = 'DELETE'
                if Name in [P.Name for P in self.Players]:
                    P = self.Players[[P.Name for P in self.Players].index(Name)]
                else:
                    self.Players.append(Player(Name))
                    P = self.Players[-1]
                continue
            # Checks for new player
            if ByGame and type(row[0]) == str and row[0].split()[0] == 'Team':
                Name = row[0].split()[1]
                if Name in Map.keys(): Name = Map[Name]
                if Name in Exclude: Name = 'DELETE'
                if Name == "Team":
                    Process = True
                elif Name in [P.Name for P in self.Players]:
                    P = self.Players[[P.Name for P in self.Players].index(Name)]
                else:
                    self.Players.append(Player(Name))
                    P = self.Players[-1]
                L = int(row[1].split()[1])
                G = int(row[2].split()[1])
                Start = row[3] if not NewDate else row[3] + NewDate
                End = row[3] if not NewDate else row[3] + NewDate
                continue
            elif ByGame:
                if HCAP and count < 4:
                    if len(row) < 10: continue
                    FbF.append(row)
                    count += 1
                    continue
                elif HCAP and count >= 4:
                    HCAP = False
                    count = 1
                    FbF.append(row)
                    print(len(FbF))
                    print(P.Name, Frames, [L, G, Start, End])
                    # bfdb
                    P.AddGame(Frames, [L, G, Start, End], FbF)
                    FbF = []
                    continue
                else:
                    if row[0] == 'Hdcp':
                        HCAP = True
                        Frames = row[1:]
                    continue

            if len(row) == 12 and row[1] == '1' and row[2] == '2' and row[11] == 'Total':
                Name = row[0]
                if Name in Exclude: Name = 'DELETE'
                if Name in Map.keys(): Name = Map[Name]
                if Name in [P.Name for P in self.Players]:
                    P = self.Players[[P.Name for P in self.Players].index(Name)]
                else:
                    self.Players.append(Player(Name))
                    P = self.Players[-1]
            # Allows for collection of frame-by-frame totals
            if count < 4:
                if row == ['Total']: continue
                count += 1
                FbF.append(row)
                if count == 4:
                    P.AddGame(Frames, [L, G, Start, End], FbF)
                    count += 1
                    FbF = []
                continue
            if type(row[0]) == str and row[0].count('Lane') > 0:
                L = int(row[0].split(' ')[-1])
                G = int(row[1].split(' ')[-1])
                Start = row[3] if NewDate is None else row[3].replace(NewDate[0], NewDate[1], NewDate[2])
                End = row[4] if NewDate is None else row[4].replace(NewDate[0], NewDate[1], NewDate[2])
                # Extract meta-data from game information.
                # print(row,[L,G,Start,End])
            # Extracts frame totals
            if len(row) == 11 and all(isinstance(x, int) for x in row):
                Frames = row
                count = 0
        # self.Players = [self.Players[-1]]
        self.Players = [P for P in self.Players if P.Name != 'DELETE']


def WriteTable(Info, f, IgnoreZeros=False):
    f.write(r'\centerline{' + '\n' + r'\resizebox{\textwidth}{!}{' + '\n')
    f.write(r'\begin{tabular}{l*{' + str(len(Info[0]) - 1) + r'}{m{' + str(1 / len(Info[0][:10])) + r'\textwidth}}}')
    f.write('\n' + r'\toprule' + '\n')
    for Row in Info: f.write(
        '&'.join((str(el) if el != 0 or not IgnoreZeros else '') for el in Row) + r'\\' + '\n' + '{0}'.format(
            r'\midrule' + '\n' if Row == Info[0] else ''))
    f.write(r'\bottomrule' + '\n' + r'\end{tabular}}}' + '\n')


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