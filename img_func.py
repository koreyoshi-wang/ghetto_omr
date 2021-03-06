import numpy as np
import cv2
import matplotlib

def splitimg(im_inp,n_row,n_col):
    #determine size of input image
    h_img, w_img = im_inp.shape[:2]
    #determine size of each cropped image
    h_row = h_img / num_rows
    w_col = w_img / num_cols
    #declare fragmented image matrix
    img_frag = np.empty((num_rows, num_cols, h_row, w_col), dtype=np.uint8)
    #fragments input image and put it into matrix
    for i in range(0, num_rows):
        h0 = h_row * i
        h1 = h_row * (i + 1)
        for j in range(0, num_cols):
            w0 = w_col * j
            w1 = w_col * (j + 1)
            img_frag[i, j] = im_inp[h0:h1, w0:w1]
            #uncomment following lines for debugging to show image
            # cv2.imshow('image1', img_frag[i, j])
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
    return img_frag


def boundimg(im_inp):
    # Select ROI
    r = cv2.selectROI(im_inp)

    # Crop image
    imCrop = im_inp[int(r[1]):int(r[1] + r[3]), int(r[0]):int(r[0] + r[2])]

    # return cropped image
    return imCrop

def thres1 (im_inp):
    blurred = cv2.GaussianBlur(im_inp,(5,5),10)
    thresh = cv2.threshold(blurred,150,255,cv2.THRESH_BINARY)[1]
    return thresh, blurred


def canny(im_inp):
    edges = cv2.Canny(im_inp,100,200)

    matplotlib.pyplot.subplot(121),matplotlib.pyplot.imshow