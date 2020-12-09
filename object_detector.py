import os
import pathlib
import cv2

import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile

from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image
from IPython.display import display

from object_detection.utils import ops as utils_ops
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

def load_model(model_name):
	model = tf.saved_model.load("saved_models/")
	return model

def run_inference_for_single_image(model, image):
	image = np.asarray(image)
	input_tensor = tf.convert_to_tensor(image)
	input_tensor = input_tensor[tf.newaxis,...]

	model_fn = model.signatures['serving_default']
	output_dict = model_fn(input_tensor)

	num_detections = int(output_dict.pop('num_detections'))
	output_dict = {key:value[0, :num_detections].numpy() 
					for key,value in output_dict.items()}
	output_dict['num_detections'] = num_detections

	output_dict['detection_classes'] = output_dict['detection_classes'].astype(np.int64)
	
	# Handle models with masks:
	if 'detection_masks' in output_dict:
		utils_ops.tf = tf.compat.v1
		detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
				tf.convert_to_tensor(output_dict["detection_masks"]),
				output_dict["detection_boxes"],
				image.shape[0], image.shape[1])      
		detection_masks_reframed = tf.cast(detection_masks_reframed > 0.5, tf.uint8)
		output_dict['detection_masks_reframed'] = detection_masks_reframed.numpy()		
	return output_dict

def show_inference(model, image_path, count):
	PATH_TO_LABELS = 'object_detection/mscoco_label_map.pbtxt' # list of classes to classify
	category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)
	image_np = np.array(Image.open(image_path))
	output_dict = run_inference_for_single_image(model, image_np)
	vis_util.visualize_boxes_and_labels_on_image_array(
		image_np,
		output_dict['detection_boxes'],
		output_dict['detection_classes'],
		output_dict['detection_scores'],
		category_index,
		instance_masks=output_dict.get('detection_masks_reframed', None),
		use_normalized_coordinates=True,
		line_thickness=8)
	img = Image.fromarray(image_np)
	return img

def run():
	tf.gfile = tf.io.gfile
	detection_model = load_model("ssd_mobilenet_v1_coco_2017_11_17") # run model by model name
	count = 0
	PATH_TO_TEST_IMAGES_DIR = pathlib.Path('uploads') # TEST Images
	TEST_IMAGE_PATHS = list(pathlib.Path("uploads").glob("*.jpg"))
	detected_image = show_inference(detection_model, TEST_IMAGE_PATHS[0], count)
	return detected_image

# model_name = "mask_rcnn_inception_resnet_v2_atrous_coco_2018_01_28"
# masking_model = load_model(model_name)

# # masking_model.signatures["serving_default"].output_shapes
# count = 0
# for image_path in TEST_IMAGE_PATHS:
# 	show_inference(masking_model, image_path, count)
# 	count += 1
