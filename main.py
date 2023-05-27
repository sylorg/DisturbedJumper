#импорт библиотек
import pygame
import random
import os
from pygame import mixer
from spritesheet import SpriteSheet
from enemy import Enemy

#инициализация пайгейма
mixer.init()
pygame.init()

#Размеры игрового окна
SCREEN_WIDTH = 700
SCREEN_HEIGHT =int(SCREEN_WIDTH*(8/6))


#создает игровое окно
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Disturbed Jumper')

#задаем фпс
clock = pygame.time.Clock()
FPS = 70

#подгружаем музыку и звуки
musix_fx=pygame.mixer.Sound('assets/music.mp3')
pygame.mixer.music.load('assets/music.mp3')
pygame.mixer.music.set_volume(0.7)
pygame.mixer.music.play(-1, 0.0)
jump_fx = pygame.mixer.Sound('assets/jump.mp3')
jump_fx.set_volume(1)
death_fx = pygame.mixer.Sound('assets/death.mp3')
death_fx.set_volume(1)
death1_fx = pygame.mixer.Sound('assets/death1.mp3')
death1_fx.set_volume(1)


#игровые переменные
SCROLL_THRESH = 200*SCREEN_HEIGHT/600
GRAVITY = 1
MAX_PLATFORMS = 8
scroll = 0
bg_scroll = 0
game_over = False
score = 0
fade_counter = 0
p_moving = False

if os.path.exists('score.txt'):
	with open('score.txt', 'r') as file:
		high_score = int(file.read())
else:
	high_score = 0

#задаю цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PANEL = (255, 0, 0)
RED= (255,0,0)

#задаю шрифт
font_small = pygame.font.SysFont('abaddoncyr', 20)
font_big = pygame.font.SysFont('abaddoncyr', 24)

#подружаем изображение
jumpy_image = pygame.image.load('assets/jump.png').convert_alpha()
bg_image = pygame.image.load('assets/bg.png').convert_alpha()
bg_image = pygame.transform.scale(bg_image,(SCREEN_WIDTH,SCREEN_HEIGHT))
bgs_image = pygame.image.load('assets/bgS.png').convert_alpha()
bgs_image = pygame.transform.scale(bgs_image,(SCREEN_WIDTH,SCREEN_HEIGHT))
platform_image = pygame.image.load('assets/platf.png').convert_alpha()
#Спрайты жнеца
death_sheet_img = pygame.image.load('assets/death.png').convert_alpha()
death_sheet = SpriteSheet(death_sheet_img)


#функция для вывода текста на экран
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

#Функция для отрисовки панели со счетом
def draw_panel():
	pygame.draw.rect(screen, PANEL, (0, 0, SCREEN_WIDTH, 30))
	pygame.draw.line(screen, WHITE, (0, 30), (SCREEN_WIDTH, 30), 2)
	draw_text('СЧЕТ ' + str(score), font_small, WHITE, 0, 0)


#функция для отрисовки фона
def draw_bg(bg_scroll):
	screen.blit(bg_image, (0, 0 + bg_scroll))
	screen.blit(bg_image, (0, -SCREEN_HEIGHT + bg_scroll))
def draw_bgs():
	screen.blit(bgs_image, (0, 0))

#класс игрока
class Player():
	def __init__(self, x, y):
		self.image = pygame.transform.scale(jumpy_image, (45*1.5*SCREEN_WIDTH/400, 45*1.5*SCREEN_HEIGHT/600))
		self.width = 25*1.5*SCREEN_WIDTH//400
		self.height = 40*1.5*SCREEN_HEIGHT//600
		self.rect = pygame.Rect(0, 0, self.width, self.height)
		self.rect.center = (x, y)
		self.vel_y = 0
		self.flip = False


	def move(self):
		#reset variables
		scroll = 0
		dx = 0
		dy = 0

		#обработка кнопок
		key = pygame.key.get_pressed()
		if key[pygame.K_a]:
			dx = -10*SCREEN_WIDTH/400
			self.flip = True
		if key[pygame.K_d]:
			dx = 10*SCREEN_WIDTH/400
			self.flip = False

		#гравитация
		self.vel_y += GRAVITY
		dy += self.vel_y

		#чтобы игрок не вышел за границы экрана
		if self.rect.left + dx < 0:
			dx = -self.rect.left
		if self.rect.right + dx > SCREEN_WIDTH:
			dx = SCREEN_WIDTH - self.rect.right


		#проверяем коллизию с платформой
		for platform in platform_group:
			#коллизия по Y направлению
			if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				#проверяем если над платформой
				if self.rect.bottom < platform.rect.centery:
					if self.vel_y > 0:
						self.rect.bottom = platform.rect.top
						dy = 0
						self.vel_y=0
						if key[pygame.K_SPACE]:
							self.vel_y = -15*SCREEN_HEIGHT/600
							jump_fx.play()


		#проверка на достижения верха экрана
		if self.rect.top <= SCROLL_THRESH:
			#елси он в прыжке
			if self.vel_y < 0:
				scroll = -dy

		#обновнление позиции ректа
		self.rect.x += dx
		self.rect.y += dy + scroll

		#обновление маски
		self.mask = pygame.mask.from_surface(self.image)

		return scroll

	def draw(self):
		screen.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x - 12, self.rect.y - 5))

#класс платформы
class Platform(pygame.sprite.Sprite):
	def __init__(self, x, y, width, moving):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.transform.scale(platform_image, (width*1.5, 20*SCREEN_HEIGHT/600))
		self.moving = moving
		self.move_counter = random.randint(0, 50)
		self.direction = random.choice([-1, 1])
		self.speed = random.randint(1, 10)
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

	def update(self, scroll):
		#Движение платформы из стороны в сторону если это двигающаяся платформа
		if self.moving == True:
			self.move_counter += 1
			self.rect.x += self.direction * self.speed

		#Изменить направление платформы если та достигла края экрана
		if self.move_counter >= 200 or self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
			self.direction *= -1
			self.move_counter = 0

		#обновление вертикальной позиции платформы
		self.rect.y += scroll

		#проверка на исчезновение платформы с экрана
		if self.rect.top > SCREEN_HEIGHT:
			self.kill()

#инстанс плеера
jumpy = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)

#создаем группы спрайтов
platform_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

#создаем стартовую платформу
platform = Platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50, 100, False)
platform_group.add(platform)

#цикл игры
run = True
while run:

	clock.tick(FPS)
	if game_over == False:
		scroll = jumpy.move()

		#отрисовка фона
		bg_scroll += scroll
		if bg_scroll >= SCREEN_HEIGHT:
			bg_scroll = 0
		draw_bgs()
		draw_bg(bg_scroll)

		#оздание платформ
		if len(platform_group) < MAX_PLATFORMS:
			p_w = random.randint(40*SCREEN_WIDTH/400, 60*SCREEN_WIDTH/600)
			p_x = random.randint(0, SCREEN_WIDTH - p_w)
			p_y = platform.rect.y - random.randint(int(80*SCREEN_HEIGHT/400), int(120*SCREEN_HEIGHT/600))
			p_type = random.randint(1,10)
			print(platform_group)
			if p_type == 2 and score >=0:
				p_moving = True
			elif p_type ==3 and score >1000:
				p_moving = True
			elif p_type ==4 and score >2000:
				p_moving = True
			elif p_type ==5 and score >3000:
				p_moving = True
			elif p_type ==6 and score >4000:
				p_moving = True
			elif p_type ==7 and score >5000:
				p_moving = True
			elif p_type ==8 and score >6000:
				p_moving = True
			else:
				p_moving = False
			platform = Platform(p_x, p_y, p_w, p_moving)
			platform_group.add(platform)

		#обновление платформ
		platform_group.update(scroll)

		#создание жнеца
		if len(enemy_group) == 0 and score > 1000:
			enemy = Enemy(SCREEN_WIDTH, 100, death_sheet, 0.35)
			enemy_group.add(enemy)

		#обновить жнеца
		enemy_group.update(scroll, SCREEN_WIDTH)

		#обновить счет
		if scroll > 0:
			score += int(scroll)

		#отрисовка линии прошлого хай скора
		pygame.draw.line(screen, WHITE, (0, score - high_score + SCROLL_THRESH), (SCREEN_WIDTH, score - high_score + SCROLL_THRESH), 3)
		draw_text('ЛУЧШИЙ СЧЕТ', font_small, WHITE, SCREEN_WIDTH - 130, score - high_score + SCROLL_THRESH)

		#отрисовка спрайтов
		platform_group.draw(screen)
		enemy_group.draw(screen)
		jumpy.draw()

		#отрисовка панели
		draw_panel()

		#проверка на поражение
		if jumpy.rect.top > SCREEN_HEIGHT:
			game_over = True
			death_fx.play()
			pygame.mixer_music.pause()
		#проверка на столкновение со жнецом
		if pygame.sprite.spritecollide(jumpy, enemy_group, False):
			if pygame.sprite.spritecollide(jumpy, enemy_group, False, pygame.sprite.collide_mask):
				game_over = True
				death1_fx.play()
				pygame.mixer_music.pause()
	else:
		if fade_counter < SCREEN_WIDTH:
			fade_counter += 5
			for y in range(0, 6, 2):
				pygame.draw.rect(screen, RED, (0, y * 100*(SCREEN_WIDTH/400), fade_counter, 100*(SCREEN_WIDTH/400)))
				pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH - fade_counter, (y + 1) * 100*(SCREEN_WIDTH/400), SCREEN_WIDTH, 100*(SCREEN_WIDTH/400)))
		else:
			draw_text('ТЫ МЕРТВ', font_big, WHITE, 100*(SCREEN_WIDTH/400), 200*(SCREEN_HEIGHT/600))
			draw_text('СЧЕТ ' + str(score), font_big, WHITE, 100*(SCREEN_WIDTH/400), 250*(SCREEN_HEIGHT/600))
			draw_text('НАЖМИ ПРОБЕЛ ЧТОБЫ ПОПРОБОВАТЬ СНОВА', font_big, WHITE, 100*(SCREEN_WIDTH/400), 300*(SCREEN_HEIGHT/600))
			#обновить хай скор
			if score > high_score:
				high_score = score
				with open('score.txt', 'w') as file:
					file.write(str(high_score))
			key = pygame.key.get_pressed()
			if key[pygame.K_SPACE]:
				#сбросить переменные
				pygame.mixer_music.unpause()
				death_fx.stop()
				game_over = False
				score = 0
				scroll = 0
				fade_counter = 0
				#сбросить позицию чувачка
				jumpy.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)
				#сбросить врагов
				enemy_group.empty()
				#сбросить платформы
				platform_group.empty()
				#создать стартовую платформу
				platform = Platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50, 100, False)
				platform_group.add(platform)


	#управление ивентами
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			#обновление хай скора
			if score > high_score:
				high_score = score
				with open('score.txt', 'w') as file:
					file.write(str(high_score))
			run = False


	#обновление отображаемого окна
	pygame.display.update()



pygame.quit()

