import numpy as np
import cv2
import matplotlib.pyplot as plt
import math

#Part 1: Image Loading
#-------------------------------------------------------------------

#load image
img = cv2.imread('img_data/omstest2.jpg',cv2.IMREAD_GRAYSCALE)
img2= cv2.imread('img_data/omstest2.jpg')
img3=cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)

#bilateral filter, sharpen, thresh image
biblur=cv2.bilateralFilter(img,20,175,175)
sharp=cv2.addWeighted(img,1.55,biblur,-0.5,0)
ret1,thresh1 = cv2.threshold(sharp,127,255,cv2.THRESH_OTSU)

#negative and closed image
inv=cv2.bitwise_not(thresh1)
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
closed = cv2.morphologyEx(inv, cv2.MORPH_CLOSE, kernel)

#Part 2: Finding Valid Contours
#-------------------------------------------------------------------
#find countours
im2, contours, hierarchy = cv2.findContours(closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)


#prepare empty canvas
height, width = img.shape[:2]
emptycanvas=np.zeros((height,width),dtype=np.uint8)

#truncate contours with A<10
kcounter = 0
for c in contours:

    A = cv2.contourArea(c)

    if A<100:
        contours=np.delete(contours,kcounter,0)
        kcounter=kcounter-1
    kcounter=kcounter+1

#find length of contour array
clen=len(contours)

#create match_array [dimension = len x len] with 0s
match_array=np.zeros((clen,clen),np.uint8)

#loop over the contours and compare two by two
icounter = 0
for i in contours:
    jcounter = 0

    for j in contours:
    #If difference has index <0.01 then regard as TRUE
        ret=cv2.matchShapes(i,j,1,0.0)
        if ret<0.01:
            match_array[icounter,jcounter]=1
        else:
            match_array[icounter,jcounter]=0
        jcounter=jcounter+1
    icounter=icounter+1


#sum each row of the array (for TRUEs and FALSEs]
sum_array=np.sum(match_array,axis=1,dtype=np.int32)

#finding mean of the comparison value
sum_array2=np.sum(sum_array,axis=0,dtype=np.int32)
sum_array_len=len(sum_array)
ave_sim_val=sum_array2/sum_array_len
#Assumption: there is a lot of 1s

#counters
#creation of new array to store centre point
#variables
counter_a=0
counter_s=0
counter_m=0
valid_counter =0
centpt_array = np.array([[0,0,0]])

hor_dist_acc=0
ver_dist_acc=0

#Area array
area_arr=np.array([])

#find valid mean area and SD
for k in sum_array:
    if k>ave_sim_val:
        A = cv2.contourArea(contours[counter_s])
        area_arr=np.append(area_arr,[A],0)
        counter_a=counter_a+1
    counter_s=counter_s +1

sum_area_array=np.array([])
sum_area_array=np.sum(area_arr,axis=0,dtype=np.uint32)
mean_valid_A=sum_area_array/counter_a
sum_dif=0

for a in area_arr:
    dif = (mean_valid_A - a)**2
    sum_dif=sum_dif+dif
SD_valid=(sum_dif/counter_a)**0.5

#find midpoints of contours that fulfils 1)high similarity 2)occurence greater than average 3)least deviation from valid mean area
for i in sum_array:

    if i>ave_sim_val:
        cv2.drawContours(img3, contours, counter_m, (0, 255, 0), 3)

        #Determine valid mean area
        condition = cv2.contourArea(contours[counter_m])>mean_valid_A-2*SD_valid and cv2.contourArea(contours[counter_m])<mean_valid_A+2*SD_valid
        if condition:

            # obtain centre point of each contour
            M = cv2.moments(contours[counter_m])
            cX = int(M['m10'] / M['m00'])
            cY = int(M['m01'] / M['m00'])

            # store in it arrays
            new_centpt_array=np.array([[cX,cY,counter_m]])
            centpt_array=np.concatenate((centpt_array,new_centpt_array),axis=0)

            #determine horizontal point and vertical point
            c=contours[counter_m]
            Xt_right=np.asarray(tuple(c[c[:,:,0].argmax()][0]))
            Xt_bot=np.asarray(tuple(c[c[:,:,1].argmax()][0]))

            hor_dist=Xt_right[0]-cX
            ver_dist=Xt_bot[1]-cY
            hor_dist_acc=hor_dist_acc+hor_dist
            ver_dist_acc=ver_dist_acc+ver_dist

            valid_counter = valid_counter +1

    counter_m = counter_m+1

mean_hor_dist=hor_dist_acc/valid_counter
mean_ver_dist=ver_dist_acc/valid_counter


#delete 1st row
centpt_array=np.delete(centpt_array,0,0)

# #checkpoint for adding array
centpt_array=np.append(centpt_array,[[100,100,1000]],0)
centpt_array=np.append(centpt_array,[[40,290,1001]],0)
centpt_array=np.append(centpt_array,[[450,800,1002]],0)
centpt_array=np.append(centpt_array,[[100,300,1003]],0)
centpt_array=np.append(centpt_array,[[0,0,1004]],0)

#Removing Duplicates
g=0
arr_len=len(centpt_array)

while arr_len>g:
    target_arr1 = centpt_array[g]
    h=1+g
    while arr_len>h and h>g:
        target_arr2 = centpt_array[h]

        if abs(target_arr1[0]-target_arr2[0])<mean_hor_dist:
            if abs(target_arr1[1]-target_arr2[1])<mean_ver_dist:
                centpt_array=np.delete(centpt_array,h,0)
                h=h-1
                arr_len=arr_len-1
        h = h + 1
    g=g+1



#Part3:Forming Grids
#Assumption: Bubbles are arranged in horinzontal x vertical grid (but not oblique)
#---------------------------------------------------------------------------------------------

#Part3a:Forming grid
#-----------------------------
#Scanning center point x and y and sort
cX_array=np.array([])
cY_array=np.array([])

for k in centpt_array:
    cX_array = np.append(cX_array, [k[0]], 0)
    cX_array=np.sort(cX_array,axis=0,kind='mergesort')
    cY_array = np.append(cY_array, [k[1]], 0)
    cY_array = np.sort(cY_array, axis=0, kind='mergesort')


#group the sorted array of x and y
g = 0
temp_var_counter=0
grp_cX_array=np.array([])
while g < len(cX_array):
    if g==0:
        temp_var=cX_array[g]
        temp_var_counter=1

    elif cX_array[g]-cX_array[g-1]<mean_hor_dist:
        if g == len(cX_array) - 1:
            temp_var = temp_var + cX_array[g]
            temp_var_counter = temp_var_counter + 1
            temp_var_ave = temp_var / temp_var_counter
            grp_cX_array = np.append(grp_cX_array, [temp_var_ave], 0)
            temp_var = 0
            temp_var_counter = 0
        else:
            temp_var=temp_var+cX_array[g]
            temp_var_counter=temp_var_counter+1

    elif cX_array[g]-cX_array[g-1]>mean_hor_dist:
        if g == len(cX_array) - 1:
            temp_var = cX_array[g]
            temp_var_counter = 1
            temp_var_ave = temp_var / temp_var_counter
            grp_cX_array = np.append(grp_cX_array, [temp_var_ave], 0)
            temp_var = 0
            temp_var_counter = 0
        else:
            temp_var_ave=temp_var/temp_var_counter
            grp_cX_array = np.append(grp_cX_array,[temp_var_ave],0)
            temp_var=cX_array[g]
            temp_var_counter=1
    g=g+1

h = 0
temp_var_counter=0
grp_cY_array=np.array([])
while h < len(cY_array):
    if h==0:
        temp_var=cY_array[h]
        temp_var_counter=1



    elif cY_array[h]-cY_array[h-1]<mean_ver_dist:
        if h == len(cY_array) - 1:
            temp_var = temp_var + cY_array[h]
            temp_var_counter = temp_var_counter + 1
            temp_var_ave = temp_var / temp_var_counter
            grp_cY_array = np.append(grp_cY_array, [temp_var_ave], 0)
            temp_var = 0
            temp_var_counter = 0
        else:
            temp_var=temp_var+cY_array[h]
            temp_var_counter=temp_var_counter+1

    elif cY_array[h]-cY_array[h-1]>mean_ver_dist:
        if h == len(cY_array) - 1:
            temp_var = cY_array[h]
            temp_var_counter = 1
            temp_var_ave = temp_var / temp_var_counter
            grp_cY_array = np.append(grp_cY_array, [temp_var_ave], 0)
            temp_var = 0
            temp_var_counter = 0
        else:
            temp_var_ave=temp_var/temp_var_counter
            grp_cY_array = np.append(grp_cY_array,[temp_var_ave],0)
            temp_var=cY_array[h]
            temp_var_counter=1
    h=h+1



#set up grid m x n
grid_row_len=len(grp_cY_array)
grid_col_len=len(grp_cX_array)

matrix_grid=np.zeros((grid_row_len,grid_col_len),dtype=np.ndarray)

#fill in the grid
for k in centpt_array:
    p=0
    while p < grid_col_len:
        if k[0]<grp_cX_array[p]+mean_hor_dist and k[0]>grp_cX_array[p]-mean_hor_dist:

            q=0
            while q<grid_row_len:
                if k[1]<grp_cY_array[q]+mean_ver_dist and k[1]>grp_cY_array[q]-mean_ver_dist:
                    matrix_grid[q,p]=k
                q=q+1
        p=p+1


#Part3b:
#creating function to check spacing are equal for both x and y
def SpaceFunc(matr):
    matr_shape = matr.shape
    spa_X_array = np.array([])
    spa_Y_array = np.array([])
    val_X_matrix = np.zeros((matr_shape[0], matr_shape[1]), dtype=np.ndarray)
    val_Y_matrix = np.zeros((matr_shape[0], matr_shape[1]), dtype=np.ndarray)
    val_X_matrix_counter = np.zeros((matr_shape[0], matr_shape[1]), dtype=np.ndarray)
    val_Y_matrix_counter=np.zeros((matr_shape[0], matr_shape[1]), dtype=np.ndarray)


    counter_g1 = 0
    while counter_g1 < matr_shape[1]:
        counter_g2 = 0
        while counter_g2 < matr_shape[0]:
            matr_value = matr[counter_g2, counter_g1]
            matr_value=np.asarray(matr_value)

            if matr_value.size==3:
                val_X_matrix[counter_g2, counter_g1] = matr_value[0]
                val_Y_matrix[counter_g2, counter_g1] = matr_value[1]
                val_X_matrix_counter[counter_g2, counter_g1] = 1
                val_Y_matrix_counter[counter_g2, counter_g1] = 1
            elif matr_value.size == 0:
                val_X_matrix[counter_g2, counter_g1] = 0
                val_Y_matrix[counter_g2, counter_g1] = 0
                val_X_matrix_counter[counter_g2, counter_g1] = 0
                val_Y_matrix_counter[counter_g2, counter_g1] = 0
            counter_g2 = counter_g2 + 1
        counter_g1 = counter_g1 + 1

    val_X_array_counter = val_X_matrix_counter.sum(axis=0)
    val_Y_array_counter = val_Y_matrix_counter.sum(axis=1)
    val_X_array_acc = val_X_matrix.sum(axis=0)
    val_Y_array_acc=val_Y_matrix.sum(axis=1)
    val_X_array = val_X_array_acc/val_X_array_counter
    val_Y_array = val_Y_array_acc / val_Y_array_counter

    spa_X_array=np.ediff1d(val_X_array)
    spa_Y_array=np.ediff1d(val_Y_array)

#Creating function to convert matrix to binary (those with value to 1, those with 0 to 0)
def MatBinFunc(matr):
    matr_shape = matr.shape
    matr_bin=np.ones((matr_shape[0],matr_shape[1]),dtype=np.uint8)

    counter_g1 = 0
    while counter_g1 < matr_shape[1]:
        counter_g2 = 0
        while counter_g2 < matr_shape[0]:
            matr_value = matr[counter_g2, counter_g1]
            matr_value=np.asarray(matr_value)
            if matr_value.size == 1:
                if matr_value==0:
                    matr_bin[counter_g2, counter_g1]=0

            counter_g2 = counter_g2 + 1
        counter_g1 = counter_g1 + 1
    return matr_bin

#Creating a function to optimise a binary matrix to grid form of 1 x 1
#Methodology:
# 1)Sum rows and columns
# 2)Forming matrix to determine the strength of each cells = (Row.value + Column.value)/2
# 3)Find sum of strength of each column and row
# 4)Defining parameters (
def OptMatFunc(matr,degree):
    row_sum=np.sum(matr,axis=1)
    col_sum = np.sum(matr, axis=0)

    matr_shape=matr.shape
    str_matr=np.zeros((matr_shape[0],matr_shape[1]),dtype=np.uint16)

    m=0
    while m<matr_shape[0]:
        n=0
        while n<matr_shape[1]:
            str_matr[m, n]=(row_sum[m]+col_sum[n]-2)*matr[m,n]
            n=n+1
        m=m+1

    row_sum_str = np.sum(str_matr, axis=1)
    col_sum_str = np.sum(str_matr, axis=0)
    print str_matr
    print row_sum_str
    print col_sum_str

    #calculate half of the strength marker (high and low)
    str_marker_high = matr_shape[0]+matr_shape[1]- math.floor(float(matr_shape[0])/2)-math.floor(float(matr_shape[1])/2)-2
    str_marker_low = matr_shape[0] + matr_shape[1] - math.ceil(float(matr_shape[0]) / 2) - math.ceil(float(matr_shape[1]) / 2) - 2

    # calculate half of the strength multiplier (high and low)
    row_str_multi_high=math.ceil(float(matr_shape[0])/2)
    row_str_multi_low = math.floor(float(matr_shape[0])/2)
    col_str_multi_high=math.ceil(float(matr_shape[1])/2)
    col_str_multi_low = math.floor(float(matr_shape[1]) / 2)

    #for parameter (only odd row or column will make a great difference due to floor and ceiling,
    #even row and column will not show any difference)
    if degree == 1:
        row_str_parameter=str_marker_high*row_str_multi_high
        col_str_parameter = str_marker_high*col_str_multi_high
    elif degree == 2:
        row_str_parameter=str_marker_high*row_str_multi_low
        col_str_parameter = str_marker_high*col_str_multi_low
    elif degree == 3:
        row_str_parameter=str_marker_low*row_str_multi_high
        col_str_parameter = str_marker_low*col_str_multi_high
    elif degree == 4:
        row_str_parameter=str_marker_low*row_str_multi_low
        col_str_parameter = str_marker_low*col_str_multi_low
    else:
        print 'no valid parameter'

    print row_str_parameter
    print col_str_parameter

    p=0
    compress_criteria_row=np.array([])
    while p<matr_shape[0]:
        if row_sum_str[p]<row_str_parameter:
             compress_criteria_row=np.append(compress_criteria_row,0)
        else:
            compress_criteria_row=np.append(compress_criteria_row,1)
        p=p+1

    q=0
    compress_criteria_col= np.array([])
    while q<matr_shape[1]:
        if col_sum_str[q]<col_str_parameter:
             compress_criteria_col=np.append(compress_criteria_col,0)
        else:
            compress_criteria_col=np.append(compress_criteria_col,1)
        q=q+1

    matr=np.compress(compress_criteria_row,matr,axis=0)
    matr= np.compress(compress_criteria_col, matr, axis=1)
    print matr

#Run Matrix Binarisation
bin_matr=MatBinFunc(matrix_grid)
print bin_matr
OptMatFunc(bin_matr,4)
#print x




#checkpoint
#print centpt_array
# print '-----------'
#print valid_counter
#print len(centpt_array)
#print mean_hor_dist
#print mean_ver_dist




#initialise plot
plt.subplot(111),plt.imshow(img3)
plt.title('dilate1 Image'), plt.xticks([]), plt.yticks([])
for k in centpt_array:
    plt.plot(k[0],k[1],'ro')


plt.show()

cv2.waitKey(0)



