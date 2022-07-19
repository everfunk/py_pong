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
    def __init__(self, plane, point1, point2):
        super().__init__()
        self.plane = plane
        self.point1 = point1
        self.point2 = point2
        pass

    def check(self, motion1, motion2):
        """
        по двум точкам движения и времени между ними
        возвращает признак нарушения, время и точку нарушения
        """
        val1 = self.plane.apply(motion1.pos)
        val2 = self.plane.apply(motion2.pos)
        if val1 >= 0 and val2 > 0:
            """обе точки с одной стороны ограничения"""
            return False, motion2, 0, self.plane.normal
        else:
            """при движении пересечено ограничение"""
            """TODO доля"""
            print(val1, val2)
            part = val1 / (val1 - val2)
            new_motion = Motion()
            new_motion.velocity = motion1.velocity
            new_motion.pos = motion1.pos.add(motion2.pos.diff(motion1.pos).scale(part))
            new_motion.phi = motion1.phi
            new_motion.omega = motion1.omega
            return True, new_motion, part, self.plane.normal
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

    def set_motion(self, m):
        self.motion = m
        pass


class Motion:
    def __init__(self):
        self.pos = Point2D(0.0, 0.0)
        self.phi = 0.0

        self.velocity = Point2D(0.13, 0.17)
        self.omega = 0.1
        pass


class BallPhysics:
    def __init__(self, ball, obstacles):
        self.ball = ball
        """список препятствий"""
        self.obstacles = obstacles

    def update_motion(self, time):
        """движение"""
        new_motion = Motion()
        new_motion.pos = self.ball.motion.pos.add_scaled(self.ball.motion.velocity, time)
        new_motion.phi = self.ball.motion.phi + self.ball.motion.omega * time
        new_motion.velocity = self.ball.motion.velocity
        new_motion.omega = self.ball.motion.omega
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
        while time_left > 0:
            new_motion = self.update_motion(time)
            got_obstacle = False
            near_time = time
            near_point = new_motion.pos
            near_normal = Point2D(0.0, 0.0)

            for obstacle in self.obstacles:
                fired, point, part, normal = obstacle.check(self.ball.motion, new_motion)
                if fired:
                    """сработало препятствие"""
                    new_near_time = time * part
                    if new_near_time <= near_time:
                        got_obstacle = True
                        near_time = new_near_time
                        near_point = point
                        near_normal = normal
                else:
                    time_left = 0
            if got_obstacle:
                new_motion = self.bounce(near_point, near_normal)
                time_left = time_left - near_time
        self.ball.set_motion(new_motion)
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

        plane1 = Plane2D(point00, Point2D(0.0, 1.0))
        plane2 = Plane2D(point00, Point2D(1.0, 0.0))
        plane3 = Plane2D(point10, Point2D(0.0, -1.0))
        plane4 = Plane2D(point01, Point2D(-1.0, 0.0))


        self.field.add_obstacle(Linear2DObstacle(plane1, point00, point01))
        self.field.add_obstacle(Linear2DObstacle(plane2, point00, point10))
        self.field.add_obstacle(Linear2DObstacle(plane3, point10, point11))        
        self.field.add_obstacle(Linear2DObstacle(plane4, point01, point11))       


        """
        self.field.add_obstacle(Linear2DObstacle(plane4, point01, point11))
        self.field.add_obstacle(Linear2DObstacle(plane3, point10, point11))
        """

        self.ball = Ball()
        self.ballphy = BallPhysics(self.ball, self.field.obstacle_list)

        self.img = Image.open(r'resources/ball.png').resize((40, 40), Image.ANTIALIAS)

        self.pimg = ImageTk.PhotoImage(image=self.img)
        """
        self.canvas.create_line(0, 0, 100, 100)
        self.canvas.create_image((100, 100), image=self.pimg)
        self.canvas.update()"""
        self.draw_field()
        self.master.after(50, lambda : self.move())


    def move(self):
        self.ballphy.make_step(100)
        self.draw_field()
        self.master.after(25, lambda: self.move())

    def workflow(self):
        pass
        """self.window.after(1000, self.move)"""

    def draw_field(self):
        self.canvas.create_line(0, 0, 100, 100)

        self.pimg = ImageTk.PhotoImage(image=self.img.rotate(self.ball.motion.phi))
        """
        self.pimg = ImageTk.PhotoImage(image=self.img)
        """
        self.canvas.create_image((self.ball.motion.pos.x, self.ball.motion.pos.y), image=self.pimg, anchor='nw')
        self.canvas.update()
        pass


root = tkinter.Tk()
application = PongApplication(root)
root.mainloop()