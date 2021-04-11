# manim-projects
Code for the animations made with **Manim** for my YouTube channel **[PRAGYAAN](https://www.youtube.com/channel/UCrmef-kSIRH8SzCLa89l_xA)** and in general, for fun. 

## Manim versions
There are two main versions of **Manim** that I'm aware of which I use for my projects :
- [Manim Community](https://www.manim.community/) (manim)
- [3b1b/manim](https://github.com/3b1b/manim) (manimgl)

If the project has computationally intensive `Scene`s (usually `ThreeDScene`s), I prefer **manimgl** since it has **OpenGL rendering** and allows **GPU acceleration**. **Manim Community** has _experimental_ OpenGL rendering support as of this commit, which for sure keeps evolving (thanks to the devs and contributors!). You can identify the version I used for a project with the import statement:
```py
from manim import *  # made with Manim Community
from manimlib import *  # made with 3b1b/manim
```
I'd recommend getting started with **Manim Community** since the code is a lot _cleaner_ with good documentation, there is active development and help, it is relatively more user, developer friendly, and it is **continuously growing**.
### NOTE
Almost all the projects made upto this commit use **3b1b/manim**. Since this version has evolved a lot from the time I began my projects, some parts of code _may_ not work / need some modifications to work. You might find some hard-coded values here and there, and just _bad_ python practices, but I think that's okay :) Code for the videos I upload to **[PRAGYAAN](https://www.youtube.com/channel/UCrmef-kSIRH8SzCLa89l_xA)** are in the `pragyaan\` directory 

## LICENSE
This repository is mainly intended to update and keep track of my personal projects made with Manim. It is made public in the hope that someone might find it useful while learning Manim. All the code is only meant as a reference and not for reuse without permission. 
