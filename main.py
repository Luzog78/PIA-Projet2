import sys
import math
import pygame


class Line:
    def __init__(self, pos1, pos2):
        self.pos1 = pos1
        self.pos2 = pos2

    def draw(self, screen, color=(255, 255, 255), width=1):
        pygame.draw.line(screen, color, self.pos1, self.pos2, width)

    def get_intersection_with(self, other) -> tuple[tuple[float, float],
                                                    tuple[float, float] | None,
                                                    tuple[float, float] | None] | None:
        """
        :param other: Other line to check intersection with.
        :return: ((x, y), (alpha_self, beta_self) or None, (alpha_other, beta_other) or None) or None
        """
        x1, x2 = min(self.pos1[0], self.pos2[0]), max(self.pos1[0], self.pos2[0])
        y1, y2 = min(self.pos1[1], self.pos2[1]), max(self.pos1[1], self.pos2[1])
        x3, x4 = min(other.pos1[0], other.pos2[0]), max(other.pos1[0], other.pos2[0])
        y3, y4 = min(other.pos1[1], other.pos2[1]), max(other.pos1[1], other.pos2[1])
        if x1 == x2 and x3 == x4:  # both vertical
            if x1 == x3:  # same line
                if y1 <= y3 <= y2:
                    return (x1, y3), None, None
                if y1 <= y4 <= y2:
                    return (x1, y4), None, None
                if y3 <= y1 and y4 >= y2:
                    return (x1, y1), None, None
            return None
        elif x1 == x2:  # self vertical
            a2 = (y4 - y3) / (x4 - x3)
            b2 = y3 - a2 * x3
            x = x1
            y = a2 * x + b2
            if x3 <= x <= x4 and y1 <= y <= y2 and y3 <= y <= y4:
                return (x, y), None, (a2, b2)
            return None
        elif other.pos2[0] == other.pos1[0]:  # other vertical
            a1 = (y2 - y1) / (x2 - x1)
            b1 = y1 - a1 * x1
            x = x3
            y = a1 * x + b1
            if x1 <= x <= x2 and y1 <= y <= y2 and y3 <= y <= y4:
                return (x, y), (a1, b1), None
            return None
        else:
            # y = ax + b
            # a = (y2 - y1) / (x2 - x1)  !! x1 != x2 !!
            # b = y - ax
            a1 = (y2 - y1) / (x2 - x1)
            b1 = y1 - a1 * x1
            a2 = (y4 - y3) / (x4 - x3)
            b2 = y3 - a2 * x3
            if a1 == a2:  # parallel
                if b1 == b2:  # same line
                    line1, line2 = (self, other) if x1 <= x2 else (other, self)
                    if min(line2.pos1[0], line2.pos2[0]) <= max(line1.pos1[0], line1.pos2[0]):
                        x = min(line2.pos1[0], line2.pos2[0])
                        y = a1 * x + b1
                        return (x, y), (a1, b1), (a2, b2)
                return None
            else:  # intersect
                x = (b2 - b1) / (a1 - a2)
                y = a1 * x + b1
                if x1 <= x <= x2 and x3 <= x <= x4 and y1 <= y <= y2 and y3 <= y <= y4:
                    return (x, y), (a1, b1), (a2, b2)
                return None


class LinearObject:
    @staticmethod
    def create_regular_polygon(pos, radius: int, n: int, offset_rad: int | float = 0,
                               color: tuple[int, int, int] = (255, 255, 255), width: int = 1,
                               fill: bool | tuple[int, int, int] | None = None):
        return LinearObject(*[(pos[0] + radius * math.cos(2 * math.pi * i / n + offset_rad),
                               pos[1] + radius * math.sin(2 * math.pi * i / n + offset_rad)) for i in range(n)],
                            color=color, width=width, fill=fill)

    def __init__(self, *pos: tuple[int | float, int | float], relative: bool = False,
                 color: tuple[int, int, int] = (255, 255, 255), width: int = 1,
                 fill: bool | tuple[int, int, int] | None = None):
        self.color = color
        self.width = width
        self.fill = fill
        current = 0, 0
        self._pos = []
        for p in pos:
            current = (current[0] + p[0], current[1] + p[1]) if relative else p
            self._pos.append(current)
        self.lines: list[Line] = []
        self.update_lines()

    def update_lines(self):
        self.lines = []
        for i in range(len(self._pos) - 1):
            self.lines.append(Line(self._pos[i], self._pos[i + 1]))
        if len(self._pos) > 2:
            self.lines.append(Line(self._pos[-1], self._pos[0]))

    def draw(self, screen):
        if self.fill is not None and self.fill is not False:
            pygame.draw.polygon(screen, self.color if self.fill is True else self.fill, self._pos)
        for line in self.lines:
            line.draw(screen, self.color, self.width)

    def get_bounds(self) -> tuple[tuple[float, float], tuple[float, float]]:
        if len(self._pos) == 0:
            return (0, 0), (0, 0)
        x1, y1 = x2, y2 = self._pos[0]
        for pos in self._pos:
            x1 = min(x1, pos[0])
            y1 = min(y1, pos[1])
            x2 = max(x2, pos[0])
            y2 = max(y2, pos[1])
        return (x1, y1), (x2, y2)

    def get_center(self) -> tuple[float, float]:
        return (self.get_bounds()[0][0] + self.get_bounds()[1][0]) / 2, \
               (self.get_bounds()[0][1] + self.get_bounds()[1][1]) / 2

    def get_intersection_with(self, other) -> tuple[tuple[tuple[float, float],
                                                          tuple[float, float] | None,
                                                          tuple[float, float] | None], Line, Line] | None:
        for line in self.lines:
            for line2 in other.lines:
                if (inter := line.get_intersection_with(line2)) is not None:
                    return inter, line, line2
        return None


class Level:
    def __init__(self, name: str, start: LinearObject, finish: LinearObject, *obstacles: LinearObject):
        self.name = name
        self.start = start
        self.finish = finish
        self.obstacles = obstacles

    def draw(self, screen):
        for obstacle in self.obstacles:
            obstacle.draw(screen)
        self.start.draw(screen)
        self.finish.draw(screen)


class Utils:
    @staticmethod
    def get_distance(pos1, pos2) -> float:
        return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

    @staticmethod
    def get_magnitude(vec) -> float:
        return math.sqrt(vec[0] ** 2 + vec[1] ** 2)

    @staticmethod
    def set_magnitude(vec, magnitude: float) -> tuple[float, float]:
        if Utils.get_magnitude(vec) == 0:
            return (1 / math.sqrt(2) * magnitude,
                    1 / math.sqrt(2) * magnitude)
        return (vec[0] / Utils.get_magnitude(vec) * magnitude,
                vec[1] / Utils.get_magnitude(vec) * magnitude)


# --- Initializing ---

pygame.init()

SIZE = 1080, 720

SCREEN = pygame.display.set_mode(SIZE)
CLOCK = pygame.time.Clock()
FPS = 200

BALL = pygame.image.load("ball.png").convert_alpha()
BALL = pygame.transform.rotozoom(BALL, 0, 0.25)  # rotate: 0°, scale: x0.25

BACKGROUND = pygame.image.load("texture.png").convert_alpha()

FONT = pygame.font.SysFont("Arial", 30)

# --- Physics & Game Variables ---

FRICTION = 0.7
BOUNCE_FRICTION = 7

position = 0, 0
velocity = 0, 0

is_moving = False
MAX_VELOCITY = 300

current_game = 0
chrono = 0
moves = 0

# --- Building ---

levels = [
    Level("Niveau 1",
          LinearObject.create_regular_polygon((285, 190), 20, 20, color=(255, 0, 0), width=1, fill=(0, 0, 255)),
          LinearObject.create_regular_polygon((740, 510), 20, 20, color=(0, 0, 0), fill=(200, 200, 0)),
          LinearObject((240, 150), (600, 0), (0, 240), (-500, 0), (0, 80), (300, 0), (0, -40), (200, 0), (0, 160),
                       (-200, 0), (0, -40), (-400, 0), (0, -240), (500, 0), (0, -80), (-500, 0), relative=True)),
    Level("Niveau 2",
          LinearObject.create_regular_polygon((285, 190), 20, 20, color=(255, 0, 0), width=1, fill=(0, 0, 255)),
          LinearObject.create_regular_polygon((740, 510), 20, 20, color=(0, 0, 0), fill=(200, 200, 0)),
          LinearObject((240, 150), (200, 0), (0, -30), (200, 0), (0, 30), (200, 0),
                       (0, 240), (-200, 0), (0, 30), (-200, 0), (0, -30), (-100, 0),
                       (0, 80), (100, 0), (0, -20), (200, 0), (0, -20), (200, 0), (0, 160),
                       (-200, 0), (0, -20), (-200, 0), (0, -20), (-200, 0), (0, -240),
                       (200, 0), (0, -30), (200, 0), (0, 30), (100, 0), (0, -80),
                       (-100, 0), (0, 30), (-200, 0), (0, -30), (-200, 0), relative=True),
          LinearObject.create_regular_polygon((540, 190), 15, 3, color=(0, 128, 255), fill=True),
          LinearObject.create_regular_polygon((540, 350), 15, 5, color=(0, 128, 255), fill=True),
          LinearObject.create_regular_polygon((540, 510), 15, 6, color=(0, 128, 255), fill=True))
]


# --- Game ---

def testing_build():
    obj = LinearObject(color=(0, 255, 255), width=2)
    while True:
        # --- Updating ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        # --- Testing > Level Building ---
        if pygame.mouse.get_pressed()[2]:
            obj._pos = []
            obj.update_lines()

        if pygame.mouse.get_pressed()[0]:
            if pygame.mouse.get_pos() not in obj._pos:
                obj._pos.append(pygame.mouse.get_pos())
                obj.update_lines()

        print(obj._pos)

        SCREEN.fill((0, 0, 0))
        obj.draw(SCREEN)

        LinearObject.create_regular_polygon((540, 190), 12, 3, color=(0, 0, 255), fill=True).draw(SCREEN)
        LinearObject.create_regular_polygon((540, 350), 12, 5, color=(0, 0, 255), fill=True).draw(SCREEN)
        LinearObject.create_regular_polygon((540, 510), 12, 6, color=(0, 0, 255), fill=True).draw(SCREEN)

        pygame.display.update()
        CLOCK.tick(FPS)


def play(game: int = 0):
    global levels, position, current_game, chrono, moves, is_moving, velocity

    current_game = game
    chrono = 0
    moves = 0
    position = levels[current_game].start.get_center()
    velocity = 0, 0
    is_moving = False

    while True:
        # --- Updating ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        if current_game != -1 and tick(levels[current_game]):
            current_game += 1

            if len(levels) == current_game:
                print("You won !")
                current_game = -1

                font = pygame.font.SysFont("Arial", 100)
                text = font.render("Bravo !", True, (255, 255, 255))
                text2 = FONT.render("Temps : ", True, (255, 255, 255))
                text3 = FONT.render(f"{chrono:.1f} sec", True, (96, 96, 255))
                text4 = FONT.render("Mvts : ", True, (255, 255, 255))
                text5 = FONT.render(f"{moves}", True, (96, 255, 255))

                SCREEN.blit(text, (SIZE[0] / 2 - text.get_size()[0] / 2, SIZE[1] / 2 - text.get_size()[1] / 2))
                SCREEN.blit(text2, (15, 50))
                SCREEN.blit(text4, (15, 85))
                tab = max(text2.get_rect().size[0], text4.get_rect().size[0])
                SCREEN.blit(text3, (25 + tab, 50))
                SCREEN.blit(text5, (25 + tab, 85))

            else:
                position = levels[current_game].start.get_center()
                velocity = 0, 0
                is_moving = False

        pygame.display.update()
        CLOCK.tick(FPS)


def tick(level: Level):
    global position, velocity, is_moving, moves, chrono

    # --- Drawing ---

    for x in range(-100, SIZE[0] + BACKGROUND.get_size()[0], BACKGROUND.get_size()[0]):
        for y in range(-100, SIZE[1] + BACKGROUND.get_size()[1], BACKGROUND.get_size()[1]):
            SCREEN.blit(BACKGROUND, (x, y))
    level.draw(SCREEN)

    # --- Logic ---

    back = position[:]

    # Damping with friction
    velocity = velocity[0] * (1 - FRICTION / FPS), velocity[1] * (1 - FRICTION / FPS)
    tempo_velocity = velocity[0] / 100, velocity[1] / 100

    position = position[0] + tempo_velocity[0], position[1] + tempo_velocity[1]

    if 0 < Utils.get_magnitude(velocity) < 5:
        velocity = 0, 0
        is_moving = False

    collider = LinearObject.create_regular_polygon(position, 17, 50, math.pi / 6, color=(0, 255, 0))

    if not is_moving:
        mouse = pygame.mouse.get_pos()
        potential_velocity = (position[0] - mouse[0]) * 1.5, (position[1] - mouse[1]) * 1.5

        if Utils.get_magnitude(potential_velocity) > MAX_VELOCITY:
            potential_velocity = Utils.set_magnitude(potential_velocity, MAX_VELOCITY)

        potential_point = (collider.get_center()[0] + potential_velocity[0] * 0.5,
                           collider.get_center()[1] + potential_velocity[1] * 0.5)
        Line(collider.get_center(), potential_point).draw(SCREEN, (255, 0, 0))

        if pygame.mouse.get_pressed()[0]:
            moves += 1
            is_moving = True
            velocity = potential_velocity[0], potential_velocity[1]

    if Utils.get_distance(collider.get_center(), level.finish.get_center()) < 8:
        print("Finished!")
        for x in range(-100, SIZE[0] + BACKGROUND.get_size()[0], BACKGROUND.get_size()[0]):
            for y in range(-100, SIZE[1] + BACKGROUND.get_size()[1], BACKGROUND.get_size()[1]):
                SCREEN.blit(BACKGROUND, (x, y))
        return True

    if velocity[0] != 0:
        for obj in level.obstacles:
            if (i := collider.get_intersection_with(obj)) is not None:
                position = back

                # Matrix:      Q = [[cos a, sin a], [-sin a, cos a]]
                # Matrix: Q^(-1) = [[cos a, -sin a], [sin a, cos a]]
                # Transformation: P = [[1, 0], [0, -1]] ->> reflection on the x-axis
                # reflection = Q * velocity * P * Q^(-1)

                # angle of linear function = arctan( multiplier )
                a = (math.pi / 2) if i[0][2] is None else math.atan(i[0][2][0])

                # Q * velocity = (vx * cos a + vy * sin a, -vx * sin a + vy * cos a)
                relative_velocity = (velocity[0] * math.cos(a) + velocity[1] * math.sin(a),
                                     -velocity[0] * math.sin(a) + velocity[1] * math.cos(a))

                # relative_velocity * P => (vx, -vy)
                relative_velocity = relative_velocity[0], -relative_velocity[1]

                # reflection = relative_velocity * Q^(-1)
                velocity = (relative_velocity[0] * math.cos(a) - relative_velocity[1] * math.sin(a),
                            relative_velocity[0] * math.sin(a) + relative_velocity[1] * math.cos(a))

                # Apply bounce friction
                velocity = Utils.set_magnitude(velocity, Utils.get_magnitude(velocity) - BOUNCE_FRICTION)

    # --- Drawing ---

    SCREEN.blit(BALL, (position[0] - BALL.get_rect().size[0] // 2,
                       position[1] - BALL.get_rect().size[1] // 2))

    text1 = FONT.render(f"[ {level.name} ]", True, (255, 255, 255))
    text2 = FONT.render("Temps : ", True, (255, 255, 255))
    text3 = FONT.render(f"{chrono:.1f} sec", True, (96, 96, 255))
    text4 = FONT.render("Mvts : ", True, (255, 255, 255))
    text5 = FONT.render(f"{moves}", True, (96, 255, 255))
    text6 = FONT.render(f"Vitesse : ", True, (255, 255, 255))
    text7 = FONT.render(f"{int(Utils.get_magnitude(velocity))}", True, (255, 96, 255))
    text8 = FONT.render(f"FPS : {int(CLOCK.get_fps())}", True, (128, 128, 128))

    SCREEN.blit(text1, (15, 15))
    SCREEN.blit(text2, (15, 50))
    SCREEN.blit(text4, (15, 85))
    SCREEN.blit(text6, (15, 120))
    tab = max(text2.get_rect().size[0], text4.get_rect().size[0], text6.get_rect().size[0])
    SCREEN.blit(text3, (25 + tab, 50))
    SCREEN.blit(text5, (25 + tab, 85))
    SCREEN.blit(text7, (25 + tab, 120))
    SCREEN.blit(text8, (SIZE[0] - text8.get_rect().size[0] - 15, 15))

    chrono += 1 / FPS

    return False


play()