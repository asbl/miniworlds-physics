from miniworlds import App, Circle, Rectangle, Line
from miniworlds_physics import PhysicsWorld
from screenshot_tester import ScreenshotTester
import unittest


class Test405(unittest.TestCase):

    def setUp(self):
        def test_code():
            world = PhysicsWorld(400, 200)

            @world.register
            def setup_environment(self, test):
                def add_line(obj1, obj2):
                    l = Line(obj1.center, obj2.center)
                    l.physics.simulation = None
                    l.border = 1

                    @l.register
                    def act(self):
                        self.start_position = obj1.center
                        self.end_position = obj2.center

                for i in range(5):
                    anchor = Rectangle((0, 0), 20, 20)
                    anchor.center = (i * 50 + 50, 50)
                    anchor.physics.simulation = "manual"
                    c = Circle((0, 0), 10)
                    if i == 0:
                        c.center = (-50, 25)
                    else:
                        c.center = anchor.center
                        c.y += 100
                    c.physics.simulation = "simulated"
                    anchor.physics.join(c)
                    add_line(anchor, c)

            return world

        App.reset(unittest=True, file=__file__)
        world = test_code()
        TEST_FRAMES = [1, 10, 20, 30, 40, 60, 80, 100, 120]
        QUIT_FRAME = 121
        tester = ScreenshotTester(TEST_FRAMES, QUIT_FRAME, self)
        tester.setup(world)
        if hasattr(world, "setup_environment"):
            world.setup_environment(self)

    def test_main(self):
        with self.assertRaises(SystemExit):
            self.world.run()


if __name__ == "__main__":
    unittest.main()