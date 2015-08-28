from unittest import TestCase

from agarnet.vec import Vec
from agarnet.world import Cell, Player, World


screen = Vec(1920, 1080)
zero = Vec(0, 0)


class WindowMock:
    def __init__(self, tl=Vec(-10, 10), br=Vec(-10, 10)):
        self.tl = tl
        self.br = br
        self.world_center = (br + tl) / 2
        self.screen_center = screen / 2
        self.screen_scale = 1

    # taken from gagar, same as in official client
    def screen_to_world_pos(self, screen_pos):
        return (screen_pos - self.screen_center) \
            .idiv(self.screen_scale).iadd(self.world_center)


class CellTest(TestCase):
    def test_lt(self):
        self.assertLess(Cell(1), Cell(2))
        self.assertLess(Cell(2, size=10), Cell(1, size=11))


class WorldTest(TestCase):
    def test_world(self):
        World()  # TODO WorldTest


class PlayerTest(TestCase):
    def test_visible_area(self):
        player = Player()

        # simple test

        win = WindowMock()

        player.scale = win.screen_scale
        player.world.top_left = win.tl
        player.world.bottom_right = win.br

        ptl, pbr = player.visible_area

        rtl = win.screen_to_world_pos(zero)
        rbr = win.screen_to_world_pos(screen)

        self.assertAlmostEqual(ptl.x, rtl.x)
        self.assertAlmostEqual(ptl.y, rtl.y)
        self.assertAlmostEqual(pbr.x, rbr.x)
        self.assertAlmostEqual(pbr.y, rbr.y)

        # complex test

        win = WindowMock(Vec(123, 234), Vec(-34.5, 45.6))

        player.scale = win.screen_scale = 2.3
        player.world.top_left = win.tl
        player.world.bottom_right = win.br

        ptl, pbr = player.visible_area

        rtl = win.screen_to_world_pos(zero)
        rbr = win.screen_to_world_pos(screen)

        self.assertAlmostEqual(ptl.x, rtl.x)
        self.assertAlmostEqual(ptl.y, rtl.y)
        self.assertAlmostEqual(pbr.x, rbr.x)
        self.assertAlmostEqual(pbr.y, rbr.y)
