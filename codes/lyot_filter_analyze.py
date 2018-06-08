#####################################################
# @Author: Abhilash Sarwade
# @Date:   2018-06-07 10:05:17
# @email: sarwade@isac.gov.in
# @File Name: lyot_filter_analyze.py
# @Project: lyot_filter

# @Last Modified time: 2018-06-08 13:14:07
#####################################################

from astropy.io import fits
import cv2
import numpy as np
import glob
import pickle
import os
from astropy.table import Table, Column

import easygui

def find_tilt(img,angle_range=[1,2]):
    
    angs = np.arange(angle_range[0],angle_range[1],0.001)
    cf = []
    rows,cols = img.shape

    for ang in angs:
        M = cv2.getRotationMatrix2D((cols/2,rows/2),ang,1)
        dst = cv2.warpAffine(img,M,(cols,rows))
        r1 = np.mean(dst[300:400,:],axis=0)
        r2 = np.mean(dst[900:1000,:],axis=0)
        #cor.append(np.correlate(r1,r2)[0])
        #rm.append(np.var(r1-r2)) 
        cf.append(np.corrcoef(r1,r2)[0,1])
    imax = np.argmax(cf)
    rot_angle = angs[imax]
    return rot_angle


### find tilts

data_folder = easygui.diropenbox(msg="open Directory", title="Open Directory", default="/media/abhilash/Deep Thought/Lyott filter tests")
out_folder = easygui.diropenbox(msg="Choose save directory", title="Save Directory", default="~/abhilash/lctf/lyot_filter/reduced_data")
if data_folder is None:
    exit(0)
print('Data Folder selected '+data_folder)
img_files = glob.glob(data_folder + '/*.fits')


rot_ang_file1 = glob.glob(data_folder+'/rotation_angle.pkl')
rot_ang_file2 = glob.glob(out_folder+'/rotation_angle.pkl')

if rot_ang_file1:
    fid_rot = open(rot_ang_file1, 'rb')
    print('Rotation angle file found in '+rot_ang_file1+'. Loading...')
    rot_angle = pickle.load(fid_rot)
elif rot_ang_file2:
    fid_rot = open(rot_ang_file2, 'rb')
    print('Rotation angle file found in '+rot_ang_file2+'. Loading...')
    rot_angle = pickle.load(fid_rot)
else:
    rot_angles = []

    for i in range(10):
        print('Calculating tilt in the images...')
        hdus = fits.open(img_files[i])
        img = hdus[0].data
        hdus.close()
        rows,cols = img.shape
        rot_angles.append(find_tilt(img,angle_range=[-0.7,0.6]))
        print('Tilt - ' + str(rot_angles[-1]))

    if np.std(rot_angles) > 0.2:
        print('Standard deviation of tilt is greater than 0.5 degrees. Check the data.')

    rot_angle = np.mean(rot_angles)
    fid_rot1 = open(data_folder+'/rot_angle.pkl','wb')
    fid_rot2 = open(out_folder+'/rot_angle.pkl','wb')
    pickle.dump(rot_angle,fid_rot1)
    pickle.dump(rot_angle,fid_rot2)
    fid_rot1.close()
    fid_rot2.close()



vlts=[]
mns = {}

print('Reading the data...')
for img_file in img_files:                                          
    hdus = fits.open(img_file)        
    
    img = hdus[0].data
    hdus.close()
    rows,cols = img.shape
    vlts.append(float(img_file[-9:-5]) / 100)
    #print(rot_angles[vlts[-1]])
    M = cv2.getRotationMatrix2D((cols/2,rows/2),rot_angle,1)
    dst = cv2.warpAffine(img,M,(cols,rows))
    #dst = np.fliplr(dst)
    dst = dst[350:1000,:]
    mn = np.mean(dst,axis=0)
    mns[vlts[-1]] = mn

vlts = np.array(vlts)
vlts = np.sort(vlts)


img_obs = np.zeros([len(vlts),2560])

for i in range(len(vlts)):
    img_obs[i,:] = mns[vlts[i]]

hdu_img = fits.PrimaryHDU(img_obs) 
t = Table(Column(vlts,name=('Voltage')))
hdu_table = fits.BinTableHDU(t) 

hdul = fits.HDUList([hdu_img,hdu_table])


if not os.path.isfile(out_folder+'/image.fits'):
    hdul.writeto(out_folder+'/image.fits')
    print('Image file written to ' + out_folder + '/image.fits')
else:
    print('Image file already exists.')