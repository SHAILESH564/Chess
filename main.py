import copy
last_move = None

class Piece:
    def __init__(self, colour, piece_type, en_passant = False, has_moved = False):
        self.colour = colour
        self.piece_type = piece_type
        self.en_passant = en_passant
        self.has_moved = has_moved

    def __repr__(self):
        return f"{self.colour} {self.piece_type}"
    
    def __str__(self):
        colour_symbol = 'W' if self.colour == 'WHITE' else 'B'
        return f"{colour_symbol}{self.piece_type}"
    
    def is_valid_rook_move(self, board, start, end):
        # Check if the move is valid for a rook
        start_row, start_col = start
        end_row, end_col = end
        if start_col == end_col:
            step = 1 if end_row > start_row else -1
            for row in range(start_row + step, end_row, step):
                if isinstance(board[row][start_col], Piece):
                    return False
            return True
        elif start_row == end_row:
            step = 1 if end_col > start_col else -1
            for col in range(start_col + step, end_col, step):
                if isinstance(board[start_row][col], Piece):
                    return False
            return True 
        return False
    
    def is_valid_bishop_move(self, board, start, end):
        # Check if the move is valid for a bishop
        start_row, start_col = start
        end_row, end_col = end
        if abs(end_col - start_col) == abs(end_row - start_row):
            step_row = 1 if end_row > start_row else -1
            step_col = 1 if end_col > start_col else -1
            row, col = start_row + step_row, start_col + step_col
            
            for _ in range(abs(end_row - start_row)-1):
                if isinstance(board[row][col], Piece):
                    return False
                row += step_row
                col += step_col
            return True
        return False
    
    def is_valid_queen_move(self, board, start, end):
        return self.is_valid_bishop_move(board, start, end) or self.is_valid_rook_move(board, start, end)

    def is_valid_knight_move(self, start, end):
        start_row, start_col = start
        end_row, end_col = end
        
        step_row = abs(start_row - end_row)
        step_col = abs(start_col - end_col)

        return (step_row, step_col) in [(2,1),(1,2)]
    
    def is_valid_king_move(self, board, start, end):
        start_row, start_col = start
        end_row, end_col = end

        step_row = abs(start_row - end_row)
        step_col = abs(start_col - end_col)

        if (step_row, step_col) in [(0,1),(1,0),(1,1)]:
            return True

        # Castling
        if step_col == 2 and not self.has_moved:
            direction = [0, -1] if start_col > end_col else [7, 1]
            rook = board[start_row][direction[0]]
            if rook and rook.piece_type == 'R' and not rook.has_moved:
                for i in range(start_col + direction[1], direction[0], direction[1]):
                    if isinstance(board[start_row][i], Piece):
                        return False
                return True
        return False
    
class Player:
    def __init__(self, name, colour):
        self.name = name
        self.colour = colour

def creat_board():
    board = [[None for _ in range(8)] for _ in range(8)]
    for i in range(8):
        board[1][i] = Piece('WHITE', 'P')
        board[6][i] = Piece('BLACK', 'P')
    
    placement = [('R', 0), ('N', 1), ('B', 2), ('Q', 3), ('K', 4), ('B', 5), ('N', 6), ('R', 7)]
    for piece, col in placement:
        board[0][col] = Piece('WHITE', piece)
        board[7][col] = Piece('BLACK', piece)
    return board

def print_board(board):
    for i, row in enumerate(board[::-1]):
        print(8 - i, end=" ")
        print("  |  ".join(str(piece) if piece else "__" for piece in row))
    print("  a      b      c      d      e      f      g      h")

def is_king_check_diags(king_pos, player, board, switch):
    # check diag for check
    directions = [(1,1),(1,-1),(-1,1),(-1,-1)]
    king_row, king_col = king_pos
    for direction in directions:
        row_var = king_row + direction[0]
        col_var = king_col + direction[1]
        while 0 <= row_var <= 7 and 0 <= col_var <= 7:
            print(board[row_var][col_var], "dia")
            if board[row_var][col_var] is not None:
                if board[row_var][col_var].colour == player.colour:
                    break
                if board[row_var][col_var].piece_type in ('B','Q'):
                    print(board[row_var][col_var], "piece", row_var, col_var)
                    return True
                if board[row_var][col_var].piece_type =='P':
                    if (player.colour == "WHITE" and row_var==king_row + 1 and abs(col_var - king_col) == 1) or (player.colour == "BLACK" and row_var==king_row - 1 and abs(col_var - king_col) == 1):
                        return True
                if board[row_var][col_var].piece_type == 'K' and abs(row_var - king_row) == 1 and abs(col_var - king_col) == 1:
                    return True
                break
            row_var += direction[0]
            col_var += direction[1]
        
    return False


def is_king_check_rows(king_pos, player, board, switch):
    # check row of king
    left_row = king_pos[1] - 1
    right_row = king_pos[1] + 1

    up_col = king_pos[0] + 1
    down_col = king_pos[0] - 1
    while left_row >= 0 or right_row <= 7 or up_col <= 7 or down_col >= 0:
        if left_row >= 0:
            if board[king_pos[0]][left_row] is not None:
                if board[king_pos[0]][left_row].colour == player.colour or board[king_pos[0]][left_row].piece_type not in ('R','Q','K'):
                    left_row = -1
                elif board[king_pos[0]][left_row].piece_type in ('R','Q'):
                    print("check", board[king_pos[0]][left_row], "piece 1 left_row")
                    return True
                elif board[king_pos[0]][left_row].piece_type == 'K' and abs(king_pos[1] - left_row) == 1:
                    return True
        if right_row <= 7:
            if board[king_pos[0]][right_row] is not None:
                if board[king_pos[0]][right_row].colour == player.colour or board[king_pos[0]][right_row].piece_type not in ('R','Q','K'):
                    right_row = 8
                elif board[king_pos[0]][right_row].piece_type in ('R','Q'):
                    print("check",board[king_pos[0]][right_row], "piece 1 right_row")
                    return True
                elif board[king_pos[0]][right_row].piece_type == 'K' and abs(right_row - king_pos[1]) == 1 :
                    return True
        if up_col <= 7:
            if board[up_col][king_pos[1]] is not None:
                if board[up_col][king_pos[1]].colour == player.colour or board[up_col][king_pos[1]].piece_type not in ('R','Q','K'):
                    up_col = 8
                elif board[up_col][king_pos[1]].piece_type in ('R','Q'):
                    print("check",board[up_col][king_pos[1]], "piece 1 right_row")
                    return True
                elif board[up_col][king_pos[1]].piece_type == 'K' and abs(up_col - king_pos[0]) == 1 :
                    return True
        if down_col >= 0:
            if board[down_col][king_pos[1]] is not None:
                if board[down_col][king_pos[1]].colour == player.colour or board[down_col][king_pos[1]].piece_type not in ('R','Q','K'):
                    down_col = -1
                elif board[down_col][king_pos[1]].piece_type in ('R','Q'):
                    print("check",board[down_col][king_pos[1]], "piece 1 right_row")
                    return True
                elif board[down_col][king_pos[1]].piece_type == 'K' and abs(down_col - king_pos[0]) == 1:
                    return True
        # print(up_col, "2", switch, king_pos[1], "kins_pos")
        left_row -= 1
        right_row += 1
        up_col += 1
        down_col -= 1
    return False

def is_king_ckeck_knight(king_pos, knight_pos, player, board):
    knight_1, knight_2 = None, None
    if not knight_pos:
        return False
    if len(knight_pos) == 1:
        knight_1 = knight_pos[0]
        piece = board[knight_1[0]][knight_1[1]] 
        if piece.is_valid_knight_move(king_pos, knight_1):
            print(knight_1, 'Check', king_pos, 'Knight')
            return True
    else:
        knight_1 = knight_pos[0] 
        knight_2 = knight_pos[1] 
        piece_1 = board[knight_1[0]][knight_1[1]]
        piece_2 = board[knight_2[0]][knight_2[1]]
        if piece_1.is_valid_knight_move(king_pos, knight_1) or piece_2.is_valid_knight_move(king_pos, knight_2):
            print(knight_1, knight_2,'Check 2', king_pos, 'Knight')
            return True
    return False
# check for checks
def is_under_check(player, board, start, end):
    # store kings positions
    white_king = None
    black_king = None
    white_knight = []
    black_knight = []

    for row_index, row in enumerate(board):
        for piece_index, piece in enumerate(row):
            if piece and piece.piece_type == 'K':
                if board[row_index][piece_index].colour == 'WHITE':
                    white_king = (row_index, piece_index)
                else:
                    black_king = (row_index, piece_index)
            if piece and piece.piece_type == 'N':
                if board[row_index][piece_index].colour == 'WHITE':
                    white_knight.append((row_index, piece_index))
                else:
                    black_knight.append((row_index, piece_index))
    temp_king1 = None
    temp_king2 = None
    temp_knight = None
    if player.colour == "WHITE":
        temp_king1 = white_king
        temp_king2 = black_king
        temp_knight = black_knight
    else:
        temp_king1 = black_king
        temp_king2 = white_king
        temp_knight = white_knight
    print(temp_king1, "temp1", temp_king2, "temp_king2")
    
    return is_king_check_rows(temp_king1, player, board, True) or is_king_check_diags(temp_king1, player, board, True) or is_king_ckeck_knight(temp_king1, temp_knight, player, board)
    # is_king_check_rows(temp_king2, player, board, False)

def make_move(start, end, player, board):
    global last_move
    start_row, start_col = start
    end_row, end_col = end
    piece = board[start_row][start_col]

    if is_valid_move(start, end, player):
        past_board = copy.deepcopy(board)
        # past_board = board.copy()
        # For en_passant
        if piece.piece_type == 'P' and abs(start_col - end_col) == 1 and board[end_row][end_col] is None:
            board[start_row][end_col] = None
        # Castling
        if piece.piece_type == 'K' and abs(start_col - end_col) == 2:
            direction = [0, 1] if start_col > end_col else [7, -1]
            board[start_row][end_col + direction[1]] = board[start_row][direction[0]]
            board[start_row][direction[0]].has_moved = True
            board[start_row][direction[0]] = None
        # Move Piece
        board[end_row][end_col] = piece
        board[start_row][start_col] = None
        piece.has_moved = True
        last_move = (piece, start, end)

        # Reset all pawns
        for row in board:
            for p in row:
                if isinstance(p, Piece) and p.piece_type == 'P' and p is not piece:
                    p.en_passant = False    

        if is_under_check(player, board, start, end):
            for i in range(8):
                for j in range(8):
                    board[i][j] = past_board[i][j]
            print("Cant move under attack!!")
            print_board(board)
            return False
    else:
        print(f"Invalid move from {start} to {end} for piece {piece}")
        return False
    return True
    
def is_valid_move(start, end, player):
    start_row, start_col = start
    end_row, end_col = end
    piece = board[start_row][start_col]
    target_piece = board[end_row][end_col]

    if piece is None:
        print("There is not piece present.")
        return False
    
    # Example validation: check if the move is within bounds and not capturing own piece
    if not (0 <= end_row < 8 and 0 <= end_col < 8):
        print("Move is out of bounds.")
        return False
    
    if player.colour != piece.colour:
        print(f"This is not your turn.")
        return False

    if target_piece is not None and target_piece.colour == piece.colour:
        print(f"Cannot capture your own piece.")
        return False
    
    if last_move and last_move[0].piece_type  == 'P' and piece.piece_type != 'P':
        last_move[0].en_passant = False
    
    # Additional rules for specific pieces can be added here
    # Pawn
    if piece.piece_type == 'P':
        direction = 1 if piece.colour == "WHITE" else -1
        start_row_limit = 1 if piece.colour == "WHITE" else 6

        if start_col == end_col:
            # one move forward
            if end_row == start_row + direction and board[end_row][end_col] is None:
                return True
                
            # Two move forward from starting row
            if start_row == start_row_limit and end_row == start_row + 2 * direction:
                if board[start_row + direction][start_col] is None and board[end_row][end_col] is None:
                    piece.en_passant = True
                    return True
        
        # Diagonal capture
        if end_row == start_row + direction and abs(end_col - start_col) == 1:
            if target_piece is not None and target_piece.colour != piece.colour:
                return True
            # en-passant logic
            adjacent = board[start_row][end_col]
            if adjacent and adjacent.piece_type == 'P' and adjacent.colour != piece.colour and adjacent.en_passant:
                return True
    # Rook
    elif piece.piece_type == 'R':
        return piece.is_valid_rook_move(board, start, end)
    # Bishop
    elif piece.piece_type == 'B':
        return piece.is_valid_bishop_move(board, start, end)
    # Queen
    elif piece.piece_type == 'Q':
        return piece.is_valid_queen_move(board, start, end)
    # Knight
    elif piece.piece_type == 'N':
        return piece.is_valid_knight_move(start, end)
    # King
    elif piece.piece_type == 'K':
        return piece.is_valid_king_move(board, start, end)
    return False

if __name__ == "__main__":
    position = { 'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7 }
    board = creat_board()
    player1 = Player(input("Enter your name player1 (WHITE): "), "WHITE")
    player2 = Player(input("Enter your name player2 (BLACK): "), "BLACK")

    turn = 1
    print_board(board)

    while True:
        current_player = player1 if turn % 2 == 1 else player2
        print(f"{current_player.name}'s turn, Enter your move (eg. a2-a3): ", end="")
        move = input().strip().lower()

        if move == 'x' or move == 'esc':
            print("Game Over!!")
            break

        try:
            start_str, to_str = move.split("-")
            # Convert string like "a2" to tuple (a, 2)
            start = (int(start_str[1])-1, position[start_str[0]])
            to = (int(to_str[1])-1, position[to_str[0]])
        except (IndexError, KeyError, ValueError):
            print("Invalid move, try again.")
            continue

        if make_move(start, to, current_player, board):
            print_board(board)
            turn += 1
        