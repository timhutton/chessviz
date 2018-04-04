''' Copyright 2018 Tim Hutton <tim.hutton@gmail.com>

    This file is part of chessviz.

    chessviz is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    chessviz is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with chessviz. If not, see <http://www.gnu.org/licenses/>.
'''

import itertools
import sys
try:
  import chess.pgn
except:
  print('Missing python-chess module. Use this to install:\n\npython -m pip install python-chess')
  exit()

def lts(l): # list to string
    return '[' + ','.join(str(i) for i in l) + ']'
def lolts(lol): # list of lists to string
    return lts(lts(l) for l in lol)
def lololts(lolol): # list of lists of lists to string
    return lts(lolts(lol) for lol in lolol)
def lolololts(lololol): # list of lists of lists of lists to string
    return lts(lololts(lolol) for lolol in lololol)

pieces = 'KQRBNPkqrbnp'

S = 8 # squares on a side of a chessboard
P = 12 # number of distinct pieces (white pawn, black bishop, etc.)
N = 100000 # maximum number of games to process
depth = 60 # for the animation, how many moves do we want to show?

# Data source: http://chessdatabaseandmore.blogspot.co.uk/2017/05/my-software.html
# Specifically: https://drive.google.com/file/d/0B3iWPBDH2o3kODd0ZGNMR3VtdDA/view?usp=sharing (1.4GB)
games = []
with open("../../AepliBase.pgn") as pgn:
    offsets_gen = chess.pgn.scan_offsets(pgn)
    offsets = []
    try:
        while len(offsets)<N:
            # skip some
            for i in range(200):
                offset = next(offsets_gen)
            offsets.append(offset)
            sys.stdout.write('.')
            sys.stdout.flush()
    except:
        pass
    print(len(offsets),' offsets found')
    for offset in offsets:
        pgn.seek(offset)
        g = chess.pgn.read_game(pgn)
        games.append(g)
        sys.stdout.write('.')
        sys.stdout.flush()
    print(len(games),' games parsed')
with open('qanim.js','w') as out:
    out.write('moves=[')
    for iMoveWanted in range(depth):
        print('\n',iMoveWanted)
        piece_move_counts = [[[[[0]*S for y1 in range(S)] for x2 in range(S)] for y2 in range(S)] for p in range(P)]
        for g in games:
            sys.stdout.write('.')
            sys.stdout.flush()
            moves = list(g.main_line())
            if(len(moves)<iMoveWanted+1):
                continue
            board = g.board()
            for i in range(iMoveWanted):
                board.push(moves[i])
            m = str(moves[iMoveWanted])
            #print(m)
            board.push(moves[iMoveWanted])
            x1 = ord(m[0])-ord('a')
            y1 = int(m[1])-1
            x2 = ord(m[2])-ord('a')
            y2 = int(m[3])-1
            p = board.piece_at(chess.square(x2,y2)).symbol()
            ip = pieces.index(p)
            piece_move_counts[ip][x1][y1][x2][y2] += 1 # TODO: if castling, move rook too
            # add non-moving pieces too
            for px in range(S):
                for py in range(S):
                    if px==x2 and py==y2:
                        continue
                    p = board.piece_at(chess.square(px,py))
                    if p:
                        ip = pieces.index(p.symbol())
                        piece_move_counts[ip][px][py][px][py] += 1 # was there, is still there
        # write piece_move_counts to file
        out.write(lolololts(piece_move_counts))
        if iMoveWanted < depth-1:
            out.write(',\n')
    out.write('];\n')
        
print('done')
