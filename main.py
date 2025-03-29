import pgzrun
import random
#import os
from pygame import Rect

#configurações iniciais de janela e de jogo
WIDTH = 1200
HEIGHT = 800
#os.environ['SDL_VIDEO_CENTERED'] = '1' #inicia a janela no meio da tela, usado durante desenvolvimento, pois não é permitido uso de outras bibliotecas de acordo com o teste
TITLE = "Jogo de Plataforma"
GRAVITY = 0.5 #gravidade, quanto maior o número maior a força que te puxa para baixo
JUMP_STRENGTH = -15 #força do pulo, é negativa para 'subir'
MOVE_SPEED = 5  #velocidade do herói
MOVE_TIME = PAUSE_TIME = 2  #variaveis em segundos para movimentação do inimigo

class Button:
    def __init__(self, x, y, text, action):
        self.rect = Rect(x, y, 200, 50)
        self.text = text
        self.action = action
        self.color = (100, 100, 100)

    def draw(self):
        screen.draw.filled_rect(self.rect, self.color)
        screen.draw.text(self.text, center=self.rect.center, fontsize=30, color="white")

    def on_click(self, pos):
        if self.rect.collidepoint(pos):
            if sound_enabled:
                sounds.click.play()
            self.action()

def set_game_state(active):
    global is_running
    is_running = active
    if active and sound_enabled:
        music.play("background")

def toggle_sound():
    global sound_enabled
    sound_enabled = not sound_enabled
    if sound_enabled:
        music.unpause()
        buttons[1].text = "Som: LIGADO"
    else:
        music.pause()
        buttons[1].text = "Som: DESLIGADO"

def quit_game():
    import sys
    sys.exit()

#menu
buttons = [
    Button(WIDTH//2 - 100, HEIGHT//2, "Iniciar jogo", lambda: set_game_state(True)),
    Button(WIDTH//2 - 100, HEIGHT//2 + 70, "Som: LIGADO", toggle_sound),
    Button(WIDTH//2 - 100, HEIGHT//2 + 140, "Sair", quit_game)
]
victory_buttons = [
    Button(WIDTH//2 - 100, HEIGHT//2, "Reiniciar", lambda: reset_game(True)),
    Button(WIDTH//2 - 100, HEIGHT//2 + 70, "Sair", quit_game)
]

game_over_buttons = [
    Button(WIDTH//2 - 100, HEIGHT//2, "Tentar de novo", lambda: reset_game(True)),
    Button(WIDTH//2 - 100, HEIGHT//2 + 70, "Sair", quit_game)
]


#carregar sprites
hero = Actor("player_idle", (100, 500))
hero.vy = 0
hero.vx = 0
hero_animation_counter = 0

platforms = [
    Rect(0, 780, 700, 20),
    Rect(500, 550, 500, 20),
    Rect(900, 280, 300, 20)
]

enemies = [
    Actor("slime_idle", (370, 763)),
    Actor("slime_idle", (770, 533)),
    Actor("slime_idle", (1100, 263))
]

animation_counter = 0
enemy_animation_counter = 0
enemy_move_probability = 0.1  #chance do inimigo se mover a cada frame (0 a 1)

is_running = False
sound_enabled = True
victory_screen = False
game_over = False


def draw():
    screen.clear()
    if game_over:  #verifica se o jogo terminou
        if victory_screen:
            screen.fill((0, 200, 0))  #vitória
            screen.draw.text("Você venceu :)", center=(WIDTH//2, HEIGHT//2 - 150), fontsize=60, color="white")
            for button in victory_buttons:
                button.draw()
        else:
            screen.fill((20, 0, 0))  #derrota
            screen.draw.text("GAME OVER :(", center=(WIDTH//2, HEIGHT//2 - 150), fontsize=60, color="red") 
            for button in game_over_buttons:
                    button.draw()
    elif is_running:
        screen.fill("lightblue")
        hero.draw()
        for p in platforms:
            screen.draw.filled_rect(p, "red")
        for e in enemies:
            e.draw()
        #mostra som no jogo
        sound_status = "LIGADO" if sound_enabled else "DESLIGADO"
        screen.draw.text(f"Som: {sound_status}", (10, 10), fontsize=30, color="white")

        #instruções
        screen.draw.text("Movimentação pelas setas [<-] [->] e pulo na [BARRA DE ESPAÇO]", 
                        (10, 50), fontsize=26, color="white")
        screen.draw.text("Derrote os inimigos pisando na cabeça deles!", 
                        (10, 80), fontsize=26, color="white")

    
    else:
        #menu inicial
        screen.fill((30, 30, 30))
        screen.draw.text("Jogo de Plataforma", center=(WIDTH//2, HEIGHT//2 - 150), fontsize=60, color="white")
        
        for button in buttons:
            button.draw()

def trigger_game_end(victory=False):
    global game_over, is_running, victory_screen
    game_over = True
    victory_screen = victory
    is_running = False
    music.fadeout(0.3) #musica vai parando em segundos
    if victory and sound_enabled:
        sounds.victory.play() #som se ganhou
    elif sound_enabled:
        sounds.game_over.play()  

def reset_game(full_reset=False):
    global is_running, game_over, victory_screen
    hero.pos = (100, 500)
    hero.vy = 0
    game_over = False
    victory_screen = False
    if full_reset: #se for do game over, reinicia o jogo
        is_running = True

def move_hero():
    global hero_animation_counter
    hero.x += hero.vx

    hero_animation_counter = (hero_animation_counter + 1) % 10
    if hero_animation_counter == 0 and hero.vx != 0:
        #alterna sprite de movimento
        if hero.vx > 0:
            hero.image = "player_move1_right" if hero.image == "player_move2_right" else "player_move2_right"
        elif hero.vx < 0:
            hero.image = "player_move1_left" if hero.image == "player_move2_left" else "player_move2_left"

    #check de pulo
    if hero.vy != 0:
        if hero.vx > 0:
            hero.image = "player_jump_right"
        elif hero.vx < 0:
            hero.image = "player_jump_left"
    elif hero.vx == 0 and hero.vy == 0:
        hero.image = "player_idle"

def update(dt):
    global is_running, animation_counter, hero_animation_counter
    if is_running:
        apply_gravity()
        move_hero()
        move_enemies(dt)
        check_collisions()

        if hero.y > HEIGHT:  #se cair da plataforma/fase perde
            trigger_game_end()

def apply_gravity():
    hero.vy += GRAVITY
    hero.y += hero.vy
    for p in platforms:
        if hero.colliderect(p) and hero.vy > 0:
            hero.y = p.y - hero.height // 2
            hero.vy = 0

def move_enemies(dt):
    global enemy_animation_counter
    for e in enemies:
        if not hasattr(e, "last_move_time"):
            e.last_move_time = 0  #inicia clock inimigo
            e.moving = True
            e.time_since_last_move = 0

        #atualiza o tempo desde a última mudança
        e.time_since_last_move += dt

        if e.moving and e.time_since_last_move < MOVE_TIME:
            e.x += random.choice([-1, 1]) * 3  #movimentação aleatório
            e.image = "slime_walk"
        elif not e.moving and e.time_since_last_move < PAUSE_TIME:
            e.image = "slime_idle"
        else:
            e.time_since_last_move = 0  #reinicia o tempo
            e.moving = not e.moving  #alterna estados

        enemy_animation_counter = (enemy_animation_counter + 1) % 45
        if enemy_animation_counter == 0:
            e.image = "slime_walk" if e.image == "slime_idle" else "slime_idle"

def check_collisions():
    global enemies
    for e in enemies:
        if hero.colliderect(e):
            if hero.vy > 0:  #se o jogador estiver caindo (pulando na cabeça do inimigo)
                enemies.remove(e)  #remove inimigo ao cair nele
                hero.vy = JUMP_STRENGTH / 2  #apenas para dar sensação de impacto/inércia, alguns jogos deixam a força total do pulo para efetuar um pulo duplo
                if sound_enabled:
                    sounds.enemy_defeated.play()
            else:
                trigger_game_end()  #se tocar no inimigo sem ser pulando, morre
    
    if len(enemies) == 0:
        trigger_game_end(True)

def reset_game(full_reset=False):
    global is_running, game_over,victory_screen, enemies
    hero.pos = (100, 500)
    hero.vy = 0

    #reinicia inimigos
    enemies = [
        Actor("slime_idle", (370, 763)),
        Actor("slime_idle", (770, 533)),
        Actor("slime_idle", (1100, 263))
    ]

    game_over = False
    victory_screen = False
    if full_reset:
        is_running = True
        if sound_enabled:
            music.play("background")

def on_key_down(key):
    if key == keys.SPACE and hero.vy == 0:
        hero.vy = JUMP_STRENGTH
        if sound_enabled:
            sounds.jump.play()
    elif key == keys.RIGHT:
        hero.vx = MOVE_SPEED
    elif key == keys.LEFT:
        hero.vx = -MOVE_SPEED

def on_key_up(key):
    if key == keys.RIGHT or key == keys.LEFT:
        hero.vx = 0  #parar o movimento quando a tecla é solta

def on_mouse_down(pos):
    if victory_screen:
            for button in victory_buttons:
                button.on_click(pos)
    elif game_over:
            for button in game_over_buttons:
                button.on_click(pos)
    elif not is_running:
        for button in buttons:
            button.on_click(pos)

pgzrun.go()