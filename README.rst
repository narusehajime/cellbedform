CELLBEDFORM
========================

This is a code for a simple cell model simulation of self-organized bedform. The model is based on Nishimori and Ouchi (1993). 

---------------
Installation

python setup.py install

---------------
Test codes

python setup.py test

---------------
Usage

After installation, use the following commands.

> from cellbedform import CellBedform
> cb = CellBedform(grid=(100,100))
> cb.run(steps=150)
> cb.save_images('bedform')

This will save calculation results as an image sequence. Instead,
to show the final result,

> cb.show()

The following command will produce the animation movie using ffmpeg or
imagemagick. However, this is not recommended because it is extremely slow.
Other softwares such as virtualDub can produce a movie file from
the image sequence, and thus recommended.

> cb.animation(filename='bedform.gif', format='gif')




