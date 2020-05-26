import pygame
import numpy as np
from collections import namedtuple
import random
import time
from paths import *  # all the image paths


class PlayMinesweeper():
    def __init__(self):
        self.win_width = 480
        self.win_height = 550

        self.start_x = 40
        self.end_x = 400
        self.start_y = 80
        self.end_y = 440

        self.segment_size = 40

        self.rows = 10
        self.cols = 10

        self.bomb_image = pygame.transform.scale(pygame.image.load(
            bomb_path), (self.segment_size - 2, self.segment_size - 2))
        self.flag_image = pygame.transform.scale(pygame.image.load(
            flag_path), (self.segment_size, self.segment_size))
        self.dead_image = pygame.transform.scale(pygame.image.load(
            dead_path), (self.segment_size + 20, self.segment_size + 20))
        self.unopened_image = pygame.transform.scale(
            pygame.image.load(unopened_path), (self.segment_size, self.segment_size))
        self.winner_image = pygame.transform.scale(pygame.image.load(
            winner_path), (self.segment_size + 20, self.segment_size + 20))
        self.reset_image = pygame.transform.scale(pygame.image.load(
            reset_path), (self.segment_size + 20, self.segment_size + 20))

        Colour = namedtuple("Colour", ["r", "g", "b"])
        self.grid_bg_colour = Colour(r=185, g=185, b=185)
        self.screen_bg_colour = Colour(r=117, g=117, b=117)
        self.grid_border_colour = Colour(r=100, g=100, b=100)
        self.full_border_colour = Colour(r=50, g=50, b=50)
        self.red_colour = Colour(r=178, g=34, b=34)
        self.green_colour = Colour(r=0, g=128, b=0)
        self.blue_colour = Colour(r=0, g=0, b=190)
        self.lime_colour = Colour(r=0, g=200, b=0)

        self.win_dimensions = self.win_width, self.win_height

        pygame.init()
        self.screen = pygame.display.set_mode(self.win_dimensions)
        pygame.display.set_caption("Minesweeper")
        self.clock = pygame.time.Clock()
        self.start_time = 0
        self.grid_font = pygame.font.Font(
            r'C:\Users\akush\Desktop\Programming\Projects\Minesweeper\Font\lcd_solid.ttf', 36)
        self.tagged_font = pygame.font.Font(
            r'C:\Users\akush\Desktop\Programming\Projects\Minesweeper\Font\lcd_solid.ttf', 40)
        self.time_font = pygame.font.Font(
            r'C:\Users\akush\Desktop\Programming\Projects\Minesweeper\Font\lcd_solid.ttf', 36)
        self.bottom_font = pygame.font.Font(
            r'C:\Users\akush\Desktop\Programming\Projects\Minesweeper\Font\lcd_solid.ttf', 30)
        self.won_lost_font = pygame.font.Font(
            r'C:\Users\akush\Desktop\Programming\Projects\Minesweeper\Font\lcd_solid.ttf', 60)

        self.display_image = self.reset_image
        self.bombs_tagged = 0
        self.bomb_clicked = False
        self.bomb_x, self.bomb_y = 0, 0
        self.right_clicked = np.full((self.rows, self.cols), False)
        self.initial_grid = []
        self.final_grid = []
        self.display_grid = np.full((self.rows, self.cols), '-')
        self.num_remaining = np.count_nonzero(self.display_grid == '-')
        self.game_lost = False
        self.game_ongoing = None
        self.first_click = True
        self.running = True
        self.curr_time = 0

        self.play_game()

    def randomize_bombs(self):
        # randomly choose rows and cols for the bombs
        rand_rows = random.choices(range(10), k=self.rows+2)
        rand_cols = random.choices(range(10), k=self.cols+2)
        self.rand_bombs = list(zip(rand_rows, rand_cols))
        random.shuffle(self.rand_bombs)

    def create_grid_with_bombs(self):
        # add bombs to the grid
        c = 0
        for i in range(self.rows):
            row_to_add = []
            for j in range(self.cols):
                if (i, j) in self.rand_bombs and c < 10:
                    row_to_add.append('X')
                    c += 1
                else:
                    row_to_add.append(0)
            self.initial_grid.append(row_to_add)

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

    def check_surrounding(self, r, c):
        # check rows above and below, and then break
        for row in range(r, self.rows):  # rows below and including
            for col_bef in range(c, -1, -1):  # before and inclunding
                if self.final_grid[row][col_bef] == '0':
                    self.display_grid[row][col_bef] = '0'
                elif self.final_grid[row][col_bef].isdigit() and self.final_grid[row][col_bef] != 0:
                    self.display_grid[row][col_bef] = self.final_grid[row][col_bef]
                    break
            for col_after in range(c, self.cols):  # after and including
                if self.final_grid[row][col_after] == '0':
                    self.display_grid[row][col_after] = '0'
                elif self.final_grid[row][col_after].isdigit() and self.final_grid[row][col_after] != 0:
                    self.display_grid[row][col_after] = self.final_grid[row][col_after]
                    break
            if np.count_nonzero(self.display_grid[row] == '0') == 0:
                break

        for row in range(r-1, -1, -1):  # rows above and not including
            for col_bef in range(c, -1, -1):  # before and inclunding
                if self.final_grid[row][col_bef] == '0':
                    self.display_grid[row][col_bef] = '0'
                elif self.final_grid[row][col_bef].isdigit() and self.final_grid[row][col_bef] != 0:
                    self.display_grid[row][col_bef] = self.final_grid[row][col_bef]
                    break
            for col_after in range(c, self.cols):  # after not inclunding
                if self.final_grid[row][col_after] == '0':
                    self.display_grid[row][col_after] = '0'
                elif self.final_grid[row][col_after].isdigit() and self.final_grid[row][col_after] != 0:
                    self.display_grid[row][col_after] = self.final_grid[row][col_after]
                    break
            if np.count_nonzero(self.display_grid[row] == '0') == 0:
                break

    def draw_obj(self):
        # draw all the necessary objects on the screen
        pygame.draw.rect(self.screen, self.full_border_colour, [self.start_x, 10, 80, 50])
        self.screen.blit(self.display_image, (205, 10))
        pygame.draw.rect(self.screen, self.full_border_colour, [320, 10, 120, 50])

        pygame.draw.rect(self.screen, self.full_border_colour, [
                         self.start_x-5, self.start_y-5, self.end_x-self.start_x+self.segment_size + 10, self.end_y-self.start_y+self.segment_size + 10], 1)
        pygame.draw.rect(self.screen, self.full_border_colour, [
                         self.start_x-5, self.start_y-5, self.end_x-self.start_x+self.segment_size + 10, self.end_y-self.start_y+self.segment_size + 10], 0)

        for i in range(self.start_x, self.end_x+1, self.segment_size):
            for j in range(self.start_y, self.end_y + 1, self.segment_size):
                self.screen.blit(self.unopened_image, (i, j))
                pygame.draw.rect(self.screen, self.grid_border_colour, [
                                 i, j, self.segment_size, self.segment_size], 1)

        if not self.game_ongoing:
            game_to_start_text = 'CLICK SMILEY TO START.'
            to_start_text = self.bottom_font.render(
                game_to_start_text, True, self.full_border_colour)
            to_start_rec = to_start_text.get_rect(center=(245, 520))
            self.screen.blit(to_start_text, to_start_rec)

    def check_if_to_show(self):
        # check if any number has been clicked and has to be displayed on the screen
        for row in range(self.rows):
            for col in range(self.cols):
                if self.display_grid[row][col] != '-':
                    x = row*self.segment_size + 40
                    y = col*self.segment_size + 80
                    num_disp = self.display_grid[row][col]
                    if int(num_disp) == 0:
                        pygame.draw.rect(self.screen, self.grid_bg_colour, [
                                         x, y, self.segment_size, self.segment_size], 0)
                    elif num_disp.isdigit() and num_disp != '0':
                        if int(num_disp) == 1:
                            col = self.blue_colour
                        elif int(num_disp) == 2:
                            col = self.green_colour
                        else:
                            col = self.red_colour
                        pygame.draw.rect(self.screen, self.grid_bg_colour, [
                                         x, y, self.segment_size, self.segment_size], 0)
                        grid_text = self.grid_font.render(num_disp, True, col)
                        grid_rec = grid_text.get_rect(center=(x+20, y+22))
                        self.screen.blit(grid_text, grid_rec)

    def check_tagged(self):
        # check if anything has been tagged and add the flag if tagged - if a bomb is tagged then it updates a counter
        for row in range(self.rows):
            for col in range(self.cols):
                if self.right_clicked[row][col]:
                    x = row*self.segment_size + 40
                    y = col*self.segment_size + 80
                    self.screen.blit(self.flag_image, (x, y))

        num_tagged = np.count_nonzero(self.right_clicked == True)
        if num_tagged > 10:
            num_tagged = 10 - num_tagged
        tagged_disp = '{:02}'.format(num_tagged)
        tagged_text = self.tagged_font.render(tagged_disp, True, self.red_colour)
        tagged_text_rec = tagged_text.get_rect(
            center=(self.start_x + self.segment_size, self.segment_size - 3))
        self.screen.blit(tagged_text, tagged_text_rec)

    def show_time(self):
        if self.game_ongoing:
            if self.start_time:
                self.curr_time = (pygame.time.get_ticks() - self.start_time)//1000
            else:
                self.curr_time = 0
        time_text = '{:02}:{:02}'.format(self.curr_time//60, self.curr_time % 60)
        time_disp = self.time_font.render(time_text, True, self.red_colour)
        time_rect = time_disp.get_rect(center=(380, 35))
        self.screen.blit(time_disp, time_rect)

    def clicked_btn(self, pos, event_type):

        if 205 <= pos[0] <= 265 and 10 <= pos[1] <= 70:
            self.initialise_game()

        if self.game_ongoing:
            if self.start_x <= pos[0] <= self.end_x + self.segment_size and self.start_y <= pos[1] <= self. end_y + self.segment_size:
                row_clicked = pos[0]//self.segment_size - 1  # border = 40 // segment_size
                col_clicked = pos[1]//self.segment_size - 2  # border = 80 // segment_size
                if event_type == 1:
                    if self.final_grid[row_clicked][col_clicked] == 'X':
                        if not self.first_click:
                            self.bomb_clicked = True
                            self.game_lost = True
                            self.bomb_x, self.bomb_y = row_clicked, col_clicked
                            return
                        else:
                            while True:
                                for event in pygame.event.get():
                                    if event.type == pygame.QUIT:
                                        pygame.quit()
                                        return
                                self.randomize_bombs()
                                self.create_grid_with_bombs()
                                self.create_grid_with_bombs_and_nums()
                                if self.final_grid[row_clicked][col_clicked] == 'X':
                                    continue
                                else:
                                    self.first_click = False
                                    break

                    elif self.final_grid[row_clicked][col_clicked].isdigit() and self.final_grid[row_clicked][col_clicked] != '0':
                        self.display_grid[row_clicked][col_clicked] = self.final_grid[row_clicked][col_clicked]
                    else:
                        self.check_surrounding(row_clicked, col_clicked)
                elif event_type == 3:
                    # allows something tagged to be reset
                    self.right_clicked[row_clicked][col_clicked] = False if self.right_clicked[row_clicked][col_clicked] else True
                    if (row_clicked, col_clicked) in self.rand_bombs:
                        self.bombs_tagged += 1

    def game_ended_screen(self):
        # the game has ended - either won or lost
        for row in range(self.rows):
            for col in range(self.cols):
                x = row*self.segment_size + 40
                y = col*self.segment_size + 80
                num_disp = self.final_grid[row][col]
                if num_disp == 'X':
                    pygame.draw.rect(self.screen, self.grid_bg_colour, [
                                     x, y, self.segment_size, self.segment_size], 0)
                    # if those exist then the game has been lost
                    if self.game_lost and (row, col) == (self.bomb_x, self.bomb_y):
                        pygame.draw.rect(self.screen, self.red_colour, [
                                         x, y, self.segment_size, self.segment_size], 0)
                    pygame.draw.rect(self.screen, self.grid_border_colour, [
                                     x, y, self.segment_size, self.segment_size], 1)
                    color = self.full_border_colour
                    self.screen.blit(self.bomb_image, (x, y))
                    continue
                elif int(num_disp) == 0:
                    pygame.draw.rect(self.screen, self.grid_bg_colour, [
                                     x, y, self.segment_size, self.segment_size], 0)
                    pygame.draw.rect(self.screen, self.grid_border_colour, [
                                     x, y, self.segment_size, self.segment_size], 1)
                    continue
                elif num_disp.isdigit() and num_disp != '0':
                    if int(num_disp) == 1:
                        color = self.blue_colour
                    elif int(num_disp) == 2:
                        color = self.green_colour
                    else:
                        color = self.red_colour
                    pygame.draw.rect(self.screen, self.grid_bg_colour, [
                                     x, y, self.segment_size, self.segment_size], 0)
                pygame.draw.rect(self.screen, self.grid_border_colour, [
                                 x, y, self.segment_size, self.segment_size], 1)
                text = self.grid_font.render(num_disp, True, color)
                rec = text.get_rect(center=(x+20, y+22))
                self.screen.blit(text, rec)
        if self.game_lost:
            tagged_disp = 'RIP'
        else:
            tagged_disp = 'GG'
        tagged_text = self.tagged_font.render(tagged_disp, True, self.red_colour)
        tagged_text_rec = tagged_text.get_rect(center=(self.start_x + 40, 35))
        self.screen.blit(tagged_text, tagged_text_rec)

    def game_ended(self):
        self.game_ongoing = False
        if self.game_lost:
            self.display_image = self.dead_image
            bold_text = 'YOU DIED.'
            colour_to_disp = self.red_colour
        else:
            bold_text = 'YOU WON!'
            self.display_image = self.winner_image
            colour_to_disp = self.lime_colour
        bold_text_obj = self.won_lost_font.render(bold_text, True, self.full_border_colour)
        bold_text_rect = bold_text_obj.get_rect(center=(self.win_width//2 + 1, self.win_height//2))
        self.screen.fill(colour_to_disp)
        pygame.display.update()
        time.sleep(0.8)
        self.screen.blit(bold_text_obj, bold_text_rect)
        pygame.display.update()
        time.sleep(2)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    break
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    self.clicked_btn(pos, 1)
            self.screen.fill(self.screen_bg_colour)
            self.draw_obj()
            self.show_time()
            self.game_ended_screen()
            pygame.display.update()
            self.clock.tick(30)

    def initialise_game(self):
        # resets the game and resets the timer
        self.curr_time = 0
        self.running = True
        self.display_image = self.reset_image
        self.bombs_tagged = 0
        self.bomb_clicked = False
        self.bomb_x, self.bomb_y = 0, 0
        self.right_clicked = np.full((self.rows, self.cols), False)
        self.initial_grid = []
        self.final_grid = []
        self.display_grid = np.full((self.rows, self.cols), '-')
        self.num_remaining = np.count_nonzero(self.display_grid == '-')
        self.game_lost = False
        self.game_ongoing = True
        self.first_click = True
        self.randomize_bombs()
        self.create_grid_with_bombs()
        self.create_grid_with_bombs_and_nums()
        self.start_time = pygame.time.get_ticks()
        self.play_game()

    def play_game(self):
        while self.running:
            if self.bombs_tagged >= self.num_remaining:
                self.game_lost = False
                self.game_ended()
                break
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    type = event.button
                    self.clicked_btn(pos, type)
                    if self.game_ongoing:
                        self.first_click = False
                self.screen.fill(self.screen_bg_colour)
                self.draw_obj()
                self.show_time()
                if self.bomb_clicked:
                    self.game_lost = True
                    self.game_ended()
                    break
                self.check_if_to_show()
                self.check_tagged()
                self.num_remaining = np.count_nonzero(self.display_grid == '-')
                pygame.display.update()
                self.clock.tick(30)


def main():
    try:
        game = PlayMinesweeper()
    except:
        pass


if __name__ == '__main__':
    main()
