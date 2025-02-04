import cv2
import numpy as np

def sobel_filter(img: np.ndarray, ksize: int = 3) -> np.ndarray:
    """
    Applies the Sobel filter to an input image to detect edges.

    Parameters:
        img (np.ndarray): Input image in BGR format.
        ksize (int): Size of the extended Sobel kernel; it must be an odd number. Default is 3.
    Returns:
        np.ndarray: Output image with edges detected, normalized to the range [0, 255].
    Raises:
        ValueError: If the kernel size is not an odd number.
    """
    if ksize % 2 == 0:
        raise ValueError("Kernel size must be an odd number")
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=ksize)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=ksize)
    sobel = np.sqrt(sobelx ** 2 + sobely ** 2)
    sobel_norm = (sobel * 255 / sobel.max()).astype(np.uint8)
    return sobel_norm