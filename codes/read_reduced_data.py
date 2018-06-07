#####################################################
# @Author: Abhilash Sarwade
# @Date:   2018-06-07 14:55:34
# @email: sarwade@isac.gov.in
# @File Name: read_reduced_data.py
# @Project: lyot_filter

# @Last Modified time: 2018-06-07 16:09:43
#####################################################

from astropy.io import fits
import numpy as np
import os
import easygui




def read_reduced_image(img_file):
	hdus = fits.open(img_file)
	img = hdus[0].data

	vlts = hdus[1].data['Voltage']
	return img,vlts

if __name__ = '__main__':
	img_file = easygui.fileopenbox(msg='Choose reduced image file',title='Choose file')
	img,vlts = read_reduced_image(img_file)
