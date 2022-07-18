import tkinter
from PIL import Image,  ImageTk

class KeyTracker:
    pass


class Field:

    pass


class Obstacle:
    def check(self):
        """признак нарушения, время и точку нарушения"""
        pass
    pass




class Ball:
    def __init__(self):
        self.visible = 0.0
        self.radius = 10.0
        self.motion = Motion()

    def set_position(self, position):
        pass

class Motion:
    def __init__(self):
        self.posX = 0.0
        self.posY = 0.0
        self.phi = 0.0

        self.velocityX = 0.0
        self.velocityY = 0.0
        self.omega = 0.1
        pass


class BallPhy:
    def __init__(self, ball):
        self.ball = ball
    def update_motion(self, time):
        """движение"""
        new_motion = Motion()
        new_motion.posX = self.ball.motion.posX + self.ball.motion.velocityX * time
        new_motion.posY = self.ball.motion.posY + self.ball.motion.velocityY * time
        new_motion.phi = self.ball.motion.phi + self.ball.motion.omega * time
        new_motion.velocityX = self.ball.motion.velocityX
        new_motion.velocityY = self.ball.motion.velocityY
        new_motion.omega = self.ball.motion.omega
        return new_motion

    def bounce(self, motion):
        """отскок"""
        new_motion = motion
        return new_motion

    def make_step(self, time):
        new_motion = self.update_motion(time)
        """пока без проверки"""
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
        self.canvas = tkinter.Canvas(self.master, width=400, height=400)
        self.canvas.pack()
        self.ballphy = BallPhy(Ball())
        self.img = Image.open(r'resources/ball.png').resize((50, 50), Image.ANTIALIAS)
        self.master.after(1000, lambda : self.move())

    def move(self):
        self.ballphy.make_step(1)

    def workflow(self):
        self.window.after(1000, self.move)

    def draw_field(self):
        self.canvas.create_line(0, 0, 100, 100)

        pimg = ImageTk.PhotoImage(image=self.img.rotate())
        self.canvas.create_image((0, 0), image=pimg, anchor='nw')
        self.canvas.update()
        pass


root = tkinter.Tk()
application = PongApplication(root)
root.mainloop()