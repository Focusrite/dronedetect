# dronedetect
Summer job project to detect and track drones using computer vision. This README describes how to set the project up
for development.

## Prerequisites

* Anaconda (miniconda)
* Numpy
* Basler pylon drivers. Note that these are not installed from anaconda.
* Pypylon library, for easy interfacing with the pylon driver (requires SWIG).
* OpenCV and OpenCV-contrib as a good place to start with algorithms.
* pip and python pre-installed if not install them first

Optional but good to have
* Scipy

For the calibration script
* docopt

# Detailed instructions

Once miniconda is installed run;
`conda create -n "Sommarjobb" python="3"`
to create an environment. Run
`conda activate Sommarjobb`
to launch the environment.

Install necessary libraries;
`pip install numpy`
`pip install scipy`
`pip install opencv-python`
`pip install opencv-contrib-python`
`conda install -c anaconda swig`
`conda update swig`
`pip install docopt==0.6.2`

Download and install the Basler pylon drivers.
To install pypylon, first export PYLON_ROOT="/PATH/TO/PYLON" then run pip install in pypylon
the folder where it was cloned. E.g.
`export PYLON_ROOT="/home/user/sommarjobb/pylon/pylon5"`

To then install pypylon do;
`git clone https://github.com/basler/pypylon.git`
`cd pypylon`
`pip install .`

All done! To run, do
`python cap.py` 
