import copy

DEBUG = True

'''
The actual board is like:
| ---------------------------------------------------- |
|             AI6 AI5 AI4 AI3 AI2 AI1                  |
| AI_Treasure                           PL_Treasure    |
|             PL1 PL2 PL3 PL4 PL5 PL6                  |
| ---------------------------------------------------- |

And the board representation is:
[ AI1, AI2, AI3, AI4, AI5, AI6, AI_Treasure, PL1, PL2, PL3, PL4, PL5, PL6, PL_Treasure ]

QUICK NOTES:
    board[0:6]   <->   AI Slots
    board[6]     <->   AI Treasure
    board[7:13]  <->   PL Slots
    board[13]    <->   PL Treasure
'''

board = [ 4, 4, 4, 4, 4, 4, 0, 4, 4, 4, 4, 4, 4, 0 ]
turn = 0 #   0 -> AI's turn to play   /   1 -> PL's turn to play

class Node:
    '''
    Node class for creating the game tree of states
    '''
    def __init__(self, state: list, turn_token: int, parent):
        self.parent = parent
        self.children = []
        self.state = state
        self.turn_token = turn_token
    
    def move0(self, slot): # AI MOVES
        board = copy.deepcopy(self.state)
        turn = self.turn_token
        slot_of_the_last_stone = -1
        if board[slot] == 0:
            return Node(board, -1, self) # (turn_token == -1   =>   Invalid Node)
        elif board[slot] == 1:
            board[slot] = 0
            board[slot+1] += 1
            slot_of_the_last_stone = slot+1
        else: # (board[slot] >= 2)
            stones = board[slot]
            board[slot] = 0
            for i in range(slot, slot+stones):
                board[i%14] += 1
            slot_of_the_last_stone = (slot+stones-1)%14

        # RULE 1 ( If last stone went into the treasure, then don't switch turn. Else, switch turn. )
        if slot_of_the_last_stone != 6:
            turn = 1
        # RULE 2
        if slot_of_the_last_stone >= 7 and slot_of_the_last_stone <= 12 and board[slot_of_the_last_stone]%2 == 0:
            board[6] += board[slot_of_the_last_stone]
            board[slot_of_the_last_stone] = 0
        # RULE 3
        if slot_of_the_last_stone >= 0 and slot_of_the_last_stone <= 5 and board[slot_of_the_last_stone] == 1 and board[12-slot_of_the_last_stone] > 0:
            board[6] += board[slot_of_the_last_stone] + board[12-slot_of_the_last_stone]
            board[slot_of_the_last_stone] = 0
            board[12-slot_of_the_last_stone] = 0
        # RULE 4
        if sum(board[0:6]) == 0:
            for i in range(7,13):
                board[6] += board[i]
                board[i] = 0
            return Node(board, 2, self)
        elif sum(board[7:13]) == 0:
            for i in range(0,6):
                board[13] += board[i]
                board[i] = 0
            return Node(board, 2, self)

        return Node(board, turn, self)
    
    def move1(self, slot): # PL MOVES
        board = copy.deepcopy(self.state)
        turn = self.turn_token
        slot_of_the_last_stone = -1
        if board[slot] == 0:
            return Node(board, -1, self) # (turn_token == -1   =>   Invalid Node)
        elif board[slot] == 1:
            board[slot] = 0
            board[slot+1] += 1
            slot_of_the_last_stone = slot+1
        else: # (board[slot] >= 2)
            stones = board[slot]
            board[slot] = 0
            for i in range(slot, slot+stones):
                board[i%14] += 1
            slot_of_the_last_stone = (slot+stones-1)%14

        # RULE 1 ( If last stone went into the treasure, then don't switch turn. Else, switch turn. )
        if slot_of_the_last_stone != 13:
            turn = 0
        # RULE 2
        if slot_of_the_last_stone >= 0 and slot_of_the_last_stone <= 5 and board[slot_of_the_last_stone]%2 == 0:
            board[13] += board[slot_of_the_last_stone]
            board[slot_of_the_last_stone] = 0
        # RULE 3
        if slot_of_the_last_stone >= 7 and slot_of_the_last_stone <= 12 and board[slot_of_the_last_stone] == 1 and board[12-slot_of_the_last_stone] > 0:
            board[13] += board[slot_of_the_last_stone] + board[12-slot_of_the_last_stone]
            board[slot_of_the_last_stone] = 0
            board[12-slot_of_the_last_stone] = 0
        # RULE 4
        if sum(board[0:6]) == 0:
            for i in range(7,13):
                board[6] += board[i]
                board[i] = 0
            return Node(board, 2, self)
        elif sum(board[7:13]) == 0:
            for i in range(0,6):
                board[13] += board[i]
                board[i] = 0
            return Node(board, 2, self)

        return Node(board, turn, self)

    def create_children(self):
        if self.turn_token == 0:
            for i in range(0,6):
                self.children.append(self.move0(i))
        elif self.turn_token == 1:
            for i in range(7,13):
                self.children.append(self.move1(i))
        else: # Children of an invalid node or a game-ending node is unimportant, therefore a dummy node will be appended.
            for i in range(6):    
                self.children.append( Node([], -1, self) )
        
    def calc_value_and_action(self):
        if self.turn_token == 2: # The node is a game-ending node
            return self.state[6] - self.state[13], -1
        elif self.turn_token == -1: # The node is an invalid node
            if self.parent.turn_token == 0:
                return -1000, -1 # Negative Infinity
            elif self.parent.turn_token == 1:
                return 1000, -1
            else:
                print('ERROR: There exists an invalid or a game-ending node that has a child!')
                exit()
        elif self.children == []: # The node is a leaf node
            return self.state[6] - self.state[13], -1
        elif self.turn_token == 0: # It is AI's turn to play
            children_values = []
            for i in range(6):
                val, act = self.children[i].calc_value_and_action()
                children_values.append(val)
            max_child_value = max(children_values)
            act_to_return = -2
            for j in range(6):
                if children_values[j] == max_child_value:
                    act_to_return = j
            return max_child_value, act_to_return
        elif self.turn_token == 1: # It is PL's turn to play
            children_values = []
            for i in range(6):
                val, act = self.children[i].calc_value_and_action()
                children_values.append(val)
            min_child_value = min(children_values)
            act_to_return = -2
            for j in range(6):
                if children_values[j] == min_child_value:
                    act_to_return = j
            return min_child_value, act_to_return
        else:
            print('ERROR: There exists a node in the tree with an undefined turn_token number, which means != -1,0,1,2')
            exit()

def print_board():
    global board
    global turn
    print()
    print('    ', str(board[5]), str(board[4]), str(board[3]), str(board[2]), str(board[1]), str(board[0]))
    print(str(board[6]), '                 ', board[13])
    print('    ', str(board[7]), str(board[8]), str(board[9]), str(board[10]), str(board[11]), str(board[12]))
    print()

def request_move() -> int:
    print('You are playing...')
    return input('Please select a slot to make your move (Like 1, 2, 3, 4, 5 or 6) : ')

def game_over():
    global board
    global turn
    print('GAME OVER!')
    if board[6] > board[13]:
        print('AI WINS!')
    elif board[13] > board[6]:
        print('PLAYER WINS!')
        print('Congratulations!')
    else:
        print('DRAW!')

def next_turn():
    global board
    global turn
    print_board()
    print('----------------------------------------------------------------------------------')
    if sum(board[0:6]) == 0 or sum(board[7:13]) == 0:
        game_over()
    elif turn == 0:
        ai_move()
    elif turn == 1:
        player_move(request_move())
    else:
        print('ERROR: The turn value is invalid!')
        exit()

def player_move(slot):
    global board
    global turn
    if slot not in ['1','2','3','4','5','6']:
        player_move(input('Please provide a valid move (Like 1, 2, 3, 4, 5 or 6) : '))
        return

    slot = int(slot) + 6
    slot_of_the_last_stone = -1
    if board[slot] == 0:
        player_move(input('Please provide a valid slot (Selected slot had no stones in it!) : '))
        return
    elif board[slot] == 1:
        board[slot] = 0
        board[slot+1] += 1
        slot_of_the_last_stone = slot+1
    else: # (board[slot] >= 2)
        stones = board[slot]
        board[slot] = 0
        for i in range(slot, slot+stones):
            board[i%14] += 1
        slot_of_the_last_stone = (slot+stones-1)%14

    # RULE 1 ( If last stone went into the treasure, then don't switch turn. Else, switch turn. )
    if slot_of_the_last_stone != 13:
        turn = 0
    # RULE 2
    if slot_of_the_last_stone >= 0 and slot_of_the_last_stone <= 5 and board[slot_of_the_last_stone]%2 == 0:
        board[13] += board[slot_of_the_last_stone]
        board[slot_of_the_last_stone] = 0
    # RULE 3
    if slot_of_the_last_stone >= 7 and slot_of_the_last_stone <= 12 and board[slot_of_the_last_stone] == 1 and board[12-slot_of_the_last_stone] > 0:
        board[13] += board[slot_of_the_last_stone] + board[12-slot_of_the_last_stone]
        board[slot_of_the_last_stone] = 0
        board[12-slot_of_the_last_stone] = 0
    # RULE 4
    if sum(board[0:6]) == 0:
        for i in range(7,13):
            board[6] += board[i]
            board[i] = 0
    elif sum(board[7:13]) == 0:
        for i in range(0,6):
            board[13] += board[i]
            board[i] = 0
    
    next_turn()

def ai_move():
    global board
    global turn
    
    print('AI is playing...')

    # Creating the tree, depth is 7
    root = Node(board, turn, None)
    root.create_children()
    for i in range(6):
        root.children[i].create_children()
        for j in range(6):
            root.children[i].children[j].create_children()
            for k in range(6):
                root.children[i].children[j].children[k].create_children()
                for l in range(6):
                    root.children[i].children[j].children[k].children[l].create_children()
                    for m in range(6):
                        root.children[i].children[j].children[k].children[l].children[m].create_children()
                        for n in range(6):
                            root.children[i].children[j].children[k].children[l].children[m].children[n].create_children()

    val, act = root.calc_value_and_action()
    board = copy.deepcopy(root.children[act].state)
    turn = root.children[act].turn_token
    print('AI decides to play its slot number ', act+1)

    if DEBUG:
        print('( By the way, AI thinks the value of the position is: ', val, ')')

    next_turn()

def main():
    global board
    global turn
    print('Initial board state is: ')
    print_board()
    start = input('If you want to start the game type 1 and press Enter, else type 0 and press Enter for the computer to start: ')
    if start == '0':
        turn = 0
        ai_move()
    elif start == '1':
        turn = 1
        player_move(request_move())
    else:
        print('    Invalid answer, please provide a valid answer (0 or 1)')
        print('    Restarting the game...')
        main()

if __name__ == '__main__':
    main()