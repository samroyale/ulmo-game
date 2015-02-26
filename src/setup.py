#!/usr/bin/env python

from distutils.core import setup

setup(name = "ulmo-game",
      version = "1.1",
      py_modules=["play"],
      packages=["rpg"],
      author="Sam Eldred",
      author_email="samuel.eldred@gmail.com",
      url="https://github.com/samroyale/ulmo-game",
      license="GNU GPL v3",
      description="A game implemented in python/pygame for the Raspberry Pi",
      long_description="""16-bit style graphics, a top-down perspective and tile-based maps - a
          retro style RPG much like the old SNES classics. Also features some pseudo-3D elements,
          eg. the ability to move underneath bridges, etc.""",
      platforms="Python source code"
)
