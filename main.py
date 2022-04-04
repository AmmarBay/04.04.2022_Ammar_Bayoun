import math
import os
import random
import time
from asyncio.windows_events import NULL
import pygame



#Constants
WIDTH = 1000
HEIGHT = 550
GAME_FPS = 60
pygame.font.init()
FONT = pygame.font.Font(os.path.join("fonts", "VCR_OSD_MONO_1.001.ttf"), 24)

PLAYER_ROT_SPEED = 2.5
PLAYER_MAX_SPEED = 50
PLAYER_DRAG_COEFF = 0.3 / GAME_FPS
PLAYER_FORCE = 4.2 / GAME_FPS + PLAYER_DRAG_COEFF
BULLET_SPEED = 3

bullets = []
asteroids = []

global score
global lives



BG = pygame.transform.scale(pygame.image.load(os.path.join("images", "galaxy.jpg")), (WIDTH, HEIGHT))
Ship = pygame.image.load(os.path.join("images", "Ship.png"))
Bullet1 = pygame.image.load(os.path.join("images", "Bullet.png"))


Asteroid_LG = pygame.image.load(os.path.join("images", "Stone3.png")) 
Asteroid_MD = pygame.image.load(os.path.join("images", "Stone2.png"))
Asteroid_SM = pygame.image.load(os.path.join("images", "Stone1.png"))

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroids")

def blitRotateCenter(surf, image, topleft, angle):

    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, rot=90):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.rot = rot
        self.speed = pygame.Vector2()
        self.defImg = Ship
        self.mask = pygame.mask.from_surface(Ship)
        self.rect = self.defImg.get_rect()
            
    def draw(self, window):
        self.curImg = self.defImg
        
        blitRotateCenter(WINDOW, self.curImg, (self.x, self.y), self.rot)
    
    def respawn(self):
        self.x = WIDTH/2 - 0.5*self.curImg.get_width()
        self.y = HEIGHT/2 - 0.5*self.curImg.get_height()
        self.speed = pygame.Vector2()
        self.rot = 0


class Asteroid(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.size = size
        asteroids_group.add(self)
        #LARGE 
        if(size == "large"):
            self.img = Asteroid_LG
            self.xVel = random.randint(-1, 1)
            self.yVel = random.randint(-1, 1)            
        #MEDIUM
        elif(size== "medium"):
            self.img = Asteroid_MD
            self.xVel = random.randint(-2, 2)
            self.yVel = random.randint(-2, 2)
        #SMALL
        elif(size== "small"):
            self.img = Asteroid_SM
            self.xVel = random.randint(-3, 3)
            self.yVel = random.randint(-3, 3)
           
        self.rect = self.img.get_rect()
        self.mask = pygame.mask.from_surface(self.img)       
        
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
        
    def destroy(self):
        global score
        if(self.size == "large"):              
            score += 25      
            asteroids.append(Asteroid(self.x + random.randint(0,15), self.y + random.randint(0, 15), "medium"))
            asteroids.append(Asteroid(self.x - random.randint(0,15), self.y - random.randint(0, 15), "medium"))
        elif(self.size == "medium"):      
            score += 50     
            asteroids.append(Asteroid(self.x + random.randint(0,10), self.y + random.randint(0, 10), "small"))
            asteroids.append(Asteroid(self.x - random.randint(0,10), self.y - random.randint(0, 10), "small"))    
                 

        elif(self.size == "small"):
            score += 100
        asteroids_group.remove(self)                               
        asteroids.remove(self)
        
    def kill(self):
        asteroids_group.remove(self)
        asteroids.remove(self)

        

class Bullet:
    def __init__(self, x, y, rot):
        self.x = x
        self.y = y
        self.rot = rot
        self.img = Bullet1
        self.active = True
        
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

def main():
    run = True
    FPS = GAME_FPS
    player = Player(WIDTH/2, HEIGHT/2, 0)

    global score
    global lives
    global asteroids_group    
    score = 0
    lives = 3
    asteroids_group = pygame.sprite.Group()
       
    clock = pygame.time.Clock()         
        
    def update():        
        global lives
        #Update player position
        player.x += player.speed.x
        player.y += player.speed.y
        
        #PLAYER BOUNDS   
        if(player.x + 10 < 0):
            player.x = WIDTH
        if(player.x - 10 > WIDTH):
            player.x = -10
        if(player.y + 10 < 0):
            player.y = HEIGHT
        if(player.y - 10 > HEIGHT):
            player.y = -10
        
        #bullets and bullet collision
        for bullet in bullets:
            bullet.x += BULLET_SPEED*math.cos(bullet.rot * math.pi/180)
            bullet.y += -1*BULLET_SPEED*math.sin(bullet.rot * math.pi/180)
            for asteroid in asteroids:
                if(asteroid.x <= bullet.x and bullet.x <= asteroid.x + asteroid.img.get_width()):
                    if(asteroid.y <= bullet.y and bullet.y <= asteroid.y + asteroid.img.get_height()):
                        bullets.remove(bullet)
                        asteroid.destroy()
                        break
                        
        for bullet in bullets:
            if bullet.x + bullet.img.get_width() < 0 or bullet.x - bullet.img.get_width() > WIDTH:
                bullets.remove(bullet)
            if bullet.y + bullet.img.get_height() < 0 or bullet.y - bullet.img.get_height() > HEIGHT:
                bullets.remove(bullet)
            break

        #asteroids
        for asteroid in asteroids:
            asteroid.x += asteroid.xVel
            asteroid.y += asteroid.yVel
            
        #COLLISION
            if(player.x + player.curImg.get_width() > asteroid.x and player.x < asteroid.x + asteroid.img.get_width()):
                if(player.y + player.curImg.get_height() > asteroid.y and player.y < asteroid.y + asteroid.img.get_height()):
                    lives -= 1
                    asteroid.kill()
                    player.respawn()             
            

            if(asteroid.x + asteroid.img.get_width() < 0):
                asteroid.x = WIDTH
            if(asteroid.x - asteroid.img.get_width() > WIDTH):
                asteroid.x = -10
            if(asteroid.y + asteroid.img.get_height() < 0):
                asteroid.y = HEIGHT
            if(asteroid.y - asteroid.img.get_height() > HEIGHT):
                asteroid.y = -10   
       
       
       
        if len(asteroids) <5:
                x = random.randint(0, WIDTH - 30)
                y = random.randint(0, HEIGHT - 30)
                
                if(abs(x - player.x) > 80 and abs(y - player.y) > 80):
                    asteroids.append(Asteroid(x,y, "large"))
               
        
        
        if(abs(player.speed.x) > 1):
           player.speed.x += -1 * player.speed.x * abs(player.speed.x) * PLAYER_DRAG_COEFF
        elif((abs(player.speed.x) + -1 * player.speed.x * PLAYER_DRAG_COEFF) > 0.01):
            player.speed.x += -1 * player.speed.x * PLAYER_DRAG_COEFF*3
        else:
            player.speed.x = 0
        
        if(abs(player.speed.y) > 1):
            player.speed.y += -1 * player.speed.y * abs(player.speed.y) * PLAYER_DRAG_COEFF
        elif((abs(player.speed.y) + -1 * player.speed.y * PLAYER_DRAG_COEFF) > 0.01):
            player.speed.y += -1 * player.speed.y * PLAYER_DRAG_COEFF*3
        else:
            player.speed.y = 0
            
    
    def draw():
        WINDOW.blit(BG, (0,0))
        
        
        for bullet in bullets:
            bullet.draw(WINDOW)

        for asteroid in asteroids:
            asteroid.draw(WINDOW)             
        player.draw(WINDOW)
        

        livesText = FONT.render(f"Lives: {lives}", 1, (255,255,255))
        scoreText = FONT.render(f"Score: {score}", 1, (255,255,255))
        WINDOW.blit(scoreText, (15,15))
        WINDOW.blit(livesText, (WIDTH - livesText.get_width() - 15, 15))
        pygame.display.update()
                    
    
    while run:
        clock.tick(FPS)
        update()
        draw()
        

        if(lives == 0):
            run = False            
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:  
                    if event.key == pygame.K_ESCAPE:
                        run = False
                    if event.key == pygame.K_KP_ENTER or event.key==pygame.K_RETURN:
                        if len(bullets) <10:
                            bullets.append(Bullet(player.x + player.curImg.get_width()/2 -1, player.y, player.rot))

        
        #key Input
        keys = pygame.key.get_pressed() 
        if keys[pygame.K_LEFT]:
            player.rot += PLAYER_ROT_SPEED
        if keys[pygame.K_RIGHT]:
            player.rot -= PLAYER_ROT_SPEED    
        if keys[pygame.K_UP]:           
            if(player.speed.x + PLAYER_FORCE * math.cos(player.rot * math.pi/180) < PLAYER_MAX_SPEED):
                player.speed.x += PLAYER_FORCE * math.cos(player.rot * math.pi/180)
            else:
                player.speed.x = PLAYER_MAX_SPEED
                
            if(player.speed.y + PLAYER_FORCE * -1*math.sin(player.rot * math.pi/180) < PLAYER_MAX_SPEED):
                player.speed.y += PLAYER_FORCE * -1*math.sin(player.rot * math.pi/180)
            else:
                player.speed.y = PLAYER_MAX_SPEED  
                
    
main()
        
