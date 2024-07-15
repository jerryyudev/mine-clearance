import pygame
import random
import sys

# 初始化Pygame
pygame.init()

# 设置颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (192, 192, 192)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# 设置游戏窗口大小
WIDTH = 400
HEIGHT = 500  # 为了放置计时器和其他信息
INFO_HEIGHT = 50
WINDOW_SIZE = [WIDTH, HEIGHT]
screen = pygame.display.set_mode(WINDOW_SIZE)

# 设置标题
pygame.display.set_caption("扫雷游戏")

# 定义常量
MARGIN = 5
CELL_SIZE = 20
GRID_SIZE = 16  # 修改为16x16的网格，总共有256个方块
MINES_COUNT = 40  # 设置40个地雷

# 创建网格
grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
revealed = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
mines = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
flags = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# 放置地雷
for _ in range(MINES_COUNT):
    x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
    while mines[x][y]:
        x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
    mines[x][y] = True

# 计算每个单元格周围的地雷数量
for row in range(GRID_SIZE):
    for col in range(GRID_SIZE):
        if not mines[row][col]:
            count = 0
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if 0 <= row + i < GRID_SIZE and 0 <= col + j < GRID_SIZE:
                        if mines[row + i][col + j]:
                            count += 1
            grid[row][col] = count

# 主游戏循环
done = False
clock = pygame.time.Clock()
start_ticks = pygame.time.get_ticks()  # 开始计时
game_over = False
game_won = False
show_hint = False
hint_start_ticks = 0

# 按钮位置和大小
button_x = WIDTH // 2 + 50
button_y = 10
button_width = 100
button_height = 30

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if not game_over:
                column = (pos[0] - MARGIN) // (CELL_SIZE + MARGIN)
                row = (pos[1] - INFO_HEIGHT - MARGIN) // (CELL_SIZE + MARGIN)
                if 0 <= row < GRID_SIZE and 0 <= column < GRID_SIZE:
                    if event.button == 1:  # 左键点击
                        if not flags[row][column]:
                            revealed[row][column] = True
                            if mines[row][column]:
                                game_over = True  # 玩家点击了地雷，游戏结束
                                end_ticks = pygame.time.get_ticks()  # 结束计时
                    elif event.button == 3:  # 右键点击
                        if not revealed[row][column]:
                            flags[row][column] = not flags[row][column]
            # 检查是否点击了提示按钮
            if button_x <= pos[0] <= button_x + button_width and button_y <= pos[1] <= button_y + button_height:
                show_hint = True
                hint_start_ticks = pygame.time.get_ticks()

    screen.fill(BLACK)

    # 绘制信息区
    pygame.draw.rect(screen, WHITE, [0, 0, WIDTH, INFO_HEIGHT])

    # 绘制网格
    for row in range(GRID_SIZE):
        for column in range(GRID_SIZE):
            color = GRAY
            if revealed[row][column]:
                if mines[row][column]:
                    color = RED
                else:
                    color = WHITE
            elif flags[row][column]:
                color = GREEN
            elif show_hint and mines[row][column]:
                color = BLUE
            pygame.draw.rect(screen, color,
                             [(MARGIN + CELL_SIZE) * column + MARGIN,
                              (MARGIN + CELL_SIZE) * row + INFO_HEIGHT + MARGIN,
                              CELL_SIZE, CELL_SIZE])

            if revealed[row][column] and not mines[row][column] and grid[row][column] > 0:
                font = pygame.font.Font(None, 36)
                text = font.render(str(grid[row][column]), True, BLACK)
                screen.blit(text, [(MARGIN + CELL_SIZE) * column + MARGIN + 5,
                                   (MARGIN + CELL_SIZE) * row + INFO_HEIGHT + MARGIN + 5])

    # 绘制计时器
    if not game_over:
        seconds = (pygame.time.get_ticks() - start_ticks) // 1000
    else:
        seconds = (end_ticks - start_ticks) // 1000  # 使用结束时的时间

    font = pygame.font.Font(None, 36)
    timer_text = font.render(f"Time: {seconds}", True, BLACK)
    screen.blit(timer_text, [10, 10])

    # 检查是否赢得游戏
    if not game_over:
        correct_flags = all(flags[row][col] == mines[row][col] for row in range(GRID_SIZE) for col in range(GRID_SIZE))
        flag_count = sum(sum(row) for row in flags)
        if correct_flags and flag_count == MINES_COUNT:
            game_won = True
            game_over = True
            end_ticks = pygame.time.get_ticks()  # 结束计时

    # 显示所有地雷
    if game_over:
        for row in range(GRID_SIZE):
            for column in range(GRID_SIZE):
                if mines[row][column]:
                    pygame.draw.rect(screen, RED,
                                     [(MARGIN + CELL_SIZE) * column + MARGIN,
                                      (MARGIN + CELL_SIZE) * row + INFO_HEIGHT + MARGIN,
                                      CELL_SIZE, CELL_SIZE])

        # 显示胜利或失败信息
        result_text = "You Win!" if game_won else "Game Over"
        result_color = GREEN if game_won else RED
        result_display = font.render(result_text, True, result_color)
        screen.blit(result_display, [WIDTH // 2 - 50, HEIGHT - 40])

    # 显示提示按钮
    pygame.draw.rect(screen, WHITE, [button_x, button_y, button_width, button_height])
    hint_text = font.render("Hint", True, BLACK)
    screen.blit(hint_text, [button_x + 20, button_y + 5])

    # 检查提示时间是否超过5秒
    if show_hint and (pygame.time.get_ticks() - hint_start_ticks) > 5000:
        show_hint = False

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
