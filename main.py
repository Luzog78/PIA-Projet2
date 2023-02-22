import sys
import math
import pygame


class Line:
    def __init__(self, pos1, pos2, x2=None, y2=None):
        if x2 is None or y2 is None:
            self.pos1 = pos1
            self.pos2 = pos2
        else:
            self.pos1 = pos1, pos2
            self.pos2 = x2, y2

    def draw(self, screen, color=(255, 255, 255), width=1):
        pygame.draw.line(screen, color, self.pos1, self.pos2, width)

    def get_rect(self):
        return pygame.Rect(self.pos1[0], self.pos1[1], self.pos2[0] - self.pos1[0], self.pos2[1] - self.pos1[1])

    def get_near(self, pos) -> tuple[int, int]:
        x1, y1 = self.pos1
        x2, y2 = self.pos2
        x, y = pos
        if x1 == x2:
            return x1, y
        elif y1 == y2:
            return x, y1
        else:
            m = (y2 - y1) / (x2 - x1)
            b = y1 - m * x1
            return (y - b) / m, y

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
    objects = []

    @staticmethod
    def create_regular_polygon(pos, radius: int, n: int = 20, offset_rad: int | float = 0):
        return LinearObject(*[(pos[0] + radius * math.cos(2 * math.pi * i / n + offset_rad),
                               pos[1] + radius * math.sin(2 * math.pi * i / n + offset_rad)) for i in range(n)])

    def __init__(self, pos0, *pos):
        self.pos = [pos0]
        for p in pos:
            self.pos.append(p)
        self.lines: list[Line] = []
        self.update_lines()

    def register(self):
        if self not in LinearObject.objects:
            LinearObject.objects.append(self)
        return self

    def unregister(self):
        if self in LinearObject.objects:
            LinearObject.objects.remove(self)
        return self

    def update_lines(self):
        self.lines = []
        for i in range(len(self.pos) - 1):
            self.lines.append(Line(self.pos[i], self.pos[i + 1]))
        if len(self.pos) > 2:
            self.lines.append(Line(self.pos[-1], self.pos[0]))

    def draw(self, screen, color=(255, 255, 255), width=1):
        for line in self.lines:
            line.draw(screen, color, width)

    def get_bounds(self) -> tuple[tuple[float, float], tuple[float, float]]:
        x1, y1 = x2, y2 = self.pos[0]
        for pos in self.pos:
            x1 = min(x1, pos[0])
            y1 = min(y1, pos[1])
            x2 = max(x2, pos[0])
            y2 = max(y2, pos[1])
        return (x1, y1), (x2, y2)

    def get_size(self) -> tuple[float, float]:
        return self.get_bounds()[1][0] - self.get_bounds()[0][0], \
               self.get_bounds()[1][1] - self.get_bounds()[0][1]

    def get_center(self) -> tuple[float, float]:
        return (self.get_bounds()[0][0] + self.get_bounds()[1][0]) / 2, \
               (self.get_bounds()[0][1] + self.get_bounds()[1][1]) / 2

    def get_relative(self, pos) -> tuple[float, float]:
        return pos[0] - self.get_bounds()[0][0], pos[1] - self.get_bounds()[0][1]

    def get_intersection_with(self, other) -> tuple[tuple[tuple[float, float],
                                                          tuple[float, float] | None,
                                                          tuple[float, float] | None], Line, Line] | None:
        for line in self.lines:
            for line2 in other.lines:
                if (inter := line.get_intersection_with(line2)) is not None:
                    return inter, line, line2
        return None

    def get_intersection_with_line(self, line) -> tuple[tuple[tuple[float, float],
                                                              tuple[float, float] | None,
                                                              tuple[float, float] | None], Line] | None:
        for l in self.lines:
            if (inter := l.get_intersection_with(line)) is not None:
                return inter, l
        return None


class Utils:
    @staticmethod
    def get_distance(pos1, pos2) -> float:
        return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

    @staticmethod
    def get_angle(pos1, pos2) -> float:
        return math.atan2(pos2[1] - pos1[1], pos2[0] - pos1[0])

    @staticmethod
    def get_angle_between(pos, pos1, pos2) -> float:
        return Utils.get_angle(pos, pos1) - Utils.get_angle(pos, pos2)

    @staticmethod
    def get_angle_by_coef(alpha1, alpha2) -> float:
        if alpha1 == alpha2 or (alpha1 is None and alpha2 is None):
            return 0
        add = 0
        if alpha1 is None:
            a1 = 0
            add = math.pi / 2
        else:
            a1 = alpha1
        if alpha2 is None:
            a2 = 0
            add = math.pi / 2
        else:
            a2 = alpha2
        return math.atan((a1 - a2) / (1 + a1 * a2)) + add

    @staticmethod
    def minimize_angle(rad) -> float:
        a = rad % (2 * math.pi)
        if a > math.pi:
            a -= 2 * math.pi
        return a

    @staticmethod
    def positivize_angle(rad) -> float:
        a = rad % (2 * math.pi)
        if a < 0:
            a += 2 * math.pi
        return a

    @staticmethod
    def get_magnitude(pos) -> float:
        return math.sqrt(pos[0] ** 2 + pos[1] ** 2)

    @staticmethod
    def deg2rad(deg) -> float:
        return deg * math.pi / 180

    @staticmethod
    def rad2deg(rad) -> float:
        return rad * 180 / math.pi

    @staticmethod
    def are_close(num1, num2) -> bool:
        return abs(num1 - num2) < 0.0001


LinearObject.objects: list[LinearObject] = []

pygame.init()

size = 1080, 720

screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
fps = 200

ball = pygame.image.load("ball.png").convert_alpha()
ball = pygame.transform.rotozoom(ball, 0, 0.25)  # rotate: 0°, scale: x0.25

friction = 0.5

position = 350, 300
velocity = -200, 250

LinearObject((300, 200), (800, 200), (800, 400), (300, 400)).register()


def tick():
    global position, velocity

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    # --- Logic ---

    back = position[:]

    # Damping with friction
    velocity = velocity[0] * (1 - friction / fps), velocity[1] * (1 - friction / fps)
    tempo_velocity = velocity[0] / 100, velocity[1] / 100

    position = position[0] + tempo_velocity[0], position[1] + tempo_velocity[1]

    if Utils.get_magnitude(velocity) < 3:
        velocity = 0, 0

    collider = LinearObject.create_regular_polygon(position, 17, 6, math.pi / 6)
    if velocity[0] != 0:
        for obj in LinearObject.objects:
            if (i := collider.get_intersection_with(obj)) is not None:
                position = back

                # Matrix:      Q = [[cos a, sin a], [-sin a, cos a]]
                # Matrix: Q^(-1) = [[cos a, -sin a], [sin a, cos a]]
                # Transformation: P = [[1, 0], [0, -1]] ->> reflection on the x-axis
                # reflection = Q * velocity * P * Q^(-1)

                # angle of linear function = arctan( multiplier )
                a = (math.pi / 2) if i[0][2] is None else math.atan(i[0][2][0])

                # Q * velocity = (vx * cos a + vy * sin a, -vx * sin a + vy * cos a)
                relative_velocity = velocity[0] * math.cos(a) + velocity[1] * math.sin(a), \
                                    -velocity[0] * math.sin(a) + velocity[1] * math.cos(a)

                # relative_velocity * P => (vx, -vy)
                relative_velocity = relative_velocity[0], -relative_velocity[1]

                # reflection = relative_velocity * Q^(-1)
                velocity = relative_velocity[0] * math.cos(a) - relative_velocity[1] * math.sin(a), \
                           relative_velocity[0] * math.sin(a) + relative_velocity[1] * math.cos(a)

    print(velocity, clock.get_fps())

    # --- Drawing ---

    screen.fill((0, 0, 0))

    screen.blit(ball, (position[0] - ball.get_rect().size[0] // 2,
                       position[1] - ball.get_rect().size[1] // 2))

    LinearObject.objects[0].draw(screen, (0, 255, 255), 2)
    # collider.draw(screen, (0, 255, 0), 1)


while True:
    # --- Updating ---

    tick()

    pygame.display.update()
    clock.tick(fps)
