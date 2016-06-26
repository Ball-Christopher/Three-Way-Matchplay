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
