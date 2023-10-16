import os
import nibabel as nib
import numpy as np
import csv
from PIL import Image, ImageDraw
import sys

def load_and_pad(in_file):
    nifti_img = nib.load(in_file)
    data = nifti_img.get_data()
    return data


def find_max_mean(matrix,xa_list,xp_list,y_list):
    global max_positiong
    global max_positionb
    max_mean = 0
    for y in y_list:
        max_meang = 0
        max_meanb = 0
        for x in xa_list:
            positions = []
            for i in range(x-3, x+4):
                for j in range(y-3, y+4):
                    if (i-x)**2 + (j-y)**2 <= 2.5**2:
                        positions.append((i,j))
            valuesg = [matrix[i][j][1] for i,j in positions]
            valuesr = [matrix[i][j][0] for i,j in positions]
            meang = np.mean(valuesg)-np.mean(valuesr)
            if meang > max_meang:
                max_meang = meang
                max_positiong = (x,y)             
        for x in xp_list:
            positions = []
            for i in range(x-3, x+4):
                for j in range(y-3, y+4):
                    if (i-x)**2 + (j-y)**2 <= 2.5**2:
                        positions.append((i,j))
            valuesb = [matrix[i][j][2] for i,j in positions]
            valuesr = [matrix[i][j][0] for i,j in positions]
            meanb = np.mean(valuesb)-np.mean(valuesr)
            if meanb > max_meanb:
                max_meanb = meanb
                max_positionb = (x,y)        
        max_meangb = max_meang+max_meanb
        if max_meangb > max_mean:
            max_mean = max_meangb
            a_position = max_positiong
            p_position = max_positionb
                      
    return a_position, p_position, max_mean

def calculate_circle_mean(a_position,img):
    positions = []
    data = nib.load(img).get_data()
    for i in range(a_position[0]-3, a_position[0]+4):
        for j in range(a_position[1]-3, a_position[1]+4):
            if (i-a_position[0])**2 + (j-a_position[1])**2 <= 5**2:
                positions.append((i,j))
    values = [data[i][j][a_position[2]] for i,j in positions]
    circle_mean = np.mean(values)          
    return circle_mean

def plot_roi(colormap,outfile,xa,xp,y,z):

    img = nib.load(colormap)    
    data = img.get_data()
    
    matrix=data[:,:,z]
    r=np.zeros(np.shape(matrix))
    g=np.zeros(np.shape(matrix))
    b=np.zeros(np.shape(matrix))
    matrix=data[:,:,z]


    for i in range(0,182):
        for j in range(0,218):
            r[i,j] = matrix[i,j][0]
            g[i,j] = matrix[i,j][1]
            b[i,j] = matrix[i,j][2]
    
    r=255*(r / np.max(r))
    g=255*(g / np.max(g))
    b=255*(b / np.max(b))
                
    rgb_image = np.dstack((r, g, b)).astype(np.uint8)
    pil_image = Image.fromarray(rgb_image)

    img = pil_image.transpose(Image.TRANSPOSE)

    resized_img = img.resize((img.width*4, img.height*4), resample=Image.NEAREST)
    
    draw = ImageDraw.Draw(resized_img)
    center = (xa*4, y*4)
    radius = 10
    thickness = 1
    draw.ellipse([(center[0]-radius, center[1]-radius), 
              (center[0]+radius, center[1]+radius)],
             outline="white", width=thickness)
    
    center = (xp*4, y*4)    
    radius = 10
    thickness = 1
    draw.ellipse([(center[0]-radius, center[1]-radius), 
              (center[0]+radius, center[1]+radius)],
             outline="white", width=thickness)
    
    flipped_image = resized_img.transpose(Image.FLIP_TOP_BOTTOM)
    img = flipped_image.transpose(Image.FLIP_LEFT_RIGHT)
    img.save(outfile)


xa_l_list = range(120, 135)
xp_l_list = range(100, 125)
xa_r_list = range(46, 60)
xp_r_list = range(57, 69)
y_list = range(100,120)
z_list = range(95,105)

root_path = './'
keyword = 'sub'

for root, dirs, files in os.walk(root_path):
    for dir_name in dirs:
        try:
            if keyword in dir_name:
                print(dir_name)
                l_max_mean=0
                r_max_mean=0
                path_colormap = dir_name + '/DTI_reoriented_ColorMap.nii.gz'
                for z in z_list:
                    data = load_and_pad(path_colormap)
                    a_l_position, p_l_position, l_max_meangb = find_max_mean(data[:,:,z],xa_l_list,xp_l_list,y_list)
                    if l_max_meangb > l_max_mean:
                        l_max_mean = l_max_meangb
                        a_l_max_position = a_l_position + (z,)
                        p_l_max_position = p_l_position + (z,)
                
                for z in z_list:
                    data = load_and_pad(path_colormap)
                    a_r_position, p_r_position, r_max_meangb = find_max_mean(data[:,:,z],xa_r_list,xp_r_list,y_list)
                    if r_max_meangb > r_max_mean:
                        r_max_mean = r_max_meangb
                        a_r_max_position = a_r_position + (z,)
                        p_r_max_position = p_r_position + (z,)    
                   
                
                print(a_l_max_position)    
                print(p_l_max_position)
                print(a_r_max_position)
                print(p_r_max_position)
                
                colormap = path_colormap
                outfile = dir_name + '_l.jpg'
                xa = a_l_max_position[0]
                xp = p_l_max_position[0]
                y = a_l_max_position[1]
                z = a_l_max_position[2]
                plot_roi(colormap,outfile,xa,xp,y,z)

                colormap = path_colormap
                outfile = dir_name + '_r.jpg'
                xa = a_r_max_position[0]
                xp = p_r_max_position[0]
                y = a_r_max_position[1]
                z = a_r_max_position[2]
                plot_roi(colormap,outfile,xa,xp,y,z)
                
                path_Dxx = dir_name + '/dti_reoriented_Dxx.nii.gz'
                path_Dyy = dir_name + '/dti_reoriented_Dyy.nii.gz'
                path_Dzz = dir_name + '/dti_reoriented_Dzz.nii.gz'
                
                dxx_l_a=calculate_circle_mean(a_l_max_position,path_Dxx)
                dxx_l_p=calculate_circle_mean(p_l_max_position,path_Dxx)
                dyy_l_p=calculate_circle_mean(p_l_max_position,path_Dyy)
                dzz_l_p=calculate_circle_mean(a_l_max_position,path_Dzz)
                alps_l=(dxx_l_a+dxx_l_p)/(dyy_l_p+dzz_l_p)
                
                dxx_r_a=calculate_circle_mean(a_r_max_position,path_Dxx)
                dxx_r_p=calculate_circle_mean(p_r_max_position,path_Dxx)
                dyy_r_p=calculate_circle_mean(p_r_max_position,path_Dyy)
                dzz_r_p=calculate_circle_mean(a_r_max_position,path_Dzz)
                alps_r=(dxx_r_a+dxx_r_p)/(dyy_r_p+dzz_r_p)
                
                print(alps_l)
                print(alps_r)
                
                with open('results.csv', 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([dir_name,a_l_max_position,p_l_max_position,dxx_l_a,dxx_l_p,dyy_l_p,dzz_l_p,alps_l,a_r_max_position,p_r_max_position,dxx_r_a,dxx_r_p,dyy_r_p,dzz_r_p,alps_r])  

        except Exception as e:
            print(f"Error occurred: {e}")
            continue

                
