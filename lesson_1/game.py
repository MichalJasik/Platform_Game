import pygame, os, random, time
import game_module as gm
from pygame.locals import *
from pygame import mixer

os.environ['SDL_VIDEO_CENTERED'] = '1'          # centrowanie okna
mixer.init() # #inicjalizacja dzwieku)
pygame.mixer.pre_init(44100, -16,2, 512)
pygame.init() #inicjalizacja wszelkich modolow dzwieku, grafika

shot= pygame.mixer.Sound("shot.mp3")
shot.set_volume(0.3)
jump=pygame.mixer.Sound("jump.wav")
jump.set_volume(0.5)
loss_life= pygame.mixer.Sound("game_over.wav")
loss_life.set_volume(0.3)

#ikonka aplikacji
gameIcon = pygame.image.load("mario.png")
pygame.display.set_icon(gameIcon)

## ustawienia ekranu i gry
screen = pygame.display.set_mode(gm.SIZESCREEN) #budujemy okno wykorzystujac funkcje pygame
pygame.display.set_caption('Gra Platformowa by Michal Jasik') #prosty napis
clock = pygame.time.Clock() #budujemy obiekt zegara ktorego celem jest zwolnienie petli


# klasa gracza
class Player(pygame.sprite.Sprite):
    def __init__(self, file_image):
        super().__init__() #wywolujemy konstruktor klasy bazowej
        self.image = file_image #przypisujemy zaladowana grafike
        self.rect = self.image.get_rect() #z obrazka ktory wczytamy budujemy obiekt prostokata
        self.movement_x = 0 # o ile pikseli zmieniona jest pozycja
        self.movement_y = 0
        self.press_left = False
        self.press_right = False
        self.rotate_left = False
        self._count = 0
        self.level = None
        self.lifes = 3
        self.items = {}


    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def turn_left(self): # jak bede miec wcisniety klawisz lewa strzalka to w iagu 1s przesunie mi sie obraz 300razy
        self.rotate_left = True
        self.movement_x = -5

    def turn_right(self):
        self.rotate_left = False
        self.movement_x = 5

    def stop(self):
        self.movement_x = 0

    def jump(self):
        self.rect.y += 2
        colliding_platforms = pygame.sprite.spritecollide(self, self.level.set_of_platforms, False) #skakac tylko na platformie
        self.rect.y -= 2
        if colliding_platforms:
            self.movement_y = -12
        jump.play()

    def shoot(self):
        if self.items.get("shotgun", False):
            b= Bullet(gm.BULLET_LIST, self.rotate_left ,self.rect.centerx , self.rect.centery+20)
            self.level.set_of_bullet.add(b)
            shot.play()

    def update(self):
        self._gravitation() #wywolanie grawitacji

        # -------ruch w poziomie--------
        self.rect.x += self.movement_x

        # animacje
        if self.movement_x > 0:
            self._move(gm.PLAYER_WALK_LIST_R)
        if self.movement_x < 0:
            self._move(gm.PLAYER_WALK_LIST_L)


        # kolizje z platformami
        colliding_platforms = pygame.sprite.spritecollide(self, self.level.set_of_platforms, False)

        for p in colliding_platforms:
            if self.movement_x > 0:
                self.rect.right = p.rect.left
            if self.movement_x < 0:
                self.rect.left = p.rect.right

        #kolizja z enemy-------------
        colliding_enemy= pygame.sprite.spritecollide(self, self.level.set_of_enemies, False)

        for p in colliding_enemy:
            if self.movement_x > 0:
                self.lifes -= 1
                loss_life.play()
                self.rect.x = -100
                self.rect.y = 50
                if self.lifes==0:
                    game_over()
            if self.movement_x == 0:
                self.lifes -= 1
                loss_life.play()
                self.rect.x = -100
                self.rect.y = 50
                if self.lifes==0:
                    game_over()

        # -------ruch w pionie--------
        self.rect.y += self.movement_y

        # kolizje z platformami
        colliding_platforms = pygame.sprite.spritecollide(self, self.level.set_of_platforms, False)

        for p in colliding_platforms:
            if self.movement_y > 0:
                self.rect.bottom = p.rect.top
                if self.rotate_left and self.movement_x == 0:
                    self.image = gm.PLAYER_STAND_L
                if not self.rotate_left and self.movement_x == 0:
                    self.image = gm.PLAYER_STAND_R
            if self.movement_y < 0:
                self.rect.top = p.rect.bottom
            self.movement_y = 0

        #wypadanie z planszy--------------------------
        if self.rect.y > gm.HEIGHT:
            if self.rotate_left:
                self.lifes =0
                game_over()
            else:
                self.lifes=0
                game_over()

        # zmiana grafik gdy spadamy i skaczemy
        if self.movement_y > 0:
            if self.rotate_left:
                self.image = gm.PLAYER_FALL_L
            else:
                self.image = gm.PLAYER_FALL_R
        if self.movement_y < 0:
            if self.rotate_left:
                self.image = gm.PLAYER_JUMP_L
            else:
                self.image = gm.PLAYER_JUMP_R

        # wykrywamy kolizje z przedmiotami
        colliding_items = pygame.sprite.spritecollide(self, self.level.set_of_items, False)

        for item in colliding_items:
            if item.name == "life":
                self.lifes += 1
                item.kill()

            if item.name == "shotgun":
                self.items[item.name] = 1
                item.kill()

            if item.name == "star":
                item.kill()
                win()

            if item.name =="spikes":
                self.movement_y -=5
                self.rect.x-=350
                self.lifes -= 1
                loss_life.play()
                if self.lifes==0:
                    game_over()

    def _gravitation(self):
        if self.movement_y == 0:
            self.movement_y = 2
        else:
            self.movement_y += 0.35

    def get_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.press_left = True
                self.turn_left()
            if event.key == pygame.K_RIGHT:
                self.press_right = True
                self.turn_right()
            if event.key == pygame.K_UP:
                self.jump()
            if event.key == pygame.K_SPACE:
                self.shoot()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                if self.press_right:
                    self.turn_right()
                else:
                    self.stop()
                    self.image = gm.PLAYER_STAND_L
                self.press_left = False

            if event.key == pygame.K_RIGHT:
                if self.press_left:
                    self.turn_left()
                else:
                    self.stop()
                    self.image = gm.PLAYER_STAND_R
                self.press_right = False

    def _move(self, image_list):
        if self._count < 3:
            self.image = image_list[0]
        elif self._count < 6:
            self.image = image_list[1]
        elif self._count < 9:
            self.image = image_list[2]
        elif self._count < 12:
            self.image = image_list[3]
        elif self._count < 15:
            self.image = image_list[4]
        elif self._count < 18:
            self.image = image_list[5]
        elif self._count < 21:
            self.image = image_list[6]

        if self._count < 21:
            self._count += 1
        else:
            self._count = 0


class Platform(pygame.sprite.Sprite):
    def __init__(self, image_list, width, height, pos_x, pos_y):
        super().__init__()
        self.image_list = image_list
        self.width = width
        self.height = height
        self.image = pygame.Surface([self.width, self.height])
        self.rect = self.image.get_rect()
        self.rect.x = pos_x
        self.rect.y = pos_y

    def draw(self, surface):
        if self.width == 70:
            surface.blit(self.image_list[0], self.rect)
        else:
            surface.blit(self.image_list[1], self.rect)
            for i in range(70, self.width - 70, 70):
                surface.blit(self.image_list[2], [self.rect.x + i, self.rect.y])
            surface.blit(self.image_list[3], [self.rect.x + self.width - 70, self.rect.y])

# klasa przedmiotu
class Item(pygame.sprite.Sprite):
    def __init__(self, image, name, pos_center_x, pos_center_y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.name = name
        self.rect.center = [pos_center_x, pos_center_y]

class Bullet(pygame.sprite.Sprite):
    def __init__(self, image_list, rotate_left, pos_center_x, pos_center_y):
        super().__init__()
        self.image = image_list[0] if rotate_left else image_list[1]
        self.rect = self.image.get_rect()
        self.movement_x = -15 if rotate_left else 15
        self.rect.center = [pos_center_x, pos_center_y]

    def update(self):
        self.rect.x += self.movement_x

#ogolna klasa wroga
class Enemy(pygame.sprite.Sprite):
    def __init__(self, start_image, image_list_left, image_list_right, image_list_dead_left,
                 image_list_dead_right, movement_x = 0, movement_y = 0):
        super().__init__()
        self.image = start_image
        self.rect = self.image.get_rect()
        self.image_list_left = image_list_left
        self.image_list_right = image_list_right
        self.image_list_dead_left = image_list_dead_left
        self.image_list_dead_right = image_list_dead_right
        self.movement_x = movement_x
        self.movement_y = movement_y
        self.lifes = 1
        self.rotate_left = True
        self.count = 0
        self.score=0
        self.count_enemy=0


    def _move(self, image_list):
        if self.count < 4:
            self.image = image_list[0]
        elif self.count < 8:
            self.image = image_list[1]

        if self.count < 8:
            self.count += 1
        else:
            self.count = 0


    def update(self):
        if not self.lifes and self.count > 7:
            self.kill()

        self.rect.x += self.movement_x

        if self.movement_x > 0 and self.rotate_left:
            self.rotate_left = False
        if self.movement_x < 0 and not self.rotate_left:
            self.rotate_left = True

        #animacja
        if self.lifes:
            if self.movement_x > 0:
                self._move(self.image_list_right)
            if self.movement_x < 0:
                self._move(self.image_list_left)
        else:
            self.movement_x = 0
            self.movement_y = 0
            if self.rotate_left:
                self._move(self.image_list_dead_left)
            if not self.rotate_left:
                self._move(self.image_list_dead_right)


class PlatformEnemy(Enemy):
    def __init__(self, start_image, image_list_left, image_list_right, image_list_dead_left,
                 image_list_dead_right, platform, movement_x = 0, movement_y = 0):

        super().__init__(start_image, image_list_left, image_list_right, image_list_dead_left,
                 image_list_dead_right, movement_x, movement_y)

        self.platform = platform
        self.lifes = 3
        self.rect.bottom = self.platform.rect.top
        self.rect.centerx = random.randint(self.platform.rect.left + self.rect.width//2,
                                           self.platform.rect.right - self.rect.width//2)


    def update(self):
        super().update()
        if (self.rect.left < self.platform.rect.left or self.rect.right > self.platform.rect.right):
            self.movement_x *= -1

class BatEnemy(Enemy):
    def __init__(self, start_image, image_list_left, image_list_right, image_list_dead_left,
                 image_list_dead_right, level, movement_x = 0, movement_y = 0, boundary_right = 0,
                 boundary_left = 0, boundary_top = 0, boundary_bottom = 0):

        super().__init__(start_image, image_list_left, image_list_right, image_list_dead_left,
                 image_list_dead_right, movement_x, movement_y)
        self.lifes = 2
        self.level=level
        self.boundary_right = boundary_right
        self.boundary_left = boundary_left
        self.boundary_top = boundary_top
        self.boundary_bottom = boundary_bottom
        self.sleep = True

    def update(self):
        if self.sleep:
            if self.rect.left - self.level.player.rect.right < 300:
                self.sleep = False
        else:
            super().update()
            self.rect.y += self.movement_y
            pos_x = self.rect.left - self.level.world_shift
            if (pos_x < self.boundary_left or pos_x + self.rect.width > self.boundary_right):
                self.movement_x *= -1
            if (self.rect.top < self.boundary_top or self.rect.bottom > self.boundary_bottom):
                self.movement_y *= -1



# ogólna klasa planszy
class Level:
    def __init__(self, player):
        self.player = player
        self.set_of_platforms = set()
        self.set_of_items = pygame.sprite.Group()
        self.set_of_bullet= pygame.sprite.Group()
        self.set_of_enemies = pygame.sprite.Group()
        self.world_shift = 0
        self.score=0


    def update(self):
        self._delete_bullets()
        self.set_of_bullet.update()
        self.set_of_enemies.update()


        if self.player.rect.right >= 500:
            diff = self.player.rect.right - 500
            self.player.rect.right = 500
            self._shift_world(-diff)

        if self.player.rect.left <= 100:
            diff = 100 - self.player.rect.left
            self.player.rect.left = 100
            self._shift_world(diff)


    def draw(self, surface):
        for p in self.set_of_platforms:
            p.draw(surface)

        self.set_of_items.draw(surface)
        self.set_of_enemies.draw(surface)
        self.set_of_bullet.draw(surface)

        # rysowanie żyć
        for i in range(self.player.lifes ):
           surface.blit(gm.HEART, [20 + 40 * i, 15])

        #rysowanie punktow------------------
        text_score = gm.text_format(f" Punktow: {self.score}", gm.font, 40, gm.darkgreen)
        screen.blit(text_score,(gm.WIDTH-200,20))


    def _shift_world(self, shift_x):
        self.world_shift += shift_x

        for p in self.set_of_platforms:
            p.rect.x += shift_x

        for item in self.set_of_items:
            item.rect.x += shift_x

        for b in self.set_of_bullet:
            b.rect.x += shift_x

        for e in self.set_of_enemies:
            e.rect.x += shift_x

    def _delete_bullets(self):
        """chcemy sprawdzic kolizje pociskow z platformami"""
        # nie usuwamy platform, usuwamy pociski
        pygame.sprite.groupcollide(self.set_of_bullet, self.set_of_platforms, True, False)

        for b in self.set_of_bullet:
            if b.rect.left > gm.WIDTH or b.rect.right < 0:
                b.kill()

            #--------------
            colliding_enemies= pygame.sprite.spritecollide(b,self.set_of_enemies, False)
            for enemy in colliding_enemies:
                b.kill()
                if enemy.lifes:
                    enemy.lifes -= 1
                    if enemy.lifes == 0:
                        enemy.count = 0
                        self.score += random.randint(15,20)



class Level_1(Level):
    def __init__(self, player = None):
        super().__init__(player)
        self._create_platforms()
        self._create_itmes()
        self._create_platform_enemies()
        self._create_bat_enemies()
        self.count_of_enemy =0
        self._create_metal_platforms()


    def _create_platforms(self):
        ws_static_platforms = [[3*70, 70, -100, 530],  # schodek 1
                               [3 * 70, 70, 200, 320],  # schodek 2
                               [8* 70, 70, -550, 145],  # schodek 3
                               [12*70, 70, 0, gm.HEIGHT - 70],  #startowa bronia
                               [120 * 70, 70, -1000, -70 ]  # startowa bronia
                               ]


        for ws in ws_static_platforms:
            p = Platform(gm.GRASS_LIST, *ws)
            self.set_of_platforms.add(p)



    def _create_itmes(self):
        #dodatkowe zycie
        life = Item(gm.HEART, 'life', -210, 110) #-210,110
        self.set_of_items.add(life)

        #bron
        shotgun = Item(gm.SHOTGUN, 'shotgun', 1050, 530)   #1150, 4300
        self.set_of_items.add(shotgun)

        #ukonczenie gry
        star = Item(gm.STAR, 'star', 3500, 320)
        self.set_of_items.add(star)

        spikes1=Item(gm.SPIKES, "spikes", 1150, 535)
        spikes2 = Item(gm.SPIKES, "spikes", 950, 535)
        spikes3= Item(gm.SPIKES, "spikes", 3400, 350)
        spikes4 = Item(gm.SPIKES, "spikes", 3600, 350)
        self.set_of_items.add(spikes1, spikes2, spikes3, spikes4)


    def _create_platform_enemies(self):
        ws_static_platforms = [[8*70, 70, 1400, 350] ,  #zombie 1
                               [6 * 70, 70, 2100, 200],  # zombie 2
                               [8 * 70, 70, 2100, 200],    # drugi zombie2
                               [5 * 70, 70, 2000, 550],  # zombie 3
                               [6 * 70, 70, 2700, 400],   #zombie 4
                               ]


        for ws in ws_static_platforms:
            p = Platform(gm.GRASS_LIST, *ws)
            self.set_of_platforms.add(p)

            pe = PlatformEnemy(gm.ZOMBIE_STAND_L, gm.ZOMBIE_WALK_LIST_L, gm.ZOMBIE_WALK_LIST_R,
                               gm.ZOMBIE_DEAD_LIST_L, gm.ZOMBIE_DEAD_LIST_R, p,
                               random.choice([-5, -4, -3, -2, 2, 3, 4, 5])) #randomowy ruch

            self.set_of_enemies.add(pe)

    def _create_bat_enemies(self):
        bat = BatEnemy(gm.BAT_HANG, gm.BAT_FLY_LIST_L, gm.BAT_FLY_LIST_R, gm.BAT_DEAD_LIST_L,
                       gm.BAT_DEAD_LIST_R, self, random.choice([-5,-4,-3,-2,2,3,4,5]),
                       random.choice([-4,-3,-2,2,3,4]),2400, 1200,0,300)

        bat.rect.left = 1600
        bat.rect.top = 0
        self.set_of_enemies.add(bat)


    def _create_metal_platforms(self):
        ws_metal_platforms= [ [6 * 70, 70, 850, 550],  # platforma z serduszkiem
                              [6 * 70, 70, 3300, 360],
                              ]

        for mp in ws_metal_platforms:
            me = Platform(gm.METAL_LIST, *mp)
            self.set_of_platforms.add(me)




# konkretyzacja obiektów
player = Player(gm.PLAYER_STAND_R)
player.rect.center = screen.get_rect().center
current_level = Level_1(player)
player.level = current_level # gracz ma dostep do planszy, do wykrywania kolizji





# Main Menu
def main_menu():

    menu=True
    selected="start"

    while menu:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_UP:
                    selected="start"
                elif event.key==pygame.K_DOWN:
                    selected="quit"
                if event.key==pygame.K_RETURN:
                    if selected=="start":
                        game()
                    if selected=="quit":
                        pygame.quit()
                        quit()

        # Main Menu UI
        screen.blit(gm.BACKGROUND, (0,-340))
        title=gm.text_format("Prosta Platformowka", gm.font, 90, gm.orange)
        if selected=="start":
            text_start= gm.text_format("START", gm.font, 75, gm.white)
        else:
            text_start = gm.text_format("START", gm.font, 75, gm.black)
        if selected=="quit":
            text_quit= gm.text_format("QUIT", gm.font, 75, gm.white)
        else:
            text_quit = gm.text_format("QUIT", gm.font, 75, gm.black)

        text_author = gm.text_format("Wykonal Michal Jasik@2021", gm.font, 90, gm.darkgreen)

        title_rect=title.get_rect()
        start_rect=text_start.get_rect()
        quit_rect=text_quit.get_rect()
        author_rect= text_author.get_rect()


        # Main Menu Text
        screen.blit(title, (gm.WIDTH/2 - (title_rect[2]/2), 80))
        screen.blit(text_start, (gm.WIDTH/2 - (start_rect[2]/2), 300))
        screen.blit(text_quit, (gm.WIDTH/2 - (quit_rect[2]/2), 360))
        screen.blit(text_author, (gm.WIDTH / 2 - (author_rect[2] / 2), 600))
        pygame.display.update()

def game():
    game = pygame.mixer.Sound("Menu.mp3")
    game.set_volume(0.1)
    game.play()
    window_open = True
    while window_open:
        screen.blit(gm.BACKGROUND, (0,-340))
        # pętla zdarzeń
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    window_open = False
            elif event.type == pygame.QUIT:
                window_open = False
            player.get_event(event)


        # rysowanie i aktualizacja obiektów
        current_level.update()
        player.update()
        current_level.draw(screen)
        player.draw(screen)


        # aktualizacja okna pygame
        pygame.display.flip()
        clock.tick(60)

def game_over():
    menu = True
    selected = "quit"

    while menu:

        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_UP:
                    selected="quit"
                if event.key==pygame.K_RETURN:
                    if selected=="quit":
                        quit()

        # Main Menu UI
        screen.blit(gm.BACKGROUND, (0, -340))
        if selected == "quit":
            text_quit = gm.text_format("QUIT", gm.font, 75, gm.white)

        text_author = gm.text_format("Wykonal Michal Jasik@2021", gm.font, 40, gm.darkgreen)
        end = gm.text_format("Sorry, you lose :(", gm.font, 160, gm.red)

        quit_rect = text_quit.get_rect()
        author_rect = text_author.get_rect()
        end_rect = end.get_rect()


        # teksty menu
        screen.blit(text_quit, (gm.WIDTH / 2 - (quit_rect[2] / 2), 360))
        screen.blit(end, (gm.WIDTH / 2 - (end_rect[2] / 2), 60))
        screen.blit(text_author, (gm.WIDTH / 2 - (author_rect[2] / 2), 600))
        pygame.display.update()

def win():
    menu = True
    selected = "quit"

    while menu:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_UP:
                    selected="quit"
                if event.key==pygame.K_RETURN:
                    if selected=="quit":
                        pygame.quit()
                        quit()

        # Main Menu UI
        screen.blit(gm.BACKGROUND, (0, -340))
        if selected == "quit":
            text_quit = gm.text_format("QUIT", gm.font, 75, gm.white)

        text_author = gm.text_format("Wykonal Michal Jasik@2021", gm.font, 40, gm.darkgreen)
        end = gm.text_format(f"GG, You win  :)", gm.font, 160, gm.blue)

        quit_rect = text_quit.get_rect()
        author_rect = text_author.get_rect()
        end_rect = end.get_rect()


        # teksty menu
        screen.blit(end, (gm.WIDTH / 2 - (end_rect[2] / 2), 60))
        screen.blit(text_quit, (gm.WIDTH / 2 - (quit_rect[2] / 2), 360))
        screen.blit(text_author, (gm.WIDTH / 2 - (author_rect[2] / 2), 600))
        pygame.display.update()



main_menu()


