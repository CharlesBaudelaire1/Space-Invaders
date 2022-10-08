import pygame
import random

pygame.init()
RSC = {
    'title': 'Space Invaders',
    'img': {
        'background': 'resources/img/background.png',
        'icon': 'resources/img/ufo.png',
        'player': 'resources/img/player.png',
        'enemy': 'resources/img/enemy.png',
        'bullet': 'resources/img/bullet.png'
    },
    'sound': {
    }
}

FPS = 24
restart_font = pygame.font.SysFont('None', 32)

class Enemy:
    Y_START_POSITION = 30

    def __init__(self, bound_size):
        self.display_width, self.display_height = bound_size
        self.bound_rect = pygame.Rect(0, 0, self.display_width, self.display_height)

        self.img = pygame.image.load(RSC['img']['enemy'])
        self.width = self.img.get_width()
        self.height = self.img.get_height()

        self.x = random.randint(0, self.display_width)
        self.y = self.Y_START_POSITION
        self.dx = random.randint(-2, 3) / 10
        self.dy = random.randint(1, 3) / 10
       # self.dx = 0.1
        #self.dy = 0.1

    def model_update(self):
        # return in_bounds status
        self.x += self.dx
        self.y += self.dy

        return self.bound_rect.contains(self.x, self.y, self.width,  self.height)

    def redraw(self, display):
        display.blit(self.img, (self.x, self.y))

    def event_procces(self):
     pass

class Player:
    GAP = 10  # расстояние до низа экрана
    SPEED = 0.5

    def __init__(self, bound_size):
        self.bullet = None
        self.display_width, self.display_height = bound_size

        self.img = pygame.image.load(RSC['img']['player'])
        self.width = self.img.get_width()
        self.height = self.img.get_height()

        self.x = self.display_width // 2 - self.width // 2
        self.y = self.display_height - self.height - self.GAP
        self.dx = 0

    def model_update(self):
        self.x += self.dx
        # не дадим игроку выходить за пределы окна
        if self.x < 0:
            self.x = 0
        if self.x > self.display_width - self.width:
            self.x = self.display_width - self.width

    def redraw(self, display):
        display.blit(self.img, (self.x, self.y))

    def event_process(self, event):
        # нажали клавишу - поехали
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.dx = -Player.SPEED
            elif event.key == pygame.K_RIGHT:
                self.dx = Player.SPEED
        # отпустили клавишу - остановились
        if event.type == pygame.KEYUP:
            self.dx = 0
        #  кликнули мышкой - выстрелили
        if event.type == pygame.MOUSEBUTTONDOWN:
            key = pygame.mouse.get_pressed()
            if key[0] and not self.bullet:
                self.bullet = Bullet(self.display_height, self.display_width, self.x, self.y)


class Bullet:
    def __init__(self, display_height, display_width, x, y):
            self.display_height = display_height
            self.display_width = display_width
            self.img = pygame.image.load(RSC['img']['bullet'])
            self.height = self.img.get_height()
            self.width = self.img.get_width()
            self.bound_rect = pygame.Rect(0, 0, self.display_width, self.display_height)
            self.x = x
            self.y = y - self.height
            self.dy = 1
        # return self.x, self.y
    def model_update(self):
            self.y -= self.dy
            return self.bound_rect.contains(self.x, self.y, self.width, self.height)

    def redraw(self, display):
        display.blit(self.img, (self.x, self.y))


class Game:
    def __init__(self, size):
        self.width, self.height = size
        self.rect = (0, 0, self.width, self.height)

        self.player = Player(size)
        self.enemy = None
        self.over = False
    def model_update(self):
        self.player.model_update()
        if self.enemy:
            if not self.enemy.model_update():
                # вылетел за границы
                self.enemy = None
        elif not self.over:
            self.enemy = Enemy((self.width, self.height))
        if self.player.bullet:
            if not self.player.bullet.model_update():
                self.player.bullet = None
    def redraw(self, display):
        display.fill((0, 0, 0), self.rect)
        self.player.redraw(display)
        if self.enemy:
            self.enemy.redraw(display)
          #  Если есть пуля - перерисовать
        if self.player.bullet:
            self.player.bullet.redraw(display)
          # Игра окончена - вывести надпись и удалить врага
        if self.over:
            restart_surface = restart_font.render("Press space to restart", True, (255, 0, 0))
            restart_rect = restart_surface.get_rect(center=(800 / 2, 600 / 2))
            display.blit(restart_surface, restart_rect)
            self.enemy = None
        pygame.display.update()

    def event_process(self, event,display):
        self.player.event_process(event)
        
        # Пуля попадет во врага - пуля с врагом исчезают
        if self.player.bullet and self.enemy:
            rect_enemy = pygame.Rect(self.player.bullet.x, self.player.bullet.y , self.player.bullet.width, self.player.bullet.height)
            rect_other = pygame.Rect(self.enemy.x, self.enemy.y, self.enemy.width, self.enemy.height)
            if rect_enemy.colliderect(rect_other):
                self.enemy = None
                self.player.bullet = None
                
        # Игрок столкнется с врагом - игра окончена
        if self.enemy:
            rect_enemy = pygame.Rect(self.enemy.x, self.enemy.y, self.enemy.width, self.enemy.height)
            rect_other = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
            if rect_enemy.colliderect(rect_other):
               self.enemy = None
               self.over = True
               self.player.dx = 0



class Application:
    def __init__(self):
        pygame.init()
        random.seed(10)

        self.width = 800
        self.height = 600
        self.size = (self.width, self.height)

        self.display = pygame.display.set_mode(self.size)
        pygame.display.set_caption(RSC['title'])
        pygame.display.set_icon(pygame.image.load(RSC['img']['icon']))

        self.running = False

    def run(self):
        # приложение уже запущено
        if self.running:
            return
        self.running = True
        clock = pygame.time.Clock()

        game = Game(self.size)

        while self.running:
            game.model_update()
            game.redraw(self.display)
            for event in pygame.event.get():
                if self.event_close_application(event):
                    self.running = False
                 
                 
                if self.restart(event):
                    game.over = False
                   
                # Игра окончена - пропустить обработку событий
                if game.over:
                    continue
                game.event_process(event, self.display)
                clock.tick(FPS)
     # Если нажат пробел - перезапустить игру        
    def restart(self,event):
        if event.type == pygame.KEYDOWN:
             return event.key == pygame.K_SPACE



    def event_close_application(self, event):
        return event.type == pygame.QUIT


app = Application()
app.run()
