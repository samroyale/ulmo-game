# Ulmo's Adventure
###A game implemented in Python/Pygame for the Raspberry Pi

Help Ulmo evade enemies, collect coins and find his way to the end of an amazing (but short) adventure. Use cursor keys to move, space to do stuff, X to toggle sound and ESC to quit.

16-bit style graphics, a top-down perspective and tile-based maps - a retro style RPG much like the old SNES classics.  Also features some pseudo-3D elements, eg. the ability to move underneath bridges, etc.

Graphics were created in Gimp, sounds in CFXR and soundtrack in Pxtone. The game itself is implemented in Python/Pygame and the map editor is in Java SWT.

Pi Store: http://store.raspberrypi.com/projects/ulmos-adventure

Pygame: http://pygame.org/project-Ulmo%27s+Adventure-2042-4658.html

![Screen grab](http://i.imgur.com/nHshMfb.png)

Rasberry Pi Users
> Should run out of the box on any recent Raspbian distribution

Other Platforms
> Will need to have Python + Pygame installed (my current dev platform is OSX with Python 2.7.8 + Pygame 1.9.1)

To run it:
```
$ ./run.sh
```

To build it (this will create *ulmo-game-1.1.tar.gz* under *src/dist*):
```
$ ./build.sh
```

