import skimage.io as io
import scipy.io as scio
import os
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from collections import Counter
from skimage import transform
import scipy.misc as m
import pdb


def crop(S2_root,crop_size_h,crop_size_w,prefix,save_dir,crop_label=False):

	raw_S2_B02 = io.imread(S2_root+'/B02.tif',dtype=np.uint8)[:,:,0]
	raw_S2_B03 = io.imread(S2_root+'/B03.tif',dtype=np.uint8)[:,:,0]
	raw_S2_B04 = io.imread(S2_root+'/B04.tif',dtype=np.uint8)[:,:,0]
	raw_S2_B08 = io.imread(S2_root+'/B08.tif',dtype=np.uint8)[:,:,0]
	raw_S2_B11 = io.imread(S2_root+'/B11.tif',dtype=np.uint8)[:,:,0]
	raw_S2_B12 = io.imread(S2_root+'/B12.tif',dtype=np.uint8)[:,:,0]

	raw_S2_4 = [raw_S2_B02, raw_S2_B03, raw_S2_B04, raw_S2_B08]
	raw_S2_2 = [raw_S2_B11, raw_S2_B12]

	raw_S2_4 = np.stack(raw_S2_4,axis=2)
	raw_S2_2 = np.stack(raw_S2_2,axis=2)

	h_S2_4,w_S2_4,ch_S2_4 = raw_S2_4.shape
	h_S2_2,w_S2_2,ch_S2_2 = raw_S2_2.shape

	index = 0

	x2,y2 = 0,0
	x0,y0 = 0,0

	stride_h = crop_size_h
	stride_w = crop_size_w

	while(y2<h_S2_2 and y2*2<h_S2_4):
		while(x2<w_S2_2 and x2*2<w_S2_4):
			x1 = x0
			x2 = x1 + crop_size_w
			y1 = y0
			y2 = y1 +crop_size_h

			print(x1,y1,x2,y2)

			if(x2>w_S2_2 or y2>h_S2_2):
				break
			elif(x2*2>w_S2_4 or y2*2>h_S2_4):
				break
			else:
				patch_S2_2_label = raw_S2_2[y1:y2,x1:x2]

				patch_S2_4_label = raw_S2_4[y1*2:y2*2,x1*2:x2*2]

				patch_S2_2 = np.zeros((crop_size_h//2,crop_size_w//2,ch_S2_2),dtype=np.uint8)
				patch_S2_2_up = np.zeros((crop_size_h,crop_size_w,ch_S2_2),dtype=np.uint8)
				patch_S2_4 = np.zeros((crop_size_h,crop_size_w,ch_S2_4),dtype=np.uint8)
				for i in range(ch_S2_2):
					patch_S2_2[:,:,i] = m.imresize(patch_S2_2_label[:,:,i], (crop_size_h//2,crop_size_w//2), 'bicubic')
				for i in range(ch_S2_2):
					patch_S2_2_up[:,:,i] = m.imresize(patch_S2_2[:,:,i], (crop_size_h,crop_size_w), 'bicubic')

				for i in range(ch_S2_4):
					patch_S2_4[:,:,i] = m.imresize(patch_S2_4_label[:,:,i], (crop_size_h,crop_size_w), 'bicubic')
				
				#patch_S2 = np.uint8(patch_S2)

				patch_S2_4_vis = patch_S2_4[:,:,:3][:,:,::-1]
				patch_S2_4_label_vis = patch_S2_4_label[:,:,:3][:,:,::-1]

				io.imsave(os.path.join(save_dir,'S2_10m_4_vis',prefix+"_%d.tif"%(index)),patch_S2_4_vis)
				io.imsave(os.path.join(save_dir,'S2_10m_4_label_vis',prefix+"_%d.tif"%(index)),patch_S2_4_label_vis)


			x0 = x1 + stride_w

			io.imsave(os.path.join(save_dir,'S2_10m_4',prefix+"_%d.tif"%(index)),patch_S2_4)
			io.imsave(os.path.join(save_dir,'S2_10m_4_label',prefix+"_%d.tif"%(index)),patch_S2_4_label)
			io.imsave(os.path.join(save_dir,'S2_20m_B11',prefix+"_%d.tif"%(index)),patch_S2_2[:,:,0])
			io.imsave(os.path.join(save_dir,'S2_20m_B11_up',prefix+"_%d.tif"%(index)),patch_S2_2_up[:,:,0])
			io.imsave(os.path.join(save_dir,'S2_20m_B11_label',prefix+"_%d.tif"%(index)),patch_S2_2_label[:,:,0])
			io.imsave(os.path.join(save_dir,'S2_20m_B12',prefix+"_%d.tif"%(index)),patch_S2_2[:,:,1])
			io.imsave(os.path.join(save_dir,'S2_20m_B12_up',prefix+"_%d.tif"%(index)),patch_S2_2_up[:,:,1])
			io.imsave(os.path.join(save_dir,'S2_20m_B12_label',prefix+"_%d.tif"%(index)),patch_S2_2_label[:,:,1])

			index = index + 1

		x0,x1,x2 = 0,0,0
		y0 = y1 + stride_h


def generate_trainval_list(pathdir):
	labels_img_paths = os.listdir(os.path.join(pathdir,'S2_20m_B11_label'))
	labels_count_list=dict()
	for labels_img_path in tqdm(labels_img_paths):
		label = io.imread(os.path.join(pathdir,'S2_20m_B11_label',labels_img_path))
		most_count_label= np.argmax(np.bincount(label.flatten().tolist()))
		labels_count_list[labels_img_path] = most_count_label
	values= labels_count_list.values()
	count_dict= Counter(values)
	print(count_dict)


def write_train_list(pathdir):
	labels_img_paths = os.listdir(os.path.join(pathdir,'S2_20m_B11_label'))
	num_sets = len(labels_img_paths)
	indexs = list(range(num_sets))
	np.random.shuffle(indexs)
	train_set_num = 0.9 * num_sets
	train_f = open(os.path.join(pathdir,'train.txt'),'w')
	val_f = open(os.path.join(pathdir,'val.txt'),'w')
	trainval_f = open(os.path.join(pathdir,'trainval.txt'),'w')
	for index in range(num_sets):
		if(index<train_set_num):
			# print >>train_f,labels_img_paths[indexs[index]]
			print(labels_img_paths[indexs[index]], file=train_f)
		else:
			# print >>val_f,labels_img_paths[indexs[index]]
			print(labels_img_paths[indexs[index]], file=val_f)
		# print >>trainval_f,labels_img_paths[indexs[index]]
		print(labels_img_paths[indexs[index]], trainval_f)
	train_f.close()
	val_f.close()
	trainval_f.close()
