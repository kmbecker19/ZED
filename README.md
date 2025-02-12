# ZED Camera Interface

This program is a GUI interface for operating the ZED depth camera. It will allow you to:

- View the camera feed (both RGB and Depth) from the ZED camera.
- Save the RGB and Depth images to a specified directory.
- Adjust the parameters of the ZED camera.

## Getting Started

- Make sure to download the latest version of the ZED SDK on [stereolabs.com](https://www.stereolabs.com/).

### Requirements

- Python>=3.8
- CUDA>=11.1
- Numpy
- Cython
- OpenCV
- OpenGL

### Using Conda

- First, make a conda environment for the program using the following command:

```bash
conda create -n zed-gui python=3.8 pip numpy cython opencv pyopengl pyside6 requests -c conda-forge
```

- Next, make sure to download the ZED SDK on [stereolabs.com](https://www.stereolabs.com/). Follow instructions for downloading the Python API.

> If you're using a conda environment, make sure to activate it **before** installing the ZED Python API!

### Using Pip

- First, install the necessary requirements for the application using pip:

```bash
pip install numpy cython opencv-python pyopengl pyside6 requests
```

- Next, make sure to download the ZED SDK on [stereolabs.com](https://www.stereolabs.com/). Follow instructions for downloading the Python API.

## Using the Interface

![ZED_GUI_diagram](https://github.com/user-attachments/assets/9e25e511-51ca-4835-8242-8d790cbd852b)

### Components

The interface has the following components:

1. **Settings**: For changing the camera initialization parameters and runtime parameters.
2. **Folder Field**: For choosing the subject folder to save the images into.
3. **Name Field**: For entering the name of the current image.
4. **Counter Field**: For incrementing, decrementing, or resetting the image counter.
5. **Display Format Field**: Choose the format for the camera feed display. Choose between:
    - **RGB**: Color camera video feed.
    - **Depth**: Depth camera video feed.
    - **Sobel**: Gradient-filtered depth camera video feed using OpenCV's `sobel` filter.
6. **Sobel Power Field**: For changing the power of the sobel gradient filter, which impacts display output. Choose lower numbers (<0.5) for topography-style gradient lines.
7. **Display**: The main display for the camera feed.
8. **Save Image and Depth Map**: Capture the image from the camera feed, both RGB and depth, and save along with metadata. To capture an image, either click here or press the Enter key.

### Image Capture

To capture an image, perform the following steps:

1. **Choose a Subject folder using the "Choose..." button.** This will determine the folder that the image gets saved into, as well as the naming of the image.
2. **Enter an Image name into the "Name" field.** This should be something like "shirt_vest" or "shirt_neg" that identifies what condition the image is being taken under.
3. **Ensure the counter is at the correct value.** Click the "Reset" button to reset the counter to 1 for each new imaging condition.
4. **Change Camera settings if desired.** The camera settings should remain consistent across sessions, but can be altered in certain circumstances.
5. **Press "Save Image and Depth Map" to capture images.** This will save the images into the subject folder and give you a pop-up confirming that the images have been succesfully saved. You can also capture an image at any time by pressing the **Enter** key.

Each image will be saved with the naming format `<SUBJECT>_<NAME>_<COUNTER>`.
When you capture an image using this program, the following files will be saved into
your subject folder:

- **2 PNG Files** containing the RGB image and visualized Depth camera image.
- **2 Numpy Files** Containing the raw data for the depth image and 3D point-cloud map.
- **2 Metadata Files** in text and JSON format containing the name, resolution,
description, and timestamp of the image, along with the camera settings and runtime
parameters.


### Parameters Tested

In our tests, we used the following parameters:

- **Camera**
- - *Resolution*: 2K
- - *FPS*: 15
- - *Depth Mode*: Ultra
- - *Coordinate Units*: Millimeters
- - *Min. Distance*: 2010
- - *Max. Distance*: 2520
- **Video**
- - *Brightness*: 4
- - *Contrast*: 4
- - *Hue*: 0
- - *Saturation*: 4
- - *Sharpness*: 4
- - *Gamma**: 5
- - *White Balance*: 4700
- - *Gain*: 97
- - *Exposure*: 91
- **Runtime**
- - *Fill*: FALSE
- - *Confidence Threshold*: 100
- - *Texture Threshold*: 100
- **Room Parameters**
- - Lights on and dimmed


