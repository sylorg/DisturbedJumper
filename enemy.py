import pygame
import random

class Enemy(pygame.sprite.Sprite):
	def __init__(self, SCREEN_WIDTH, y, sprite_sheet, scale):
		pygame.sprite.Sprite.__init__(self)
		#обозанаем переменные
		self.animation_list = []
		self.frame_index = 0
		self.update_time = pygame.time.get_ticks()
		self.direction = random.choice([-1, 1])
		if self.direction == 1:
			self.flip = True
		else:
			self.flip = False

		#подгружаем изображения из спрайтового изображения
		animation_steps = 8
		for animation in range(animation_steps):
			image = sprite_sheet.get_image(animation, 320, 320, scale, (0, 0, 0))
			image = pygame.transform.flip(image, self.flip, False)
			image.set_colorkey((0, 0, 0))
			self.animation_list.append(image)
		
		#select starting image and create rectangle from itвыбор стартовой картинки и создание из нее ректа
		self.image = self.animation_list[self.frame_index]
		self.rect = self.image.get_rect()

		if self.direction == 1:
			self.rect.x = 0
		else:
			self.rect.x = SCREEN_WIDTH
		self.rect.y = y

	def update(self, scroll, SCREEN_WIDTH):
		#обновление анимации
		ANIMATION_COOLDOWN = 50
		#обновление картинки в зависимости от текущего фрейма
		self.image = self.animation_list[self.frame_index]
		#проверка на то, что прошло достаточно времени с предыдущего кадра
		if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
			self.update_time = pygame.time.get_ticks()
			self.frame_index += 1
		#если анимация кончилась, то сбросить ее и начать снова
		if self.frame_index >= len(self.animation_list):
			self.frame_index = 0

		#двиг жнеца
		self.rect.x += self.direction * 2
		self.rect.y += scroll

		#проверка на исчезновение с экрана
		if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
			self.kill()