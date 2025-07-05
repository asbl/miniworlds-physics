from miniworldmaker import App, Line
from miniworldmaker_physics import PhysicsBoard
from .screenshot_tester import ScreenshotTester
import unittest
import os
import random


class Test718(unittest.TestCase):

    def setUp(self):
        def test_code():
            board = PhysicsBoard(400, 400)

            # Here comes your code
            @board.register
            def setup_environment(self, test):
                for i in range(9):
                    l = Line((i * 40, 20 + i * 10), ((i + 1) * 40, 20 + i * 10))
                    l.thickness = i

                for i in range(9):
                    l = Line((i * 40, 80 + i * 10), ((i + 1) * 40, 120 + i * 10))
                    l.thickness = i

                for i in range(9):
                    l = Line((i * 40, 160 + i * 10), ((i + 1) * 40, 160 + i * 10))
                    l.thickness = i
                    l.direction = 135

                for i in range(18):
                    l = Line((300, 300), (350, 350))
                    l.direction = i * 20
                    l.border_color = (i * 10, i * 10, i * 10)

                l = Line((100, 300), (150, 300))

                @l.register
                def act(self):
                    l.direction += 1

            board.debug = True
            return board

        App.reset(unittest=True, file=__file__)
        board = test_code()
        """ Setup screenshot tester"""
        TEST_FRAMES = [1, 3, 6, 9, 12, 20, 40, 60]
        QUIT_FRAME = 60
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
