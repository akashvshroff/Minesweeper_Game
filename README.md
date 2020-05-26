# Outline:

- A simulation of the beginner version of the classic minesweeper game using PyGame. A more detailed description lies below.

# Purpose:

- Building minesweeper was wholly challenging and engaging. Undertaking the project allowed me to understand the nuances of the pygame module by working with their clock, images and clickable buttons as well as solidify my knowledge of python and programming as I solved the larger logical puzzles that minesweeper comprises of. The project ultimately gave me a very fun game that I wholly enjoy playing and can spend countless hours doing.

# Description:

- The first task of the program is to set a random list of rows and columns where the 10 bombs are going to be planted - the program generates 12 in case of the unlikely scenario that two sets of rows and columns match and then plants 10 bombs in a 2-d array of 0s and Xs (to denote bombs).
- Next the array is analysed to ascertain a key feature of minesweeper, numbers denoting adjacent bombs. This is done in a 4 layered nested for loop that looks at the 3*3 grid surrounding every piece given that it is within the bounds of the grid.

    ```python
    def create_grid_with_bombs_and_nums(self):
            # compute the minesweeper grid with the surrounding bombs
            for r in range(self.rows):
                row_w_count = []
                for c in range(self.cols):
                    if self.initial_grid[r][c] == 'X':
                        row_w_count.append('X')
                        continue
                    else:
                        count = 0
                        for x in range(r-1, r+2):
                            if x < 0 or x > self.rows - 1:
                                continue
                            for y in range(c-1, c+2):
                                if y < 0 or y > self.cols - 1:
                                    continue
                                # print(x, y)
                                if self.initial_grid[x][y] == 'X':
                                    count += 1
                        row_w_count.append(str(count))
                self.final_grid.append(row_w_count)
    ```

- Finally, a board is generated that only consists of '-', arbitrarily chosen. This grid represents what is displayed to the user, with a '-' representing an unopened spot.
- As the game goes on, and tiles are opened, the check_surrounding function is called when an opened tile is empty and opens any tiles surrounding it if the tiles are blank and stopping at one opened number, mimicking the action of the original minesweeper.
- The rest of the program is fairly self-explanatory, with images from the original minesweeper game being used in order to aid authenticity, such as the unopened tiles, the colour scheme, the flag symbol, the bombs and the smiley face.
- Modularity is heavily favoured and a number of boolean variables are used to determine the various states of the game such as game_lost, game_ongoing, first_click and these ensure that certain functions such as game_ended can run smoothly for both scenarios: losing and winning.
- The first_click boolean is used to ensure that the first click of the user is protected as if they click a bomb, the grids are regenerated till their first spot does not coincide with a bomb.
- Moreover, pygame's native time.get_ticks() is used to maintain a timer that is presented to the user.

# P.S - Important Notes:

- All the icons and fonts used for the project are included in the repo.
- The file paths for the pictures are imported into my code and then used.
