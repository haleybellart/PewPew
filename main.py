import pygame
from pygame import mixer
import os
import random
import csv
import time 
from pygame import font
from pygame import freetype


pygame.init()
pygame.mixer.init()

##set window size
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('PewPew')

#set frame rate
clock = pygame.time.Clock()
FPS = 60

#define game variables 
GRAVITY = 0.75
SCROLL_THRESH = 250
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS 
TILE_TYPES = 45 #add more here for more types of tiles 
MAX_LEVELS = 5 #(As you create more, add more levels here. end screen counts as a level)
screen_scroll = 0
bg_scroll = 0
level = 1 #TEMP CHANGE FOR TESTING
start_game = False 
start_intro = False
credits = False 

##define player action variables
moving_left = False
moving_right = False
shoot = False 
grenade = False
grenade_thrown= False


jump_fx = pygame.mixer.Sound('data/audio/audio_jump.wav')
jump_fx.set_volume(0.8)
shot_fx = pygame.mixer.Sound('data/audio/audio_shot.wav')
shot_fx.set_volume(0.5)
grenade_fx = pygame.mixer.Sound('data/audio/audio_grenade.wav')
grenade_fx.set_volume(0.8)
pickup_fx = pygame.mixer.Sound('data/audio/audio_pickup.wav')
pickup_fx.set_volume(0.5)
victory_fx = pygame.mixer.Sound('data/audio/audio_victory.wav')
victory_fx.set_volume(0.5)
health0_fx = pygame.mixer.Sound('data/audio/audio_health0.wav')
health0_fx.set_volume(0.5)
throw_fx = pygame.mixer.Sound('data/audio/audio_throw.wav')
throw_fx.set_volume(0.5)
death_fx = pygame.mixer.Sound('data/audio/audio_death.wav')
death_fx.set_volume(0.5)
click_fx = pygame.mixer.Sound('data/audio/audio_click.wav')
click_fx.set_volume(0.5)




##load images
start_img = pygame.image.load('data/img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('data/img/exit_btn.png').convert_alpha()
credits_img = pygame.image.load('data/img/credits_btn.png').convert_alpha()
restart_img = pygame.image.load('data/img/restart_btn.png').convert_alpha()
winner_img = pygame.image.load('data/img/tile/21.png').convert_alpha()
x_img = pygame.image.load('data/img/x_btn.png').convert_alpha()
credits_text_img = pygame.image.load('data/img/credits.png').convert_alpha()
sleepy_img = pygame.image.load('data/img/sleepy_minty.png').convert_alpha()
icon_img = pygame.image.load('data/img/icon.png').convert_alpha()
title_img = pygame.image.load('data/img/PEWPEW3.png')



#background
bg_grass = pygame.image.load('data/img/background/bg_grass.png').convert_alpha()
bg_mount = pygame.image.load('data/img/background/bg_mount.png').convert_alpha()
bg_clouds = pygame.image.load('data/img/background/bg_clouds.png').convert_alpha()
bg_sky = pygame.image.load('data/img/background/bg_sky.png').convert_alpha()


#tiles
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'data/img/tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

#bullet
bullet_img = pygame.image.load('data/img/icons/bullet.png').convert_alpha()
#grenade
grenade_img = pygame.image.load('data/img/icons/grenade.png').convert_alpha()
#pickups 
health_box_img = pygame.image.load('data/img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('data/img/icons/ammo_box.png').convert_alpha() #leftover from limited ammo mechanic 
grenade_box_img = pygame.image.load('data/img/icons/grenade_box.png').convert_alpha()
item_boxes = {
    'Health' : health_box_img,
    'Ammo' : ammo_box_img,
    'Grenade': grenade_box_img
}


#define colors
WHITE = (255, 255, 255)
GREEN = (50,205,50)
BLACK = (0, 0, 0)
BLUE = (135, 189, 248)
HEALTH_GREEN = (88, 179, 150)
HEALTH_BG = (11, 54, 76)


#font
pygame.font.get_fonts()
font = pygame.font.Font('data/font/Retro Gaming.ttf', 20)
font2 = pygame.font.Font('data/font/Retro Gaming.ttf', 25)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_bg():
    screen.fill(GREEN)
    width = bg_sky.get_width()
    for x in range(5):
        screen.blit(bg_sky, ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(bg_clouds, ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - bg_clouds.get_height() - 250))
        screen.blit(bg_mount, ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - bg_mount.get_height() - 150))
        screen.blit(bg_grass, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - bg_grass.get_height()))

#function to reset level
def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()
    spike_group.empty()
    tutorial_group.empty()
    player.victory = False
    player.health = player.max_health
    start_intro = False
    intro_fade.fade_counter = 0
    

    #create empty tile list
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)

    return data

    #create empty tile list 

#         self.font_name = '8-BIT WONDER.TTF'
#         self.font_name = '8-BIT WONDER.TTF'


class Button():
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False

        #get mouse position
        pos = pygame.mouse.get_pos()

        #check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
                click_fx.play()
                

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        #draw button
        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action

#create buttons
start_button = Button(SCREEN_WIDTH // 2 -95, SCREEN_HEIGHT // 2 - 70, start_img, 1)
credits_button = Button(SCREEN_WIDTH // 2 -95, SCREEN_HEIGHT // 2 +40, credits_img, 1)
exit_button = Button(SCREEN_WIDTH // 2 -95, SCREEN_HEIGHT // 2 + 150, exit_img, 1)
restart_button = Button(SCREEN_WIDTH // 2 -125, SCREEN_HEIGHT // 2 -50, restart_img, 1)
x_button = Button(720, 20, x_img, 1)

class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed 
        self.ammo = ammo #leftover from limited ammo 
        self.start_ammo = ammo #leftover from limited ammo 
        self.shoot_cooldown=0
        self.grenades = grenades 
        self.health = 100 
        self.max_health = self.health 
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.jump_amount = 2
        self.jump_cooldown =0
        self.crouch = False
        self.in_air = True 
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        
        #create ai specific variables 
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 200, 20) #variable 3 is sight distance 
        self.idling = False
        self.idling_counter = 0 
        self.victory = False 
        self.damage = False 
        self.damage_cooldown = 0

    


        #load all images for players
        animation_types = ['idle', 'run', 'jump', 'death', 'crouch', 'victory', 'damage']
        for animation in animation_types:
            #reset temporary list of images 
            temp_list = []
            #count num of files in folder 
            num_of_frames = len(os.listdir(f'data/img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'data/img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()


    def update(self):
        self.update_animation()
        self.check_alive()
        #update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1


    def move(self, moving_left, moving_right):
        ##reset movement varaibles 
        screen_scroll = 0
        dx=0
        dy=0

        ##assign movement variables if moving l/r
        if moving_left and self.crouch == False:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right and self.crouch == False:
            dx = self.speed
            self.flip = False
            self.direction = 1   

        ##jump
        if self.jump == True and self.jump_amount == 2: 
            self.vel_y = -11
            self.jump = False
            self.in_air = True
            self.jump_amount -= 1
            jump_fx.play()
        
        if self.jump_amount == 1 and self.jump == True:
            self.vel_y = -8
            self.jump=False
            self.in_air = True 
            self.jump_amount -=1
            jump_fx.play()
            

        if self.jump_amount == 0 and self.in_air == False: #reset jump counter on ground 
            self.jump_amount = 2

        if self.crouch == True and self.in_air == False: 
            self.vel_y = 0
            self.vel_x = 0
        
        if self.victory == True:
            self.vel_x = 0
            self.vel_y = 0
            
            
        

        #apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        #check for collision 

        #check collision in x axis 
        for tile in world.obstacle_list: 
            if tile[1].colliderect((self.rect.x + dx), self.rect.y, self.width, self.height):
                dx = 0
                #if ai has hit wall, turn around. 
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0
        #check collision in y axis 
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                #check if below the ground, i.e. jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                #check if above ground/falling 
                elif self.vel_y >= 0: 
                    self.vel_y = 0
                    self.in_air = False
                    dy = (tile[1].top - self.rect.bottom)
                    self.jump_amount = 2

        #check if going off edges 
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx=0

        #check for water colision
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0
            death_fx.play()

        #check for EXIT colision
        level_complete = False 
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

            

        #check if fallen off map 
        if self.rect.bottom > SCREEN_HEIGHT: 
            self.health = 0
            death_fx.play()

        ##update rect postiion 
        self.rect.x += dx
        self.rect.y += dy
        
        #update scroll based on player position
        if self.char_type == 'player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH -100 and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH)\
                or (self.rect.left < SCROLL_THRESH -100 and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx
                
        return screen_scroll, level_complete

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown=20
            if self.crouch == False: 
                bullet = Bullet(self.rect.centerx + (0.9 * self.rect.size[0] * self.direction), self.rect.centery+3, self.direction)
                bullet_group.add(bullet)
            if self.crouch == True: #change bullet spawn point if crouching 
                bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery +10, self.direction)
                bullet_group.add(bullet)
            #reduce ammo
            #self.ammo -=1
            shot_fx.play()

    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)#0: Idle 
                self.idling = True 
                self.idling_counter = 50
            #check if ai is near player
            if self.vision.colliderect(player.rect) and self.shoot_cooldown == 0:
                #stop running and face the player
                self.update_action(0)#0: idle
                #shoot
                self.shoot()
                self.shoot_cooldown = 30 #enemies shoot slower than player 
            else:
                if self.idling == False: 
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False 
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1) #1: run
                    self.move_counter += 1
                    #update ai vision as enemy moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
                    # pygame.draw.rect(screen, RED, self.vision) #visual for enemy sight

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *=-1
                    

                else: 
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False
                
        #scroll
        self.rect.x += screen_scroll


    def update_animation(self):
        #update animation 
        ANIMATION_COOLDOWN = 90
        #update image depending on current frame
        self.img = self.animation_list[self.action][self.frame_index]
        #check if enough time has passed since last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        #if animation has run out, reset
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else: 
                self.frame_index = 0



    def update_action(self, new_action):
        #check if new action is different from previous action 
        if new_action != self.action: 
            self.action = new_action
            #update animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()


    #death
    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

            


    def draw(self):
        screen.blit(pygame.transform.flip(self.img, self.flip, False), self.rect)

class World():
    def __init__(self):
        self.obstacle_list = []

    
    def process_data(self, data):
        #iterate through each value in level data file
        global player, health_bar, x, y #this and the two lines below fix the local variable error I was encountering 
        player = Soldier('player', x * TILE_SIZE, y * TILE_SIZE, 2, 5, 20, 5)
        health_bar = HealthBar(10, 10, player.health, player.health)

        self.level_length = len(data[0])
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 15: #0-15 are ground tiles 
                        self.obstacle_list.append(tile_data)
                    elif tile == 16: #only bottom water tile is here, this is the only one that kills the player, top water tile for decoration
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif tile >= 17 and tile <= 21:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 22:#create player
                        player = Soldier('player', x * TILE_SIZE, y * TILE_SIZE, 2, 5, 20, 5)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 23: #create enemies 
                        enemy = Soldier('enemy', x * TILE_SIZE, y * TILE_SIZE, 2, 2, 20, 0)
                        enemy_group.add(enemy)
                    elif tile == 24: #gernadebox
                        grenade_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(grenade_box)
                    elif tile == 25: #healthbox
                        health_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(health_box)
                    elif tile == 26 or tile == 27: #create exit
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)
                    elif tile == 28: #create spike
                        spike = Spike(img, x * TILE_SIZE, y * TILE_SIZE)
                        spike_group.add(spike)
                    elif tile == 29: #create downspike
                        spike = DownSpike(img, x * TILE_SIZE, y * TILE_SIZE)
                        spike_group.add(spike)
                    elif tile >= 30 and tile <= 42: #tutorial images
                        tutorial = Tutorial(img, x * TILE_SIZE, y * TILE_SIZE)
                        tutorial_group.add(tutorial)

                    else:
                        pass

        return player, health_bar
            

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])
            
class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Tutorial(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
    
    def update(self):
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE//2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        #scroll
        self.rect.x += screen_scroll
        #check collision for player
        if pygame.sprite.collide_rect(self, player):
            #check kind of box
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo': #leftover from limited ammo 
                player.ammo += 15
            elif self.item_type == 'Grenade':
                player.grenades += 3
            self.kill()
            pickup_fx.play()

class Spike(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
    
    
    def damage(self):
        if player.damage_cooldown > 0:
            player.update_action(6)
            player.damage_cooldown -= 1
        if player.damage_cooldown <=0: 
            pass

    def update(self):
        #scroll
        self.rect.x += screen_scroll
        #check collision for player
        if pygame.sprite.collide_rect(self, player):
            
            player.health -= 25

            if player.health > 0:
                health0_fx.play()
            player.vel_y = -7
            self.in_air = True

class DownSpike(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
    
    
    def damage(self):
        if player.damage_cooldown > 0:
            player.update_action(6)
            player.damage_cooldown -= 1
        if player.damage_cooldown <=0: 
            pass

    def update(self):
        #scroll
        self.rect.x += screen_scroll
        #check collision for player
        if pygame.sprite.collide_rect(self, player):
            
            player.health -= 25
            player.vel_y = 7
            if player.health > 0:
                health0_fx.play()

            
            


class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health
    
    def draw(self, health):
        #update health amount 
        self.health = health 
        #calc health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, WHITE, (self.x-2, self.y-2, 154, 24))
        pygame.draw.rect(screen, HEALTH_BG, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, HEALTH_GREEN, (self.x, self.y, 150 * ratio, 20))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        #move bullet
        self.rect.x += (self.direction * self.speed)
        #check if off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        #check for level collision
        for tile in world.obstacle_list: 
            if tile[1].colliderect(self.rect):
                self.kill()
        #check character collision 
        if pygame.sprite.spritecollide(player, bullet_group, False) and player.crouch == False:
            if player.alive:
                player.health -=10
                self.kill()
                health0_fx.play()
                player.vel_y = -4 #damage feedback 

                
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -=25
                    self.kill()


#grenade
class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100 
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction
        throw_fx.play()

    def update(self):
        self.vel_y += GRAVITY 
        dx = self.direction * self.speed
        dy = self.vel_y

        #check for level collision 
        for tile in world.obstacle_list:
            #check if off screen
            if tile[1].colliderect(self.rect.x +dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed

            #check collision in y direction 
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                #check if below ground/thrown up 
                if self.vel_y < 0: 
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                #check if above ground/falling 
                elif self.vel_y >= 0: 
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom 


        #update grenade position 
        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        #grenade timer 
        self.timer -= 1 
        if self.timer <= 0:
            self.kill()
            grenade_fx.play()
            explosion = Explosion(self.rect.x, self.rect.y, 1)
            explosion_group.add(explosion)
            #do damage to anyone in range 
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= 50
                player.damage == True 
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 100 
                    
   

#explosions 
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 9):
                img = pygame.image.load(f'data/img/explosion/explosion_{num}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0


    def update(self):
        #scroll
        self.rect.x += screen_scroll
        EXPLOSION_SPEED = 5
        #update explosion animation 
        self.counter += 1

        if self.counter >= EXPLOSION_SPEED: 
            self.counter = 0
            self.frame_index +=1
            #if animation is complete then delete explosion 
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]

class ScreenFade():
    def __init__(self, direction, color, speed):
        self.direction = direction
        self.color = color
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed

        if self.direction == 1: #whole/center screen fade 
            pygame.draw.rect(screen, self.color, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        if self.direction == 2: #vertical screen fade down, death fade
            pygame.draw.rect(screen, self.color, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))

        if self.fade_counter >= SCREEN_WIDTH:
            fade_complete = True
        
        return fade_complete

#create screen fades
intro_fade = ScreenFade(1, BLACK, 8)
death_fade = ScreenFade(2, BLACK, 8)

#create sprite groups 
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
spike_group = pygame.sprite.Group()
tutorial_group = pygame.sprite.Group()




world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
#load in level data and create world
with open(f'data/levels/level_{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)

#set game window icons
pygame.display.set_icon(icon_img)

run = True
while run: 

    clock.tick(FPS)
    

    if start_game == False:
        #draw menu
        screen.fill(BLUE)
        screen.blit(title_img, (70,60))

        #ad bttn
        if start_button.draw(screen):
            start_game = True
            start_intro = True
            pygame.mixer.music.load('data/audio/Track9.wav') #Alt Music
            pygame.mixer.music.set_volume(0.45)
            pygame.mixer.music.play(-1, 0.0, 2000)
        elif credits_button.draw(screen):
            credits = True 
        elif credits == True: #create credits screen
            screen.fill(BLUE)
            screen.blit(credits_text_img, (0,0))
            if x_button.draw(screen): #exit credits screen
                credits = False 
        elif exit_button.draw(screen):
            run = False

    else: 
        
        #update bg
        draw_bg()
        #draw map
        world.draw()
        #show health
        health_bar.draw(player.health)
        #show text
        # draw_text('AMMO: ', font, WHITE, 10, 35) ##leftover limited ammo mechanic 
        # for x in range(player.ammo): 
        #     screen.blit(bullet_img, (85 + (x*12), 45))

        #show grenades
        draw_text('GRENADES: ', font, WHITE, 6, 35)
        for x in range(player.grenades): 
            screen.blit(grenade_img, (145 + (x*20), 39))


        player.update()
        player.draw()

        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()

        #update and draw groups
        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        exit_group.update()
        spike_group.update()
        tutorial_group.update()

        bullet_group.draw(screen)
        grenade_group.draw(screen)
        decoration_group.draw(screen)
        item_box_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)
        spike_group.draw(screen)
        explosion_group.draw(screen)
        tutorial_group.draw(screen)

        #show intro
        if start_intro == True: 
            if intro_fade.fade(): 
                start_intro = False
                intro_fade.fade_counter = 0

        #update player actions
        if player.alive: 
            #shoot
            if shoot: 
                player.shoot()
            #throw gernades
            elif grenade and grenade_thrown == False and player.grenades > 0: 
                grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction), 
                            player.rect.top, player.direction)
                grenade_group.add(grenade)
                #reduce grenades
                player.grenades -= 1
                grenade_thrown = True  
            if player.in_air:
                player.update_action(2) #2: jump
            elif player.crouch:
                player.update_action(4) #4: crouch
            elif moving_left or moving_right: 
                player.update_action(1) #1: run
            elif player.victory == True:
                player.update_action(5) #5 Victory 
            elif player.damage_cooldown > 0:
                player.update_action(6)
            else:
                player.update_action(0) #0: idle  
            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll
            #check if player has completed level 
            if level_complete: 
                victory_fx.play()
                player.update_action(5) #5 Victory 
                pygame.time.delay(1500)
                level += 1 
                start_intro = True 
                bg_scroll = 0
                world_data = reset_level()
                if level <= MAX_LEVELS:

                    with open(f'data/levels/level_{level}_data.csv', newline='') as csvfile:
                            reader = csv.reader(csvfile, delimiter=',')
                            for x, row in enumerate(reader):
                                for y, tile in enumerate(row):
                                    world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)
                    screen.fill(BLUE)

                    

                    
                                    
        else:
            screen_scroll = 0

            if death_fade.fade():
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    world_data = reset_level()
                    #load in level data and create world
                    with open(f'data/levels/level_{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)
        #winner screen
        if level >= MAX_LEVELS:
            start_game == False
            start_intro == True 
            intro_fade.fade_counter = 0
            screen.fill(BLUE)
            draw_text('CONGRATULATIONS!', font2, WHITE, 255, 150)
            draw_text('You have won ALL the levels. Thanks for playing!', font2, WHITE, 24, 200)
            sleepy_img = pygame.transform.scale(sleepy_img, (160, 120))
            screen.blit(sleepy_img, (340, 280))
            
            # #guidelines to center the text on the end sreen
            # pygame.draw.line(screen, BLACK, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, 800))
            # pygame.draw.line(screen, BLACK, (0, SCREEN_HEIGHT // 2), (800, SCREEN_HEIGHT // 2))

            #add button
            if exit_button.draw(screen):
                run = False
            


        #keep window open
    for event in pygame.event.get():
        #quit game
        if event.type== pygame.QUIT:
            run = False 
        #keyboard presses
        if event.type == pygame.KEYDOWN and level != MAX_LEVELS:
            if event.key == pygame.K_LEFT:
                moving_left = True
            if event.key == pygame.K_RIGHT:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_LSHIFT:
                grenade=True 
            if event.key ==pygame.K_UP and player.alive and player.jump_amount > 0:
                player.jump = True 
            if event.key ==pygame.K_UP and player.jump_amount == 0:
                pass
            if event.key == pygame.K_ESCAPE:
                run=False
            if event.key == pygame.K_DOWN:
                player.crouch = True

    #key released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                moving_left = False
            if event.key == pygame.K_RIGHT:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_LSHIFT:
                grenade=False
                grenade_thrown = False
            if event.key == pygame.K_DOWN: 
                player.crouch = False
            
            

    pygame.display.update()


pygame.quit()


