import numpy as np
import pandas as pd

from Player import *


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
