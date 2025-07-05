from miniworldmaker import App, Circle, Token, Line
from miniworldmaker_physics import PhysicsBoard
from .screenshot_tester import ScreenshotTester
import unittest
import os
import random


class Test405(unittest.TestCase):

    def setUp(self):
        def test_code():
            board = PhysicsBoard((400, 200))
            # Here comes your code
            @board.register
            def setup_environment(self, test):
                anchors = []
                circles = []

                def add_line(obj1, obj2):
                    l = Line(obj1.center, obj2.center)
                    l.physics.simulation = None
                    l.border = 1
                    @l.register
                    def act(self):
                        self.start_position = obj1.center
                        self.end_position = obj2.center
                        
                for i in range(5):
                    anchor = Token()
                    anchor.size = (20,20)
                    anchor.center = (i*50+50, 50)
                    anchor.physics.simulation = "manual"
                    anchors.append(anchor)
                    
                    c = Circle((0,0),10)
                    circles.append(c)
                    if i==0:
                        c.center = (-50, 25)
                        print("setup anchor:", anchor.center, anchor.local_center, anchor.topleft)
                        print("setup circle:", c.center, c.local_center, c.topleft)
                    else:
                        c.center = anchor.center
                        print("setup anchor:", anchor.center, anchor.local_center, anchor.topleft)
                        print("setup circle:", c.center, c.local_center, c.topleft)
                        c.y += 100
                    c.physics.simulation = "simulated"
                    anchor.physics.join(c)
                    add_line(anchor, c)
            return board
        App.reset(unittest=True, file=__file__)
        board = test_code()
        """ Setup screenshot tester"""
        TEST_FRAMES = [1,10,20,30,40,60,80,100,120]
        QUIT_FRAME = 121
        tester = ScreenshotTester(TEST_FRAMES, QUIT_FRAME, self)
        tester.setup(board)
        if hasattr(board, "setup_environment"):
            board.setup_environment(self)



        return board

    def test_main(self):
        with self.assertRaises(SystemExit):
            self.board.run()


if __name__ == "__main__":
    unittest.main()