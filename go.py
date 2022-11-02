import copy

WIDTH = 20
BLACK_STONE = 1
WHITE_STONE = 2


class Board:
    def __init__(self, height, width, handicap):
        self.height = height
        self.width = width
        self.initial_handicap = handicap
        self.points = [[Point() for _ in range(width + 1)] for _ in range(height + 1)]
        self.game_record = GameRecord(width, height)
        self.recordPoints = []
        self.init_board()

    def init_board(self):
        self.P1 = Player(1)
        self.P2 = Player(2)
        self.actualPlayer = self.P1
        self.handicap = 0
        for x in range(1, self.width + 1):
            for y in range(1, self.height + 1):
                self.points[x][y] = Point(self, x, y)

    def is_in_board(self, x, y):
        return 0 < x < self.width and 0 < y < self.height

    def point_is_in_board(self, point):
        x, y = point.x, point.y
        return self.is_in_board(x, y)

    def get_point(self, x, y):
        if self.is_in_board(x, y):
            return self.points[x][y]
        else:
            return None

    def play(self, x, y, player):
        point = self.get_point(x, y)
        if point is None:
            print('落子超出了棋盘范围，请重新落子')
            return False
        return self.play_in_board(point, player, True)

    def play_in_board(self, point, player, handle_ko):
        current_turn = None
        ko = False

        if self.point_is_in_board(point) is False:
            return False
        if point.group is not None:
            return False
        captured_stones, captured_groups = None, None
        if handle_ko:
            captured_stones, captured_groups = set(), set()
        adj_groups = point.get_adjacent_groups()
        new_group = Group(point, player)
        point.group = new_group
        for group in adj_groups:
            if group.owner == player:
                new_group.add(group, point)
            else:
                group.remove_liberties(point)
                if len(group.liberties) == 0:
                    if handle_ko:
                        captured_stones.update(group.stones)
                        captured_groups.add(Group(group))
                    group.die()

        if handle_ko:
            current_turn = self.game_record.get_last_turn().to_next(point.x, point.y, player.get_identifier(),
                                                                    captured_stones)
            for turn in self.game_record.get_turns():
                if turn is current_turn:
                    ko = True
                    break
            if ko:
                for chain in captured_stones:
                    for stone in chain.stones:
                        stone.group = chain
        if len(new_group.liberties) == 0 or ko:
            for chain in point.get_adjacent_groups():
                chain.liberites.add(point)
            point.group = None
            return False

        for stone in new_group.stones:
            stone.group = new_group
        if handle_ko:
            self.game_record.apply(current_turn)
        self.recordPoints.append(point)
        return True

    def change_player(self, undo):
        if self.handicap < self.initial_handicap and undo is False:
            self.handicap += 1
        elif undo is True and self.game_record.nbr_preceding() < self.initial_handicap:
            self.handicap -= 1
        else:
            if self.actualPlayer == self.P1:
                self.actualPlayer = self.P2
                print('Changing player for P2')
            else:
                self.actualPlayer = self.P1
                print('Changing player for P1')

    def free_intersections(self):
        for i in range(1, self.width):
            for j in range(1, self.height):
                point = self.get_point(i, j)
                point.group = None

    def take_game_turn(self, game_turn, one, two):
        self.free_intersections()
        board_state = game_turn.board_state
        for x in range(1, self.width + 1):
            for y in range(1, self.height + 1):
                state = board_state[x][y]
                if state == BLACK_STONE:
                    self.play_in_board(self.get_point(x, y), one, False)
                elif state == WHITE_STONE:
                    self.play_in_board(self.get_point(x, y), two, False)

    def get_player(self):
        return self.actualPlayer

    def next_player(self):
        self.change_player(False)

    def precedent_player(self):
        self.change_player(True)

    def undo(self):
        if self.game_record.has_preceding():
            self.game_record.undo()
            last = self.game_record.get_last_turn()
            self.take_game_turn(last, self.P1, self.P2)
            self.precedent_player()
            return True
        else:
            return False

    def redo(self):
        if self.game_record.has_following():
            self.game_record.redo()
            next_turn = self.game_record.get_last_turn()
            self.take_game_turn(next_turn, self.P1, self.P2)
            self.next_player()

    def to_string(self):
        string_board = ''
        for i in range(1, self.width):
            for j in range(1, self.height):
                cross = self.points[i][j]
                if cross.group is None:
                    string_board += '· '
                else:
                    if cross.group.owner.identifier == 1:
                        string_board += '1 '
                    else:
                        string_board += '2 '
            string_board += '\n'
        return string_board


class Player:
    def __init__(self, identifier):
        self.identifier = identifier

    def get_identifier(self):
        return self.identifier


class Point:
    def __init__(self, *args):
        if len(args) == 3:
            self.board = args[0]
            self.x = args[1]
            self.y = args[2]
            self.group = None

        elif len(args) == 4:
            print(4)
            self.color = args[0]
            self.x = args[1]
            self.y = args[2]
            self.step = args[3]

    # 拿到相邻棋子所属的组
    def get_adjacent_groups(self):
        adjacent_groups = set()
        dx, dy = [-1, 0, 1, 0], [0, 1, 0, -1]
        for i in range(0, len(dx)):
            new_x = self.x + dx[i]
            new_y = self.y + dy[i]
            if self.board.is_in_board(new_x, new_y):
                adj_point = self.board.get_point(new_x, new_y)
                if adj_point.group is not None:
                    adjacent_groups.add(adj_point.group)

        return adjacent_groups

    def get_empty_groups(self):
        empty_groups = []
        dx, dy = [-1, 0, 1, 0], [0, 1, 0, -1]
        for i in range(0, len(dx)):
            new_x = self.x + dx[i]
            new_y = self.y + dy[i]
            if self.board.is_in_board(new_x, new_y):
                adj_point = self.board.get_point(new_x, new_y)
                if adj_point.group is None:
                    empty_groups.append(adj_point)

        return empty_groups


class Group:
    def __init__(self, *args):
        if len(args) == 1:
            self.stones = set(args[0].stones)
            self.liberties = set(args[0].liberties)
            self.owner = args[0].owner
        elif len(args) == 2:
            self.stones = set()
            self.stones.add(args[0])
            self.owner = args[1]
            self.liberties = set(args[0].get_empty_groups())
        elif len(args) == 3:
            self.stones = args[0]
            self.liberties = args[1]
            self.owner = args[2]

    def add(self, group, played_stones):
        self.stones.update(group.stones)  # 一个集合添加另一个集合的所有元素
        self.liberties.update(group.liberties)
        self.liberties.remove(played_stones)

    def remove_liberties(self, played_stones):
        new_group = Group(self.stones, self.liberties, self.owner)
        new_group.liberties.remove(played_stones)

    def die(self):
        for rolling_stone in iter(self.stones):
            rolling_stone.group = None
            adjacent_groups = rolling_stone.get_adjacent_groups()
            for group in iter(adjacent_groups):
                group.liberties.add(rolling_stone)


class GameTurn:
    def __init__(self, *args):
        if len(args) == 2:
            self.board_state = [[0 for _ in range(args[0] + 1)] for _ in range(args[1] + 1)]
            self.x, self.y = -1, -1
        elif len(args) == 5:
            width = len(args[0].board_state)
            height = len(args[0].board_state[0])
            self.board_state = [[0 for _ in range(width + 1)] for _ in range(height + 1)]
            for i in range(width):
                self.board_state[i] = copy.deepcopy(args[0].board_state[i])
            self.x, self.y = args[1], args[2]
            if args[1] >= 0 and args[2] >= 0:
                self.board_state[args[1]][args[2]] = args[3]
            for point in args[4]:
                self.board_state[point.x][point.y] = 0

    def to_next(self, x, y, player_id, free_points):
        return GameTurn(self, x, y, player_id, free_points)

    def get_board_state(self):
        return self.board_state


class GameRecord:
    def __init__(self, width, height):
        self.preceding = Stack()
        self.following = Stack()
        first = GameTurn(width, height)
        self.apply(first)

    def apply(self, turn):
        self.preceding.push(turn)
        self.following.clear()

    def has_preceding(self):
        return self.preceding.size() > 1

    def nbr_preceding(self):
        return self.preceding.size() - 1

    def has_following(self):
        return self.following.size() > 0

    def undo(self):
        if self.preceding.size() > 1:
            self.following.push(self.preceding.pop())

    def redo(self):
        if self.following.size() > 0:
            self.preceding.push(self.following.pop())

    def get_last_turn(self):
        if self.preceding.size() > 0:
            return self.preceding.peek()
        else:
            return GameTurn(WIDTH, WIDTH)

    def get_turns(self):
        return self.preceding

    def get_size(self):
        return self.preceding.size()


class Stack:
    def __init__(self, max_size=9999):
        self.items = []
        self.max_size = max_size
        self.n, self.a, self.b = 0, 0, 1

    def is_empty(self):
        return self.items == []

    def peek(self):
        return self.items[len(self.items) - 1]

    def size(self):
        return len(self.items)

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def clear(self):
        return self.items.clear()

    def __iter__(self):
        return self

    def __next__(self):
        if self.n < self.max_size:
            out = self.b
            self.a, self.b = self.b, self.a + self.b
            self.n = self.n + 1
            return out
        raise StopIteration()


if __name__ == '__main__':
    board_play = Board(19, 19, 0)
    print("1代表黑棋 2代表白棋 输入999后退出" + "\n" + "坐标x为列 坐标y为行" + "\n" + "该黑棋下啦")
    while True:
        print('请输入x坐标')
        index_x = int(input())
        if index_x == 999:
            break
        print('请输入y坐标')
        index_y = int(input())
        player_ = board_play.get_player()
        if board_play.play(index_x, index_y, player_) is True:
            print('正常落子')
            board_play.next_player()
        else:
            print('这里不可以落子')
        print(board_play.to_string())
