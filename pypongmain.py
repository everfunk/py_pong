import tkinter
import math
from PIL import Image,  ImageTk


class KeyTracker:
    pass


class GameField:
    def __init__(self):
        self.obstacle_list = []

    def add_obstacle(self, obstacle):
        self.obstacle_list.append(obstacle)
        pass

    def draw(self):
        pass
    pass


class Point2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def scalar(self, point):
        return self.x * point.x + self.y * point.y

    def add(self, point):
        return Point2D(self.x + point.x, self.y + point.y)

    def add_scaled(self, point, k):
        return Point2D(self.x + k * point.x, self.y + k * point.y)

    def scale(self, k):
        return Point2D(self.x * k, self.y * k)

    def diff(self, point):
        return Point2D(self.x - point.x, self.y - point.y)

    def norm(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def normalize(self):
        n = self.norm()
        if n > 0:
            return self.scale(1.0 / n)
        else:
            return Point2D(0.0, 0.0)


class Plane2D:
    def __init__(self, point, normal):
        self.point = point
        self.normal = normal.normalize()
        pass

    def apply(self, point):
        return self.normal.scalar(point.diff(self.point))

    pass


class Obstacle:
    def check(self, motion1, motion2):
        """
        по двум точкам движения и времени между ними
        возвращает признак нарушения, время и точку нарушения
        """
        return False, motion2, 0
        pass
    pass


class ObstacleView:
    def __init__(self, master, point1, point2):
        self.master = master
        self.firing = False
        pass

    def fire(self):
        self.firing = True
        self.master.after(200, lambda: self.dim)
        pass

    def dim(self):
        self.firing = False
        pass

    """
    def  draw(self, canvas):
        canvas.
    """


class Linear2DObstacle(Obstacle):
    def __init__(self, obstacle_id, plane, point1, point2):
        super().__init__()
        self.obstacle_id = obstacle_id
        self.plane = plane
        self.point1 = point1
        self.point2 = point2
        self.co_normal = Point2D(plane.normal.y, -plane.normal.x)
        v1 = self.co_normal.scalar(point1)
        v2 = self.co_normal.scalar(point2)
        self.v_min = min(v1, v2)
        self.v_max = max(v1, v2)
        pass

    def check(self, size, motion1, motion2):
        """
        по двум точкам движения и времени между ними
        возвращает признак нарушения, время и точку нарушения
        """
        val1 = self.plane.apply(motion1.pos)
        val2 = self.plane.apply(motion2.pos)
        if val1 >= size * 0.5 and val2 > size * 0.5:
            """обе точки с одной стороны ограничения"""
            return False, motion2, 0, self.plane.normal
        else:
            """при движении пересечена линия ограничения"""
            """определяем границы"""

            part = (val1 - size * 0.5) / (val1 - val2)
            point = motion1.pos.add(motion2.pos.diff(motion1.pos).scale(part))

            if self.v_min <= self.co_normal.scalar(point) <= self.v_max:
                """полный отскок"""
                new_motion = Motion()
                new_motion.velocity = motion1.velocity
                new_motion.pos = point
                new_motion.phi = motion1.phi
                new_motion.omega = motion1.omega
                return True, new_motion, part, self.plane.normal

            direction = Plane2D(motion1.pos, Point2D(motion1.velocity.y, -motion1.velocity.x))
            if abs(direction.apply(self.point1)) <= size*0.5 or abs(direction.apply(self.point2)) <= size*0.5:
                """задели за край"""
                print(motion1.pos.x, motion1.pos.x, motion1.velocity.x, motion1.velocity.y, val1, val2)
                new_motion = Motion()
                new_motion.velocity = motion1.velocity
                new_motion.pos = point
                new_motion.phi = motion1.phi
                new_motion.omega = motion1.omega
                return True, new_motion, part, self.plane.normal

            return False, motion2, 0, self.plane.normal
        pass
    pass


class ObstacleRepresentation:
    def __init__(self, obstacle):
        self.obstacle = obstacle
    pass


class Ball:
    def __init__(self):
        self.visible = 0.0
        self.radius = 10.0
        self.motion = Motion()
        self.motion.pos.x = 40
        self.motion.pos.y = 20
        self.motion.velocity.x = 0.02
        self.motion.velocity.y = 0.02
        self.size = 40

    def set_motion(self, m):
        self.motion = m
        pass


class Motion:
    def __init__(self):
        self.pos = Point2D(0.0, 0.0)
        self.phi = 0.0

        self.velocity = Point2D(0.0, 0.0)
        self.omega = 0.1
        pass


class FiredObstacle:
    def __init__(self, motion, part, normal):
        self.motion = motion
        self.part = part
        self.normal = normal
        pass


class BallPhysics:
    def __init__(self, ball, obstacles):
        self.ball = ball
        """список препятствий"""
        self.obstacles = obstacles

    def update_motion(self, motion, time):
        """движение"""
        new_motion = Motion()
        new_motion.pos = motion.pos.add_scaled(motion.velocity, time)
        new_motion.phi = motion.phi + motion.omega * time
        new_motion.velocity = motion.velocity
        new_motion.omega = motion.omega
        return new_motion

    def bounce(self, motion, normal):
        """отскок"""
        new_motion = Motion()
        new_motion.pos = motion.pos
        new_motion.velocity = motion.velocity.diff(normal.scale(2.0*normal.scalar(motion.velocity)))
        new_motion.phi = motion.phi
        new_motion.omega = motion.omega
        return new_motion

    def make_step(self, time):
        time_left = time
        motion = self.ball.motion
        while time_left > 0:
            new_motion = self.update_motion(motion, time_left)
            near_time = time_left
            list_of_fired_obstacles = []

            for obstacle in self.obstacles:
                fired, motion, part, normal = obstacle.check(self.ball.size, self.ball.motion, new_motion)
                if fired:
                    fired_obstacle = FiredObstacle(motion, part, normal)
                    """сработало препятствие"""
                    print("#"+str(obstacle.obstacle_id))
                    new_near_time = time * part
                    if 0 < new_near_time < near_time:
                        """новое более раннее препятствие"""
                        list_of_fired_obstacles = [fired_obstacle]
                        near_time = new_near_time
                    elif 0 < new_near_time == near_time:
                        """добавляем препятствие в список препятствий"""
                        list_of_fired_obstacles.append(fired_obstacle)

            if len(list_of_fired_obstacles) > 0:
                """если несколько препятствий вычисляем среднюю нормаль"""
                new_normal = Point2D(0.0, 0.0)
                new_point = Point2D(0.0, 0.0)
                for obstacle in list_of_fired_obstacles:
                    new_normal = new_normal.add(obstacle.normal)
                    new_point = new_point.add(obstacle.motion.pos)
                new_normal = new_normal.normalize()
                new_point = new_point.scale(1.0/len(list_of_fired_obstacles))
                new_motion = list_of_fired_obstacles[0].motion
                new_motion.pos = new_point
                new_motion = self.bounce(new_motion, new_normal)
                time_left = time_left - near_time
            else:
                time_left = 0
            motion = new_motion
        self.ball.set_motion(motion)
    pass


class Score:
    def __init__(self, ):
        pass

    def clear(self):
        pass


class PongApplication:
    def __init__(self, window):
        self.master = window
        self.master.geometry('640x480+300+300')
        self.master.title('PONG')
        self.canvas = tkinter.Canvas(self.master, width=500, height=480)
        self.canvas.pack()

        self.field = GameField()
        point00 = Point2D(0.0, 0.0)
        point01 = Point2D(400.0, 0.0)
        point10 = Point2D(0.0, 200.0)
        point11 = Point2D(400.0, 200.0)

        point200 = Point2D(100.0, 100.0)
        point201 = Point2D(150.0, 100.0)
        point210 = Point2D(100.0, 150.0)
        point211 = Point2D(150.0, 150.0)

        point300 = Point2D(200.0, 50.0)
        point301 = Point2D(250.0, 50.0)
        point310 = Point2D(200.0, 100.0)
        point311 = Point2D(250.0, 100.0)

        plane1 = Plane2D(point00, Point2D(0.0, 1.0))
        plane2 = Plane2D(point00, Point2D(1.0, 0.0))
        plane3 = Plane2D(point10, Point2D(0.0, -1.0))
        plane4 = Plane2D(point01, Point2D(-1.0, 0.0))

        plane21 = Plane2D(point200, Point2D(0.0, -1.0))
        plane22 = Plane2D(point200, Point2D(-1.0, 0.0))
        plane23 = Plane2D(point210, Point2D(0.0, 1.0))
        plane24 = Plane2D(point201, Point2D(1.0, 0.0))

        plane31 = Plane2D(point300, Point2D(0.0, -1.0))
        plane32 = Plane2D(point300, Point2D(-1.0, 0.0))
        plane33 = Plane2D(point310, Point2D(0.0, 1.0))
        plane34 = Plane2D(point301, Point2D(1.0, 0.0))

        self.field.add_obstacle(Linear2DObstacle(1, plane1, point00, point01))
        self.field.add_obstacle(Linear2DObstacle(2, plane2, point00, point10))
        self.field.add_obstacle(Linear2DObstacle(3, plane3, point10, point11))
        self.field.add_obstacle(Linear2DObstacle(4, plane4, point01, point11))

        """
        self.field.add_obstacle(Linear2DObstacle(5, plane21, point200, point201))
        self.field.add_obstacle(Linear2DObstacle(6, plane22, point200, point210))
        """

        self.field.add_obstacle(Linear2DObstacle(7, plane23, point210, point211))
        self.field.add_obstacle(Linear2DObstacle(8, plane24, point201, point211))

        """
        self.field.add_obstacle(Linear2DObstacle(9, plane31, point300, point301))
        self.field.add_obstacle(Linear2DObstacle(10, plane32, point300, point310))
        self.field.add_obstacle(Linear2DObstacle(11, plane33, point310, point311))
        self.field.add_obstacle(Linear2DObstacle(12, plane34, point301, point311))
        """

        """
        self.field.add_obstacle(Linear2DObstacle(plane4, point01, point11))
        self.field.add_obstacle(Linear2DObstacle(plane3, point10, point11))
        """

        self.ball = Ball()
        self.ballphy = BallPhysics(self.ball, self.field.obstacle_list)

        self.img = Image.open(r'resources/ball.png').resize((self.ball.size, self.ball.size), Image.ANTIALIAS)

        self.pimg = ImageTk.PhotoImage(image=self.img)
        """
        self.canvas.create_line(0, 0, 100, 100)
        self.canvas.create_image((100, 100), image=self.pimg)
        self.canvas.update()"""
        self.draw_field()
        self.master.after(25, lambda : self.move())


    def move(self):
        self.ballphy.make_step(50)
        self.draw_field()
        self.master.after(25, lambda: self.move())

    def workflow(self):
        pass
        """self.window.after(1000, self.move)"""

    def draw_field(self):
        self.canvas.create_line(0, 0, 100, 100)
        self.canvas.create_rectangle(0, 0, 400, 200, fill="#DDD")
        self.canvas.create_rectangle(100, 100, 150, 150, fill="#222")
        self.canvas.create_rectangle(200, 50, 250, 100, fill="#222")
        self.pimg = ImageTk.PhotoImage(image=self.img.rotate(self.ball.motion.phi))
        """
        self.pimg = ImageTk.PhotoImage(image=self.img)
        """
        self.canvas.create_image((self.ball.motion.pos.x - self.ball.size / 2, self.ball.motion.pos.y - self.ball.size / 2), image=self.pimg, anchor='nw')
        self.canvas.update()
        pass


root = tkinter.Tk()
application = PongApplication(root)
root.mainloop()