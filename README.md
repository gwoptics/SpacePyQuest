# Space-Py Quest 0.1.0

Space-Py Quest is a gravitational wave interferometer parameter optimisation game, written in Python and run in a Jupyter notebook. 
It is based on the original game Space-Time Quest, available as apps for iOS, Android, Windows, Linux and MacOs
at <a href="https://www.laserlabs.org/spacetimequest.php">https://www.laserlabs.org/spacetimequest.php</a>. Both games can be used for teaching and public engagement. The apps are easy to use and provide a playful way to introduce detector design and technology. This Python version allows students to look into the underlying noie models.

## Getting Started

Space-Py Quest is played from a Jupyter notebook that consists of a single plot displaying multiple noise curves, which can be altered by modifying the detector's physical properties. A drop-down menu provides access to controls for the interferometer's variable parameters. Additional controls are available for adjusting the limits of the x- and y-axes, and for adding and removing individual noise curves from the total calculation. 

The Science Run option tool is a button, which returns the 'Score': the complexity and cost of the instrument; the number of sources of supernova, Black Hole (BH) binaries and Neutron Star (NS) binaries seen; the range to which the detector can sense NS and BH mergers; and the weighted total observation range of the detector.

### Prerequisites

Space-Py Quest should be run with Python versions at or above 3.5.4, and with the Bokeh package at version 0.12.9. 

### Installing

There are many ways to install the required software packages and Space-Py Quest. Experienced Python users can download the files from the repository and start the Jupyter notebook [SpacePyQuest.ipynb](SpacePyQuest.ipynb).

Below we provide some suggestions for installing the required Python packages for less experienced users. From years of experience on working with diverse groups of people, for example, such as during summer schools, we recommend the use of [Anacoda distribution](https://www.anaconda.com/) which is cross platform, well documented and provides an easy to install and well managed Python environment.

#### Example 1: I do not have Anaconda
(If this does not apply to you, skip to [Example 2](Example 2: I do not have Jupyter)
Download either Miniconda or the full Anaconda package. Miniconda is quicker to install and perfectly adequate for the purposes of Space-Py Quest, while Anaconda would be more useful if you will use Python for other purposes as well. To download and install Miniconda with Python, instructions are available here: [https://conda.io/miniconda.html]. 
Ensure that you are installing Python versions at or above 3.5.4.

See the [Anaconda user guide](https://conda.io/docs/user-guide/install/download.html) for more advice on chosing between Anaconda and Miniconda.

#### Example 2: I do not have Jupyter
Open an Anaconda or Miniconda terminal. 
You can check that you are running a Python version at or above 3.5.4. by typing ```python --version```. If you are not, run ```conda update python``` first.
Run the command ```conda install jupyter``` to install Jupyter. You will need to confirm the install by pressing 'y' when prompted.

#### Example 3: I do not have Bokeh
Bokeh is an interactive graphics library for Python. To install this, open a command window and run ```conda install bokeh=0.12.9```. (Note that there are subtle differences between different versions of Bokeh and Space-Py Quest might only work correctly with Bokey 0.12.9.

#### Example 4: I have all aforementioned packages
Great! Open a command window and navigate to the SpacePyQuest folder. Run the command ```jupyter notebook SpacePyQuest.ipynb```.

## Authors

This project was created by Philip Jones and Isobel Romero-Shaw, with support from Roshni Vincent and Andreas Freise. The code has been generated from the original game Space Time Quest with permission.

## License

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License version 3 as published by the Free Software Foundation.

This project is licensed under the MIT License - see the [gpl-3.0.md](gpl-3.0.md) file for details

