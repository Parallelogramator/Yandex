import random


def create_board(size, mines):
    board = [['[ ]' for _ in range(size)] for _ in range(size)]
    display_board = [['[ ]' for _ in range(size)] for _ in range(size)]
    mine_positions = random.sample(range(size * size), mines)
    for pos in mine_positions:
        x, y = divmod(pos, size)
        board[x][y] = '[*]'
    return board, display_board


def print_board(board):
    for row in board:
        print(' '.join(row))


def make_move(board, display_board, x, y):
    if board[x][y] == '[*]':
        return False
    else:
        display_board[x][y] = '[X]'
        return True


def game():
    size = 5
    mines = 5
    board, display_board = create_board(size, mines)
    while True:
        print_board(display_board)
        x = int(input("Введите номер строки: "))-1
        y = int(input("Введите номер столбца: "))-1
        if not make_move(board, display_board, x, y):
            print("Вы проиграли!")
            for row in board:
                print(' '.join(row))
            break


if __name__ == '__main__':
    game()
