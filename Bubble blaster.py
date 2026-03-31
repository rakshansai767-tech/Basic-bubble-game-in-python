from tkinter import *
from random import randint, uniform
from time import time
from math import sqrt, sin
import os
import threading
import pygame 


BASE_PATH = os.path.dirname(__file__)
SOUND_DIR = os.path.join(BASE_PATH, "Sound files")
BG_MUSIC = os.path.join(SOUND_DIR, "Background.mp3")
BOMB_SOUND = os.path.join(SOUND_DIR, "Bomb.mp3")
POP_SOUND = os.path.join(SOUND_DIR, "bubble pop.mp3")

try:
    pygame.mixer.init()
except:
    print("Audio hardware busy")

WIDTH, HEIGHT = 800, 500
SHIP_SPD = 12
running, paused = True, False
score, level, lives = 0, 1, 3
end_time = 0
bub_id, bub_r, bub_speed, bub_type = [], [], [], []
keys_pressed = set()


shield_active = False
shield_ui = None
boss_id = None
boss_hp = 0
boss_max_hp = 0


def play_sound(file_path, vol=0.5):
    if os.path.exists(file_path) and running:
        try:
            s = pygame.mixer.Sound(file_path); s.set_volume(vol); s.play()
        except: pass

def music_loop_thread():
    if os.path.exists(BG_MUSIC) and running:
        try:
            pygame.mixer.music.load(BG_MUSIC); pygame.mixer.music.set_volume(0.2); pygame.mixer.music.play(-1)
        except: pass

def on_closing():
    global running; running = False; pygame.mixer.music.stop(); window.destroy(); os._exit(0)


window = Tk()
window.title('Bubble Blaster: 30 Level 3-BOSS Edition')
window.protocol("WM_DELETE_WINDOW", on_closing)
c = Canvas(window, width=WIDTH, height=HEIGHT, bg='darkblue')
c.pack()

def setup_ui():
    global score_text, time_text, level_text, lives_text, ship_id, ship_id2
    c.create_text(50, 30, text='TIME', fill='white', font=('Helvetica', 12, 'bold'))
    c.create_text(150, 30, text='SCORE', fill='white', font=('Helvetica', 12, 'bold'))
    c.create_text(250, 30, text='LEVEL', fill='white', font=('Helvetica', 12, 'bold'))
    c.create_text(350, 30, text='LIVES', fill='white', font=('Helvetica', 12, 'bold'))
    time_text = c.create_text(50, 55, fill='white', text='30', font=('Helvetica', 15))
    score_text = c.create_text(150, 55, fill='white', text='0', font=('Helvetica', 15))
    level_text = c.create_text(250, 55, fill='white', text='1', font=('Helvetica', 15))
    lives_text = c.create_text(350, 55, fill='white', text='3', font=('Helvetica', 15))
    ship_id = c.create_polygon(5, 5, 5, 25, 30, 15, fill='red')
    ship_id2 = c.create_oval(0, 0, 30, 30, outline='red')

def reset_ship():
    c.coords(ship_id, 5, 5, 5, 25, 30, 15); c.coords(ship_id2, 0, 0, 30, 30)
    c.move(ship_id, WIDTH/2, HEIGHT/2); c.move(ship_id2, WIDTH/2, HEIGHT/2)


def create_boss(hp_val, boss_num):
    global boss_id, boss_hp, boss_max_hp
    boss_hp = boss_max_hp = hp_val
    r = 50 if boss_num < 3 else 80  # Final Boss is huge
    color = 'purple' if boss_num < 3 else 'gold'
    boss_id = c.create_oval(WIDTH, HEIGHT/2-r, WIDTH+r*2, HEIGHT/2+r, fill=color, outline='white', width=4, tags='boss_obj')
    c.create_rectangle(500, 30, 750, 50, outline='white', tags='boss_ui')
    c.create_rectangle(500, 30, 750, 50, fill='red', tags=('boss_ui', 'boss_bar'))
    c.create_text(625, 20, text=f"BOSS {boss_num}", fill='white', font=('Helvetica', 10, 'bold'), tags='boss_ui')


def create_bubble():
    if boss_id: return 
    x, y, r = WIDTH + 100, randint(0, HEIGHT), randint(10, 30)
    chance = uniform(0, 100)
    
    if chance < 15:
        bub_id.append(c.create_oval(x-r, y-r, x+r, y+r, outline='red', fill='black', width=2)); bub_type.append('bomb')
    elif chance < 22: 
        bub_id.append(c.create_oval(x-r, y-r, x+r, y+r, outline='lightgreen', fill='green', width=2)); bub_type.append('bonus')
    elif chance < 28: 
        bub_id.append(c.create_oval(x-r, y-r, x+r, y+r, outline='cyan', fill='blue', width=2)); bub_type.append('shield')
    else: 
        bub_id.append(c.create_oval(x-r, y-r, x+r, y+r, outline='white')); bub_type.append('normal')
    
    bub_r.append(r)
    speed_boost = level // 3
    bub_speed.append(randint(2 + speed_boost, 5 + speed_boost))

def main_game_loop():
    global end_time, score, level, lives, shield_active, shield_ui, boss_id, boss_hp
    if running and not paused:
        if time() < end_time and lives > 0:
            # Controls
            if any(k in keys_pressed for k in ['Up', 'w']): c.move(ship_id, 0, -SHIP_SPD); c.move(ship_id2, 0, -SHIP_SPD)
            if any(k in keys_pressed for k in ['Down', 's']): c.move(ship_id, 0, SHIP_SPD); c.move(ship_id2, 0, SHIP_SPD)
            if any(k in keys_pressed for k in ['Left', 'a']): c.move(ship_id, -SHIP_SPD, 0); c.move(ship_id2, -SHIP_SPD, 0)
            if any(k in keys_pressed for k in ['Right', 'd']): c.move(ship_id, SHIP_SPD, 0); c.move(ship_id2, SHIP_SPD, 0)
            
            # Boss Spawning
            if not boss_id:
                if level == 10: create_boss(20, 1)
                elif level == 20: create_boss(40, 2)
                elif level == 30: create_boss(80, 3)
                if randint(1, 10) == 1: create_bubble()


            for i in range(len(bub_id)-1, -1, -1):
                wobble = sin(time() * 5) * ((level // 5) * 2) if level >= 5 else 0
                c.move(bub_id[i], -bub_speed[i], wobble)
                s_pos = c.coords(ship_id2)
                b_pos = c.coords(bub_id[i])
                dist = sqrt(((s_pos[0]+15)-(b_pos[0]+bub_r[i]))**2 + ((s_pos[1]+15)-(b_pos[1]+bub_r[i]))**2)
                if dist < (15 + bub_r[i]):
                    t = bub_type[i]
                    if t == 'bomb':
                        if shield_active: shield_active = False; c.delete(shield_ui)
                        else: lives -= 1; play_sound(BOMB_SOUND)
                    elif t == 'bonus': end_time += 5; play_sound(POP_SOUND)
                    elif t == 'shield':
                        shield_active = True; play_sound(POP_SOUND)
                        if shield_ui: c.delete(shield_ui)
                        shield_ui = c.create_oval(0,0,0,0, outline='cyan', width=2)
                    else: score += bub_r[i]; play_sound(POP_SOUND)
                    c.delete(bub_id[i]); del bub_id[i], bub_r[i], bub_speed[i], bub_type[i]

            if boss_id:
                c.move(boss_id, -2, sin(time() * 4) * 6)
                s_pos = c.coords(ship_id2)
                b_pos = c.coords(boss_id)
                boss_r = 80 if level == 30 else 50
                dist = sqrt(((s_pos[0]+15)-(b_pos[0]+boss_r))**2 + ((s_pos[1]+15)-(b_pos[1]+boss_r))**2)
                if dist < (15 + boss_r):
                    boss_hp -= 1; play_sound(POP_SOUND)
                    c.coords('boss_bar', 500, 30, 500 + (boss_hp/boss_max_hp)*250, 50)
                    if boss_hp <= 0:
                        c.delete(boss_id, 'boss_ui', 'boss_obj'); boss_id = None; score += 2000; level += 1

            if shield_active:
                sp = c.coords(ship_id2)
                c.coords(shield_ui, sp[0]-5, sp[1]-5, sp[2]+5, sp[3]+5)

          
            new_lvl = min(30, (score // 500) + 1)
            if new_lvl > level and not boss_id:
                level = new_lvl; end_time += randint(2, 5)
            
            c.itemconfig(score_text, text=str(score))
            c.itemconfig(time_text, text=str(int(max(0, end_time - time()))))
            c.itemconfig(level_text, text=str(level))
            c.itemconfig(lives_text, text=str(lives))
            window.after(30, main_game_loop)
        else: show_retry_screen()

def show_retry_screen():
    c.create_text(WIDTH/2, HEIGHT/2, text="GAME OVER", fill='white', font=('Helvetica', 50), tags='end')
    btn = c.create_text(WIDTH/2, HEIGHT/2 + 70, text="RETRY", fill='yellow', font=('Helvetica', 25, 'bold'), tags='end')
    c.tag_bind(btn, '<Button-1>', lambda e: start_game())

def start_game():
    global score, level, lives, end_time, shield_active, boss_id; c.delete('all'); setup_ui()
    score, level, lives, shield_active, boss_id = 0, 1, 3, False, None
    end_time = time() + 30
    reset_ship(); main_game_loop()

c.bind_all('<KeyPress>', lambda e: keys_pressed.add(e.keysym))
c.bind_all('<KeyRelease>', lambda e: keys_pressed.discard(e.keysym))
threading.Thread(target=music_loop_thread, daemon=True).start()
start_game(); window.mainloop()
