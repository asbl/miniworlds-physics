from miniworlds import App, Circle
from miniworlds_physics import PhysicsBoard
from .screenshot_tester import ScreenshotTester
import unittest

class Test411(unittest.TestCase):

    def setUp(self):
        def test_code():
            world = PhysicsBoard((800, 600))
            # Here comes your code
            @world.register
            def setup_environment(self, test):
                world.gravity = (0, 0)

                a = Circle()
                a.position = (75, 200)
                a.color = (255,0,0)
                a.impulse(90, 500)

                b = Circle()
                b.position = (275, 200)
                b.color = (255,0,0)
                b.impulse(-90, 500)

                @a.register
                def on_separation_from_circle(self, other, info):
                    self.color = (0,255,0)
                    print("OUTCH (a)!!!", self)
                    other.border_color = (255,0,255)
                    
                @b.register
                def on_separation_from_circle(self, other, info):
                    self.color = (100,100,255)
                    other.border_color = (255,255,255)
            return world
        App.reset(unittest=True, file=__file__)
        world = test_code()
        """ Setup screenshot tester"""
        TEST_FRAMES = [1,3,6,9,12,20,40,60]
        QUIT_FRAME = 60
        tester = ScreenshotTester(TEST_FRAMES, QUIT_FRAME, self)
        tester.setup(board)
        if hasattr(board, "setup_environment"):
            world.setup_environment(self)



        return board

    def test_main(self):
        with self.assertRaises(SystemExit):
            self.world.run()


if __name__ == "__main__":
    unittest.main()