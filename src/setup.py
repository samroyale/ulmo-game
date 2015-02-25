#!/usr/bin/env python

from distutils.core import setup

setup(name = "rpg-world",
      version = "1.0",
      py_modules=["play"],
      packages=["rpg"],
      author="Sam Eldred",
      author_email="samuel.eldred@gmail.com",
      url="http://code.google.com/p/rpg-world/",
      license="GNU GPL v3",
      description="Game/game engine written in Python/Pygame",
      long_description="""16-bit style graphics, a top-down perspective and tile-based maps - a
          retro style RPG much like the old SNES classics. Also features some pseudo-3D elements,
          eg. the ability to move underneath bridges, etc.""",
      platforms="Python source code"
)
