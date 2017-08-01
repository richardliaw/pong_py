class Paddle():
    STOP = 0
    UP = 1
    DOWN = 2


    def __init__(self, rhs, pong):
        self.pid = rhs
        self.width = 12
        self.height = 60
        self.dt = pong.dt
        self.minY = pong.wall_width
        self.maxY = pong.height - pong.wall_width - self.height
        self.speed = (self.maxX - self.minX) /2
        self.ai_reaction = 1.0
        self.ai_error = 120
        self.set_direction(0)
        self.set_position(pong.width - self.width if rhs else 0, 
                          self.minY + (self.maxY - self.minY) / 2)
        self.prediction = None

    def set_position(self, x, y):
        self.x      = x
        self.y      = y
        self.left   = self.x
        self.right  = self.left + self.width
        self.top    = self.y
        self.bottom = self.y + self.height

    def set_direction(self, dy):
        # Needed for spin calculation
        self.up = -dy if dy < 0 else 0
        self.down = dy if dy > 0 else 0

    def step(self, action):
        if action == self.STOP:
            self.stopMovingDown()
            self.stopMovingUp()
        elif action == self.DOWN:
            self.moveDown()
        elif action == self.UP:
            self.moveUp()
        amt = self.down - self.up
        if amt != 0:
            y = self.y + (amt * self.dt * self.speed)
        if y < self.minY:
            y = self.minY
        elif y > self.maxY:
            y = self.maxY
        self.set_position(self.x, y)

    def predict(self, ball, dt):
        # only re-predict if the ball changed direction, or its been some amount of time since last prediction
        if (self.prediction and ((self.prediction.dx * ball.dx) > 0) and
                ((self.prediction.dy * ball.dy) > 0) and 
                (self.prediction.since < self.aiReaction)):
            self.prediction.since += dt
            return

        rect = Rectangle(self.left, self.right, -10000, 10000)
        pt = helper.ballIntercept(ball, rect, ball.dx * 10, ball.dy * 10)

        if (pt):
            t = self.minY + ball.radius
            b = self.maxY + self.height - ball.radius

            while ((pt.y < t) or (pt.y > b)):
                if (pt.y < t):
                    pt.y = t + (t - pt.y)
                elif (pt.y > b):
                    pt.y = t + (b - t) - (pt.y - b)
            self.prediction = pt
        else:
            self.prediction = None

        if self.prediction:
            self.prediction.since = 0
            self.prediction.dx = ball.dx
            self.prediction.dy = ball.dy
            self.prediction.radius = ball.radius
            self.prediction.exactX = self.prediction.x
            self.prediction.exactY = self.prediction.y
            closeness = (ball.x - self.right if ball.dx < 0 else self.left - ball.x) / self.pong.width
            error = self.ai_error * closeness
            self.prediction.y = self.prediction.y + Game.random(-error, error)

    def ai_step(self, ball):
        if (((ball.x < self.left) and (ball.dx < 0)) or
           ((ball.x > self.right) and (ball.dx > 0))):
            self.stopMovingUp()
            self.stopMovingDown()
            return

        self.predict(ball, self.dt)

        if (self.prediction):
            if (self.prediction.y < (self.top + self.height/2 - 5)):
                self.stopMovingDown()
                self.moveUp()
            elif (self.prediction.y > (self.bottom - self.height/2 + 5)):
                self.stopMovingUp()
                self.moveDown()
            else:
                self.stopMovingUp()
                self.stopMovingDown()

    def moveUp(self):
        self.down = 0
        self.up = 1

    def moveDown(self):
        self.down = 1
        self.up = 0

    def stopMovingDown(self):
        self.down = 0

    def stopMovingUp(self):
        self.up = 0