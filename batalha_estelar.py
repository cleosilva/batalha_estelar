# Jogo de tiro no espaço
# Arte de kenney.nl
# Musica OpenGameArt.Org - Autor: Playonloop.com
import pygame
import random

width = 480
height = 600
fps = 60 # velocidade em que a tela será atualizada
powerup_time = 5000  # tempo do powerup em segundos

# Definição de cores
white = (255,255,255)
black = (0,0,0)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
yellow = (255,255,0)

# Inicializa o pygame e cria a tela
pygame.init()
pygame.mixer.init()  # controla os efeitos sonoros do game
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Shmup! Batalha Estelar.")
clock = pygame.time.Clock()  # Controla o número de frames por segundo

font_name = pygame.font.match_font('arial')
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, white)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def newmob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    bar_length = 100
    bar_height = 10
    fill = (pct / 100) * bar_length
    outline_rect = pygame.Rect(x, y, bar_length, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    pygame.draw.rect(surf, green, fill_rect)
    pygame.draw.rect(surf, white, outline_rect, 2)

def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)

class Player(pygame.sprite.Sprite):
    """Cria a nave do piloto."""
    def __init__(self):
        self.speedx = 0
        self.shield = 100
        pygame.sprite.Sprite.__init__(self)
        self.image = player_img
        self.rect = self.image.get_rect()
        self.radius = 20
        # pygame.draw.circle(self.image, red, self.rect.center, self.radius)
        self.rect.centerx = width / 2 
        self.rect.bottom = height - 10
        self.speedx = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_shoot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_time = pygame.time.get_ticks()
        self.power = 1
        self.power_time = pygame.time.get_ticks() 
    
    def update(self):
        # tempo para os powerups
        if self.power >= 2 and pygame.time.get_ticks() - self.power_time > powerup_time:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()
        # mostrando o jogador escondido
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            # posição correta da nave
            self.rect.centerx = width / 2
            self.rect.bottom = height - 10
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -8
        if keystate[pygame.K_RIGHT]:
            self.speedx = 8
        if keystate[pygame.K_SPACE]:
            self.shoot()
        self.rect.x += self.speedx
        # Limita a nave dentro da tela
        if self.rect.right > width:
            self.rect.right = width
        if self.rect.left < 0:
            self.rect.left = 0

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shoot > self.shoot_delay:
            self.last_shoot = now
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            if self.power >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()

    def hide(self):
        # ocultando o jogador temporariamente
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (width / 2, height + 200)

class Mob(pygame.sprite.Sprite):
    """Cria os inimigos."""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image = self.image_orig.copy()      
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        # pygame.draw.circle(self.image, red, self.rect.center, self.radius)
        self.rect.x = random.randrange(width - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.speedy = random.randrange(1, 8) 
        self.speedx = random.randrange(-3, 3)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks() 
    
    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center 

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > height + 10 or self.rect.left < -25 or self.rect.right > width + 20:
            self.rect.x = random.randrange(width - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10  
    
    def update(self):
        self.rect.y += self.speedy
        # Remove a bala quando chega no topo da tela
        if self.rect.bottom < 0:
            self.kill()

class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = powerup_images[self.type]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 5  # velocidade do powerup  
    
    def update(self):
        self.rect.y += self.speedy
        # Remove a bala quando chega no topo da tela
        if self.rect.top > height:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 75
    
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center    

def show_go_screen():
    screen.blit(background, background_rect)
    draw_text(screen, 'SHMUP!', 64, width / 2, height / 4)
    draw_text(screen, 'Use as setas para movimentar e espaço para atirar', 
                       22, width / 2, height / 2)
    draw_text(screen, 'Pressione uma tecla para começar', 18, width / 2, height * 3 / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False        

# Carregando imagens gráficas do jogo
background = pygame.image.load('img/starfield.png')
background_rect = background.get_rect()
player_img = pygame.image.load('img/ship_green_small.png')
player_mini_img = pygame.transform.scale(player_img, (25, 19))
meteor_img = pygame.image.load('img/meteor_2.png')
bullet_img = pygame.image.load('img/laserRed_medio.png')
meteor_images = []
meteor_list = ['img/meteorBrown_big1.png', 'img/meteorBrown_big2.png', 'img/meteorBrown_med1.png',
               'img/meteorBrown_med1.png', 'img/meteorBrown_small1.png', 'img/meteorBrown_small2.png',
               'img/meteorBrown_tiny1.png'] 
for img in meteor_list:
    meteor_images.append(pygame.image.load(img))
explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
    filename = 'img/regularExplosion0{}.png'.format(i)
    img = pygame.image.load(filename)
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)
    filename = 'img/sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(filename)
    explosion_anim['player'].append(img)
powerup_images = {}
powerup_images['shield'] = pygame.image.load('img/shield_gold.png')
powerup_images['gun'] = pygame.image.load('img/bolt_gold.png')

# Carregando efeitos sonoros do jogo
shoot_sound = pygame.mixer.Sound('snd/pew.wav')
shield_sound = pygame.mixer.Sound('snd/pow4.wav')
power_sound = pygame.mixer.Sound('snd/pow5.wav')
expl_sounds = []
for snd in ['snd/expl3.wav', 'snd/expl6.wav']:
    expl_sounds.append(pygame.mixer.Sound(snd))
player_die_sound = pygame.mixer.Sound('snd/rumble1.ogg')    
pygame.mixer.music.load('snd/POL-battle-march-short.wav')
pygame.mixer.music.set_volume(0.4)

pygame.mixer.music.play(loops=-1)   # Repete a musica quando chegar ao final

# Loop do jogo
game_over = True
running = True 
while running:
    if game_over:
        show_go_screen()
        game_over = False
        all_sprites = pygame.sprite.Group()   
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        for i in range(8):
            newmob()
        score = 0

    # Mantém o loop  rodando na velocidade certa
    clock.tick(fps)
    # Process Input (Eventos)
    for event in pygame.event.get():
        # Ocorre o fechamento da janela
        if event.type == pygame.QUIT:
            running = False
        
    # Update
    all_sprites.update()

    # Verificando se a bala atingi o inimigo
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        score += 50 - hit.radius
        random.choice(expl_sounds).play()
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        if random.random() > 0.9:
            pow = Pow(hit.rect.center)
            all_sprites.add(pow)
            powerups.add(pow)
        newmob()
       
    # Verificando se o inimigo colidiu com o jogador
    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= hit.radius * 2
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        newmob()
        if player.shield <= 0:
            player_die_sound.play()
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.shield = 100
    
    # Verificando se o jogador colidiu com o powerup
    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        if hit.type == 'shield':
            player.shield += random.randrange(10, 30)
            shield_sound.play()
            if player.shield >= 100:
                player.shield = 100
        if hit.type == 'gun':
            player.powerup()
            power_sound.play()

    
    # Se o jogador morrer e a explosão tiver terminado
    if player.lives == 0 and not death_explosion.alive():
        game_over = True        

    # Draw / render
    screen.fill(black)
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, width / 2, 10)
    draw_shield_bar(screen, 5, 5, player.shield)
    draw_lives(screen, width - 100, 5, player.lives, player_mini_img)
   
    # Depois de desenhar tudo, vire (flip) a tela
    pygame.display.flip() # Atualiza a tela  // double buffering

pygame.quit()
