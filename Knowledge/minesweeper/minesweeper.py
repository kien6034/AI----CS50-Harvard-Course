import itertools
import random

#handle the game play
class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        self.safe_moves = set()
      

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines

class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        if len(self.cells) == self.count:
            return self.cells
        return  None

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells

        return None

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -=1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)

#infering which moves to make base on knowledge
class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width
          #all possible moves
        self.all_possible_cells = set()

        for i in range (height):
            for j in range(width):
                self.all_possible_cells.add((i, j))

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count): # a cell is represetn as a tuple (i,j)
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        #mark the cell as a move that has been made
        self.moves_made.add(cell)

        #mark the cell as safe
        self.mark_safe(cell)
        
        new_knowledge_cells = []

        #add a new sentence to the AI's knowledge base based on the value of 'cell' and 'count'
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] -1, cell[1] + 2):
                #ignore the self itslef
                if cell == (i, j):
                    continue

                #updaet cell if it's not in move made and safe cell
                if 0 <= i < self.height and 0<= j < self.width: # in bound
                    if(i,j) not in self.moves_made and (i, j) not in self.safes:
                        new_knowledge_cells.append((i, j))
        
        if(len(new_knowledge_cells) != 0):
            self.knowledge.append(Sentence(new_knowledge_cells, count))

        #mark additional cells as safe or mines if it can be conclued base on KB
        knowledge_to_iterate = self.knowledge.copy()

        
        for sentence in knowledge_to_iterate:
            known_safes = sentence.known_safes()
            known_mines = sentence.known_mines()

            if sentence.cells == None:
                self.knowledge.remove(sentence)

            if known_safes:
                #update cell
                self.safes.update(known_safes)
                #remove sentence from KB if it is known has full of mines or no mines
                self.knowledge.remove(sentence)
                

            if known_mines:
                self.knowledge.remove(sentence)
                for mine_cell in known_mines.union(self.mines):
                    self.mark_mine(mine_cell)
            
            #add inference from KB
        for sentence in knowledge_to_iterate:
            for other in knowledge_to_iterate:
                if sentence.cells != other.cells:
                    if sentence.cells.issubset(other.cells):
                        self.knowledge.append(Sentence(other.cells - sentence.cells, (other.count - sentence.count)))
                        print('************************************')
                        print(f'Inferecing from existing knowledge: => {other.cells - sentence.cells}\n KB1: {other.cells}, \n KB2:{sentence.cells}')
                        
                        #remove parent sentences
                        if sentence in self.knowledge:
                            self.knowledge.remove(sentence)
                        if other in self.knowledge:
                            self.knowledge.remove(other)
                    
        print("Knowledge Base:")
        for sentence in self.knowledge:
            print(sentence)
        print("=======================================================")
        if self.safes:
            print(f'Cells that are known to be safe {self.safes}')
        
        if self.mines:
            print(f'Cells that are known to be mines {self.mines}')

        #add new sentences to the KB if it can be infering from existing knowledge
                    

       

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """

        self.safe_moves = self.safes - self.moves_made

        if len(self.safe_moves) > 0:
            return random.choice(tuple(self.safe_moves))
        
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        freeSets = self.all_possible_cells - self.moves_made - self.mines
       
        if len(freeSets) >0:
            return random.choice(tuple(freeSets))
        else:
            return None
