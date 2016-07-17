from Game import *


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
            return (self.Name, len(self.Scores),
                    self.G200, round(sum(self.Scores) / len(self.Scores), 2), max(self.Scores),
                    round(100 * self.Spares / self.SShots), round(100 * self.Strikes / self.FShots),
                    round(100 * self.Open / self.FShots), round(100 * self.Splits / self.FShots, 1),
                    round(100 * self.SplitsC / self.Splits, 1),
                    round(100 * self.SPM / sum(Game.FirstDist[9] for Game in self.Games), 1),
                    round(100 * self.Errors / self.FShots, 1))
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
