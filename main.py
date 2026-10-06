# James Cocone
# AI For Game Programming
# Ms. Qiu - Period 7

import pygame
import random
import math
import asyncio

async def main():
  pygame.init()

  WIDTH, HEIGHT = 600, 400

  screen = pygame.display.set_mode((WIDTH, HEIGHT))
  clock = pygame.time.Clock()
  running = True

  NUM_ASTEROIDS = 5

  ROTATION_SPEED = 3

  THRUST = 0.15
  DRAG = 0.99
  MAX_SPEED = 7

  MISSILE_SPEED = 7

  ENEMY_SPEED = 1.5
  DETECTION_RANGE = 200

  font = pygame.font.SysFont(None, 30)

  class Spaceship:
    def __init__(self, x, y):
      self.position = pygame.Vector2(x, y)
      self.velocity = pygame.Vector2(0, 0)
      self.acceleration = pygame.Vector2(0, 0)
      self.angle = 90
      self.radius = 18
      
      
    def get_forward_vector(self):
      radians = math.radians(self.angle)
      forward = pygame.Vector2(
        math.cos(radians),
        -math.sin(radians)
      )
      
      return forward
    
    def update(self):
      keys = pygame.key.get_pressed()
      
      if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        self.angle += ROTATION_SPEED
        
      if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        self.angle -= ROTATION_SPEED
        
      forward = self.get_forward_vector()
      
      self.acceleration = pygame.Vector2(0, 0)
      
      if keys[pygame.K_UP] or keys[pygame.K_w]:
        self.acceleration = forward * THRUST
        
      self.velocity += self.acceleration
      self.velocity *= DRAG

      if self.velocity.length() > MAX_SPEED:
        self.velocity.scale_to_length(MAX_SPEED)
        
      self.position += self.velocity
      
      if self.position.x > WIDTH:
        self.position.x = 0

      if self.position.x < 0:
        self.position.x = WIDTH

      if self.position.y > HEIGHT:
        self.position.y = 0

      if self.position.y < 0:
        self.position.y = HEIGHT
        
    def draw(self):
      forward = self.get_forward_vector()
      
      left = forward.rotate(140)
      right = forward.rotate(-140)

      front = self.position + forward * 22
      back_left = self.position + left * 17
      back_right = self.position + right * 17


      pygame.draw.polygon(
        screen,
        "white",
        [front, back_left, back_right],
        2
      )
        
    def draw_forward_vector(self):
      forward = self.get_forward_vector()

      end_point = (
        self.position + forward * 60
      )

      pygame.draw.line(
        screen,
        "red",
        self.position,
        end_point,
        2
      )
      
    def draw_velocity_vector(self):
        if self.velocity.length() > 0.1:
          end_point = (self.position + self.velocity * 10)

          pygame.draw.line(
            screen,
            "blue",
            self.position,
            end_point,
            3
          )
          
  class Enemy:
    def __init__(self, x, y):
      self.position = pygame.Vector2(x, y)
      
      self.angle = 0
      self.velocity = pygame.Vector2(0, 0)
      
      self.radius = 20
      self.state = "PATROL"
      
      self.distance = 0
      self.dot = 0
      
      self.fire_timer = 0
      
    def get_forward_vector(self):
      radians = math.radians(self.angle)
      forward = pygame.Vector2(
        math.cos(radians),
        -math.sin(radians)
      )
      
      return forward
    
    def update(self, player):
      enemy_forward = self.get_forward_vector()
      to_player = player.position - self.position 
      self.distance = to_player.length()
      if to_player.length() > 0:
        to_player = to_player.normalize()
      self.dot = enemy_forward.dot(to_player)
      
      if (self.distance < DETECTION_RANGE):
          self.state = "ATTACK"
      else:
          self.state = "PATROL"
          
      if self.state == "PATROL":
        self.angle += 1

        enemy_forward = self.get_forward_vector()
        self.position += enemy_forward * ENEMY_SPEED 
      else:
        enemy_forward = self.get_forward_vector()

        to_player = player.position - self.position

        if to_player.length() > 0:
          to_player = to_player.normalize()

          turn = enemy_forward.cross(to_player)

          if turn > 0:
              self.angle -= 2
          elif turn < 0:
              self.angle += 2

        enemy_forward = self.get_forward_vector()

        self.position += enemy_forward * ENEMY_SPEED
        
        self.fire_timer += 1

        if self.fire_timer >= 60:

          missile_start = self.position + enemy_forward * 24

          enemy_missiles.append(
            Missile(
              missile_start,
              enemy_forward
            )
          )

          self.fire_timer = 0
          
      if self.position.x > WIDTH + self.radius:
        self.position.x = -self.radius

      if self.position.x < -self.radius:
        self.position.x = WIDTH + self.radius

      if self.position.y > HEIGHT + self.radius:
        self.position.y = -self.radius

      if self.position.y < -self.radius:
        self.position.y = HEIGHT + self.radius

    def draw(self):
      forward = self.get_forward_vector()

      left = forward.rotate(140)
      right = forward.rotate(-140)

      front = self.position + forward * 24
      back_left = self.position + left * 18
      back_right = self.position + right * 18

      if self.state == "ATTACK":
        color = "red"
      else:
        color = "white"

      pygame.draw.polygon(
        screen,
        color,
        [front, back_left, back_right],
        2
      )

      pygame.draw.circle(
        screen,
        (80, 80, 80),
        (
          int(self.position.x),
          int(self.position.y)
        ),
        DETECTION_RANGE,
        1
      )

      pygame.draw.line(
        screen,
        "red",
        self.position,
        self.position + forward * 100,
        3
      )
          
  class Asteroid:
    def __init__(self):
      self.radius = random.randint(18, 35)
      self.position = pygame.Vector2(
        random.randint(self.radius, WIDTH - self.radius),
        random.randint(self.radius, HEIGHT - self.radius)
      )
      
      angle = random.uniform(0, 2 * math.pi)
      
      speed = random.uniform(1.0, 2.5)
      
      self.velocity = pygame.Vector2(math.cos(angle), math.sin(angle) * speed)
      
    def update(self):
      self.position += self.velocity

      if self.position.x > WIDTH + self.radius:
        self.position.x = -self.radius

      if self.position.x < -self.radius:
        self.position.x = WIDTH + self.radius

      if self.position.y > HEIGHT + self.radius:
        self.position.y = -self.radius

      if self.position.y < -self.radius:
        self.position.y = HEIGHT + self.radius
        
    def draw(self):
      pygame.draw.circle(
        screen,
        "gray",
        (
          int(self.position.x),
          int(self.position.y)
        ),
        self.radius
      )
      
  class Missile: 
    def __init__(self, start_position, direction):
      self.position = pygame.Vector2(
        start_position
      )

      self.radius = 4

      self.velocity = (
        direction * MISSILE_SPEED
      )

    def update(self):
      self.position += self.velocity

    def draw(self):
      pygame.draw.circle(
        screen,
        "yellow",
        (
          int(self.position.x),
          int(self.position.y)
        ),
        self.radius
      )

    def is_off_screen(self):
      return (
        self.position.x < 0
        or self.position.x > WIDTH
        or self.position.y < 0
        or self.position.y > HEIGHT
      )
      
  def missile_hits_asteroid(missile,asteroid):
    distance = (missile.position.distance_to(asteroid.position))

    return (distance < missile.radius + asteroid.radius)

  def missile_hits_ship(missile, ship):
      distance = missile.position.distance_to(ship.position)

      return distance < missile.radius + ship.radius


  player = Spaceship(
    WIDTH / 2,
    HEIGHT / 2
  )

  enemy = Enemy(
      WIDTH / 4,
      HEIGHT / 2
  )

  asteroids = []

  for i in range(NUM_ASTEROIDS):
      asteroids.append(
          Asteroid()
      )

  missiles = []
  enemy_missiles = []

  score = 0

  running = True

  while running:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
          forward = player.get_forward_vector()
        
          missile_start = (player.position + forward * 24)

          new_missile = Missile(missile_start, forward)

          missiles.append(new_missile)
        
    player.update()
    
    enemy.update(player)
    
    for asteroid in asteroids:
      asteroid.update()

    for missile in missiles:
      missile.update()
      
    missiles = [
      missile
      for missile in missiles
      if not missile.is_off_screen()
    ]
    
    for missile in enemy_missiles:
      missile.update()
      
    enemy_missiles = [
      missile
      for missile in enemy_missiles
      if not missile.is_off_screen()
    ]

    for missile in missiles[:]:
      for asteroid in asteroids[:]:
        if missile_hits_asteroid(missile, asteroid):
          if missile in missiles:
            missiles.remove(missile)

            if asteroid in asteroids:
              asteroids.remove(asteroid)
              
              asteroids.append(Asteroid())

              score += 1

              break
            
    for missile in enemy_missiles:
      if missile_hits_ship(missile, player):
          running = False
            
    screen.fill((20, 24, 40))

    for asteroid in asteroids:
      asteroid.draw()

    for missile in missiles:
      missile.draw()
      
    for missile in enemy_missiles:
      missile.draw()

      
    enemy.draw()
      
    player.draw_forward_vector()
    player.draw_velocity_vector()
    player.draw()
    
    forward = (
      player.get_forward_vector()
    )

    speed = (
      player.velocity.length()
    )
    
    dot_text = font.render(
      f"Dot Product: {enemy.dot:.2f}",
      True,
      "white"
    )
    
    screen.blit(
      dot_text,
      (10, 10)
    )
    
    score_text = font.render(
      f"Score: {score}",
      True,
      "white"
    )

    screen.blit(score_text, (10, 40))
    
    pygame.display.flip()
    clock.tick(60)
    await asyncio.sleep(0)
asyncio.run(main())