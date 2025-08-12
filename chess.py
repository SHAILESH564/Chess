import pygame
import copy
import os

WIDTH  = 1000
HEIGHT  = 820

NO_OF_BOARD_SQR = 8
FPS = 60
SQUARE_SIZE = 80 
last_move = None

class Player:
    def __init__(self, name, colour):
        self.name = name
        self.colour = colour

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
                x = start_col + direction[1]
                for i in range(x, direction[0], direction[1]):
                    if isinstance(board[start_row][i], Piece):
                        return False
                return True
        return False

    def is_pawn_valid_move(self, board, start, end):
        start_row, start_col = start
        end_row, end_col = end
        target_piece = board[end_row][end_col]

        direction = 1 if self.colour == "WHITE" else -1
        start_row_limit = 1 if self.colour == "WHITE" else 6

        if start_col == end_col:
            # one move forward
            if end_row == start_row + direction and board[end_row][end_col] is None:
                return True
                
            # Two move forward from starting row
            if start_row == start_row_limit and end_row == start_row + 2 * direction:
                if board[start_row + direction][start_col] is None and board[end_row][end_col] is None:
                    self.en_passant = True
                    return True
        
        # Diagonal capture
        if end_row == start_row + direction and abs(end_col - start_col) == 1:
            if target_piece is not None and target_piece.colour != self.colour:
                return True
            # en-passant logic
            adjacent = board[start_row][end_col]
            if adjacent and adjacent.piece_type == 'P' and adjacent.colour != self.colour and adjacent.en_passant:
                return True
    
def print_board(board):
    for i, row in enumerate(board[::-1]):
        print(8 - i, end=" ")
        print("  |  ".join(str(piece) if piece else "__" for piece in row))
    print("  a      b      c      d      e      f      g      h")

def is_king_check_diags(king_pos, player, board):
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

def is_king_check_rows(king_pos, player, board):
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

def is_king_ckeck_knight(king_pos, knight_pos, board):
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
def is_under_check(player, board):
    # store kings positions
    global check_message
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
    temp_knight1 = None
    temp_knight2 = None
    if player.colour == "WHITE":
        temp_king1 = white_king
        temp_king2 = black_king
        temp_knight1 = black_knight
        temp_knight2 = white_knight
    else:
        temp_king1 = black_king
        temp_king2 = white_king
        temp_knight1 = white_knight
        temp_knight2 = black_knight
    print(temp_king1, "temp1", temp_king2, "temp_king2")
    check = is_king_check_rows(temp_king2, other_player, board) or is_king_check_diags(temp_king2, other_player, board) or is_king_ckeck_knight(temp_king2, temp_knight2, board)
    if check:
        check_message = f"Under Check {str(board[temp_king2[0]][temp_king2[1]])} at {str(temp_king2)}"
    else:
        check_message = ""
    return is_king_check_rows(temp_king1, player, board) or is_king_check_diags(temp_king1, player, board) or is_king_ckeck_knight(temp_king1, temp_knight1, board)

def make_move(start, end, player, board):
    global last_move
    start_row, start_col = start
    temp_col = start_col
    end_row, end_col = end
    piece = board[start_row][start_col]

    if is_valid_move(start, end, player):
        past_board = copy.deepcopy(board)

        # For en_passant
        if piece.piece_type == 'P' and abs(start_col - end_col) == 1 and board[end_row][end_col] is None:
            if board[start_row][end_col].colour == "WHITE":
                white_captured.append(board[start_row][end_col])
            else:
                black_captured.append(board[start_row][end_col])
            board[start_row][end_col] = None
        # Castling
        if piece.piece_type == 'K' and abs(start_col - end_col) == 2:
            # [rook column, rook end pos right or left of king, direction king will take]
            direction = [0, 1, -1] if start_col > end_col else [7, -1, 1]
            if is_under_check(player, board):
                    for i in range(8):
                        for j in range(8):
                            board[i][j] = past_board[i][j]
                    print("Cant move under attack!!")
                    return False
            for x in range(start_col + direction[2], end_col, direction[2]):
                board[start_row][x] = board[start_row][temp_col]
                board[start_row][temp_col] = None
                if is_under_check(player, board):
                    for i in range(8):
                        for j in range(8):
                            board[i][j] = past_board[i][j]
                    print("Cant move under attack!!")
                    return False
                temp_col += 1
            board[start_row][end_col + direction[1]] = board[start_row][direction[0]]
            board[start_row][direction[0]].has_moved = True
            board[start_row][direction[0]] = None
        # Move Piece
        if board[end_row][end_col] is not None:
            if board[end_row][end_col].colour == "WHITE":
                white_captured.append(board[end_row][end_col])
            else :
                black_captured.append(board[end_row][end_col])
        board[end_row][end_col] = piece
        board[start_row][start_col] = None
        piece.has_moved = True
        last_move = (piece, start, end)

        # Reset all pawns
        for row in board:
            for p in row:
                if isinstance(p, Piece) and p.piece_type == 'P' and p is not piece:
                    p.en_passant = False    
        # Pawn reached Promotion Square
        if piece.piece_type == 'P' and (end_row == 7 or end_row == 0):
            chosen_piece = select_piece(end)
            print(f"Chosen piece for promotion in p: {chosen_piece}")
            chosen_colour, chosen_piece_type = chosen_piece.split(" ")
            print(f"Chosen colour: {chosen_colour}, Chosen piece type: {chosen_piece_type}")
            board[end_row][end_col] = Piece(chosen_colour, chosen_piece_type)
            print_board(past_board)
            print("/n")
            print_board(board)

        if is_under_check(player, board):
            for i in range(8):
                for j in range(8):
                    board[i][j] = past_board[i][j]
            print("Cant move under attack!!")
            return False
    else:
        print(f"Invalid move from {start} to {end} for piece {piece}")
        return False
    return True

def select_piece(end):
    end_row, end_col = end
    piece = board[end_row][end_col]
    colour = piece.colour
    print(f"Select a piece for promotion for {colour} {piece.piece_type} at {end}")
    piece_spaccing = 40
    promo_piece = ['Q','R','B','N']
    total_piece_width = len(promo_piece) * piece_spaccing
    x = whole_board_size + (leftover_width - total_piece_width)//2
    y = SQUARE_SIZE * 3 + 25
    temp_x = x
    for i in promo_piece:
        screen.blit(images_small[colour[0] + i],(temp_x,y))
        temp_x += piece_spaccing 
    pygame.display.flip()
    selecting = True
    chosen = None
    
    while selecting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit() 
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                temp_x = x

                for i in promo_piece:
                    rect = pygame.Rect(temp_x, y, images_small[colour[0] + i].get_width(), images_small[colour[0] + i].get_height())
                    if rect.collidepoint(mouse_x, mouse_y):
                        selecting = False
                        chosen = colour + " "+ i
                        break
                    temp_x += piece_spaccing
    print(f"Chosen piece for promotion: {chosen}")
    return chosen

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
        return piece.is_pawn_valid_move(board, start, end)
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

def load_images():
    pieces = ['P','K','Q','R','N','B']
    images_big = {}
    images_small = {}
    for player in ['B','W']:
        for piece in pieces:
            name = player+piece
            path = os.path.join("assests", name+'.png')
            image = pygame.image.load(path)
            images_big[name] = pygame.transform.scale(image,(70,70))
            images_small[name] = pygame.transform.scale(image,(50,50))
    return (images_big, images_small)

def create_board():
    board = [[None for _ in range(8)] for _ in range(8)]
    for i in range(8):
        board[1][i] = Piece('WHITE', 'P')
        board[6][i] = Piece('BLACK', 'P')
    
    placement = [('R', 0), ('N', 1), ('B', 2), ('Q', 3), ('K', 4), ('B', 5), ('N', 6), ('R', 7)]
    for piece, col in placement:
        board[0][col] = Piece('WHITE', piece)
        board[7][col] = Piece('BLACK', piece)
    return board

def draw_board():
    light_square = (240, 217, 181)
    dark_square = (181, 136, 99)
    big_font = pygame.font.Font('freesansbold.ttf', 50)
    small_font = pygame.font.Font('freesansbold.ttf', 20)
    row_names = ["a", "b", "c", "d", "e", "f", "g", "h"]
    ranks = ['1','2','3','4','5','6','7','8']

    for row in range(8):
        for col in range(8):
            x = col * SQUARE_SIZE 
            y = row * SQUARE_SIZE 
            colour = light_square if (row + col) % 2 == 0 else dark_square
            pygame.draw.rect(screen, colour,(x, y, SQUARE_SIZE, SQUARE_SIZE))
    
    for index_x, row in enumerate(board[::-1]):
        for index_y, piece in enumerate(row):
            x_start = index_y * SQUARE_SIZE
            y_start = index_x * SQUARE_SIZE
            if piece:
                key = str(piece)
                image = images.get(key)
                if image:
                    image_rect = image.get_rect(center=(x_start + SQUARE_SIZE//2, y_start + SQUARE_SIZE//2))
                    screen.blit(image, image_rect)

    for col in range(8):
        file_label = small_font.render(row_names[col], True, "black")
        screen.blit(file_label, (col * SQUARE_SIZE + file_label.get_width()//2, whole_board_size - SQUARE_SIZE//2 + 10))
    for row in range(8):
        rank_label = small_font.render(ranks[7 - row], True, "black")
        screen.blit(rank_label, (5, row * SQUARE_SIZE + rank_label.get_height()//2))

    leftover_height = HEIGHT - whole_board_size
    pygame.draw.rect(screen, (200, 200, 200), (0, whole_board_size, WIDTH, leftover_height))  # fill
    pygame.draw.rect(screen, (255, 215, 0), (0, whole_board_size, WIDTH, leftover_height), 5)  # border

    pygame.draw.rect(screen, (200, 200, 200),(whole_board_size, 0, leftover_width, HEIGHT))
    pygame.draw.rect(screen, (255, 215, 0),(whole_board_size, 0, leftover_width, HEIGHT),5)
    # Draw Reset Button
    pygame.draw.rect(screen, (255, 0, 0), (whole_board_size, whole_board_size  + SQUARE_SIZE, leftover_width, WIDTH - whole_board_size - SQUARE_SIZE))
    screen.blit(big_font.render("RESET", True, 'white'), (whole_board_size + leftover_width//2 - 60, whole_board_size + SQUARE_SIZE + 20))


    screen.blit(big_font.render(message, True, 'black'), (20,whole_board_size+ 20))

    pygame.draw.rect(screen, (255, 215, 0), (whole_board_size, 0, leftover_width, SQUARE_SIZE * 3), 3)
    
    screen.blit(small_font.render("WHITE CAPTURED", True, 'black'), (whole_board_size + 15, SQUARE_SIZE * 6 + 10))
    screen.blit(small_font.render("BLACK CAPTURED", True, 'black'), (whole_board_size + 15, 10))
    screen.blit(small_font.render(check_message, True, 'black'), (whole_board_size + 15, SQUARE_SIZE * 4 + 10))
    

    piece_spaccing = 40
    row_spaccing = 40
    max_x = WIDTH - 50

    if black_captured:
        x = whole_board_size + 15
        y = SQUARE_SIZE * 6 + 10 + 25
        for piece in black_captured:
            image = images_small.get(str(piece))
            screen.blit(image, (x, y))
            x += piece_spaccing
            if x >= max_x:
                x = whole_board_size + 15
                y += row_spaccing

    if white_captured:
        x = whole_board_size + 15
        y = 10 + 25
        for piece in white_captured:
            image = images_small.get(str(piece))
            screen.blit(image, (x, y))
            x += piece_spaccing
            if x >= max_x:
                x = whole_board_size + 15
                y += row_spaccing

    pygame.draw.rect(screen, (255, 215, 0), (whole_board_size, SQUARE_SIZE * 6, leftover_width, SQUARE_SIZE * 3), 3)
    if selected:
        r, c = selected
        pygame.draw.rect(screen, (255, 215, 0), (c*SQUARE_SIZE, (7-r)*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

def reset_board():
    global board, turn, selected, message, current_player, white_captured, black_captured

    turn = 1
    selected = None
    current_player = player1
    message =  f"{current_player.name}'s turn"

    white_captured = []
    black_captured = []

    board = create_board()
    draw_board()
    pygame.display.flip()

def mouse_to_board(pos):
    x, y = pos
    if x > NO_OF_BOARD_SQR * SQUARE_SIZE and x < WIDTH and y > NO_OF_BOARD_SQR * SQUARE_SIZE + SQUARE_SIZE and y < HEIGHT:
        print("Resetting board")
        reset_board()
    if x < 0 or x >=  NO_OF_BOARD_SQR * SQUARE_SIZE or y < 0 or y >=  NO_OF_BOARD_SQR * SQUARE_SIZE:
        return None
    col = x // SQUARE_SIZE
    row = y // SQUARE_SIZE
    return (row, col)

def handle_click(pos):
    global turn, selected, message, other_player, current_player
    square = mouse_to_board(pos)
    if not square:
        return 
    r, c = square
    r = 7 - r  # Invert row for display
    print(f"Clicked on square: {square} at position {pos}: {r}, {c}")
    current_player = player1 if turn %2 == 1 else player2 
    other_player = player1 if player2 == current_player else player2
    if not selected:
        piece = board[r][c]
        if piece and piece.colour == current_player.colour:
            selected = (r,c)
            message = f"{current_player.name} selected {str(piece)} {selected}"
            print(message)
        else:
            message = "Select your piece"
    else:
        start = selected
        end = (r, c)
        if make_move(start, end, current_player, board):
            turn += 1
            current_player = player1 if turn %2 == 1 else player2
            message =  f"{current_player.name}'s turn"
        else:
            message = "Invalid move"
        selected = None

if  __name__ == "__main__":

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Basic Chess Game")
    clock = pygame.time.Clock()

    images, images_small = load_images()
    board = create_board()
    whole_board_size = NO_OF_BOARD_SQR * SQUARE_SIZE
    leftover_width = WIDTH - whole_board_size 

    turn = 1
    player1 = Player("Player1", "WHITE")
    player2 = Player("Player2", "BLACK")
    current_player = None
    other_player = None
    selected = None
    message = "White to move"
    check_message = ""
    white_captured = []
    black_captured = []
    draw_board()
    
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                handle_click(event.pos)
        draw_board()
        pygame.display.flip()
    pygame.quit()