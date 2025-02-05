# ZED Camera Interface

This program is a GUI interface for operating the ZED depth camera. It will allow you to:

- View the camera feed (both RGB and Depth) from the ZED camera.
- Save the RGB and Depth images to a specified directory.
- Adjust the parameters of the ZED camera.

## Getting Started

- Make sure to download the latest version of the ZED SDK on [stereolabs.com](https://www.stereolabs.com/).

### Using Conda

- First, make a conda environment for the program using the following command:

`conda create -n zed-gui python=3.8 pip numpy cython opencv pyopengl pyside6 requests -c conda-forge`

- Next, make sure to download the ZED SDK on [stereolabs.com](https://www.stereolabs.com/). Follow instructions for downloading the Python API.

> If you're using a conda environment, make sure to activate it **before** installing the ZED Python API!

### Using Pip

- First, install the necessary requirements for the application using pip:

`pip install numpy cython opencv-python pyopengl pyside6 requests`

- Next, make sure to download the ZED SDK on [stereolabs.com](https://www.stereolabs.com/). Follow instructions for downloading the Python API.

## Using the Interface

> Make sure to include a screen capture of the interface here!

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
8. **Save Image and Depth Map**: Capture the image from the camera feed, both RGB and depth, and save along with metadata.
