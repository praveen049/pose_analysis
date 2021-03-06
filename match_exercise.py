#
#  https://www.gnu.org/licenses/gpl-3.0.en.html
#
# =============================================================
# This script take the video file as inputs as generates the
# names of the exercise of the video.
#
# This script is expected to be run as the first analyze to get
# only the name of the exercise.
################################################################
import tensorflow as tf
import commands
import sys
import cv2
import re
import pdb
import os.path
import argparse
import numpy as np
from tensorflow.python.platform import gfile
from collections import OrderedDict
from glob import glob

VIDEO_FPS = 25
SAMPLE = 5

def create_images(video_file, image_dir):
    """Create a list of images from the video file

    Returns:
       A list of image file names in the image_dir provided as argument.
    """
    extensions = ['jpg','jpeg','JPG','JPEG']
    file_list = []

    # Remove any old files in this folder with the default extension
    for extension in extensions:
        old_files = os.path.join(image_dir, '*.' + extension)
        for old_file in glob(old_files):
            os.remove(old_file)
    
    image_list = split_video(FLAGS.video_file, FLAGS.image_dir, SAMPLE)
   
    for extension in extensions:
        file_glob = os.path.join(image_dir, '*.' + extension)
        file_list.extend(gfile.Glob(file_glob))
    if not file_list:
        print('No image files created from the video')
        return None
    return file_list

def label_images(image_list):
    """
    Goes through the provied list of images and calculate the probabilities using the default tensorgraph.
    Sorts the resulting values and select the top-1

    Returns:
        A dictonary of the label and the top probilities
    """
    prod_list = {}
   # Unpersists graph from file
    with tf.gfile.FastGFile("../retrain/tf_files/flower_photos/retrained_graph.pb", 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        _ = tf.import_graph_def(graph_def, name='')
    for image in image_list:
        '''loop through the list of testing images from video'''
        image_data = tf.gfile.FastGFile(image, 'rb').read()
        # Loads label file, strips off carriage return
        label_lines = [line.rstrip() for line 
                       in tf.gfile.GFile("../retrain/tf_files/flower_photos/retrained_labels.txt")]
        with tf.Session() as sess:
            # Feed the image_data as input to the graph and get first prediction
            softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')

            predictions = sess.run(softmax_tensor, {'DecodeJpeg/contents:0': image_data})
            top_1 = predictions[0].argsort()[-len(predictions[0]):][::-1][0:1]

            for node_id in top_1:
                human_string = label_lines[node_id]
                score = predictions[0][node_id]
                exercise_string = human_string.split(None, 1)[0]
                if exercise_string in prod_list:                        
                    if score > prod_list.get(exercise_string, score):
                        prod_list[exercise_string] = score
                else:                      
                    prod_list[exercise_string] = score
    return prod_list

def split_video(video_file, image_dir, image_count):
    """
    Split the video using CV library

    Does not return anything but stores the split images into the image_dir
    """
    video = cv2.VideoCapture(video_file)
    pose_timestamp = [0, 5]
    fps = VIDEO_FPS
    poseCount = 0
    for i in range(0,len(pose_timestamp)):
        if i>0 and i%2 == 1:
            poseCount+=1
            duration = int(pose_timestamp[i])-int(pose_timestamp[i-1]) + 1
            frameNum = fps * duration          
            frameIgnore = frameNum / image_count - 1;
            readCount = 0
            writeCount = 0
            while readCount < frameNum:
                ignoreCount = 0
                readCount+=1
                while ignoreCount < frameIgnore and readCount < frameNum:
                    rval, frame = video.read()
                    ignoreCount+=1
                    readCount+=1              
                rval, frame = video.read()
                if writeCount < image_count:
                    cv2.imwrite(image_dir + '/pose'+str(poseCount)+'-'+str(writeCount) + '.jpg',frame)
                    writeCount+=1

def analyze_video(video_file):
    """
    Analyze the video and get information that will be used later on

    Returns
        A dictonary of the duration of the video, the frames per second,
    """
    video_specs = {}
    status, output = commands.getstatusoutput("ffmpeg -i "+video_file+" -vcodec copy -f rawvideo -y /dev/null 2>&1 | tr ^M '\n' | grep -i 'fps'")
    #print("the status is %s" %(status))
    #print("the output is %s" %(output))
	
    if status != 0:
        return 0
    lines = output.split('\n')
    entrys = lines[0].split(', ')
    fps = 0;
    frame = 0;
    
    for entry in entrys:
        posFPS = entry.find('fps')
        #print(posFPS)
        if(posFPS > 0):
            fpsStr = entry.split(' ')[0]
            fps = float(fpsStr)
            VIDEO_FPS = fps
            video_specs['fps'] = float(fpsStr)
            #print("fps is %d" %(float(fpsStr)))
            break
    entrys = re.split("\s+",lines[2]);
    frame = int(entrys[1])
    video_specs['frame']=int(entrys[1])

    return video_specs

def main(_):
  if not tf.gfile.Exists(FLAGS.video_file):
     print ("Video file '" + FLAGS.video_file + "'does not exist")
     return None
  if not tf.gfile.Exists(FLAGS.image_dir):
     print ("Image directory '" + FLAGS.image_dir + "' does not exist")
     return None
  if not tf.gfile.Exists("../image_classification/tf_files/flower_photos/retrained_labels.txt"):
      print ("The labels txt file is not correct relative path")
      return None
  if not tf.gfile.Exists("../image_classification/tf_files/flower_photos/retrained_graph.pb"):
      print ("The retrained graph not correct relative path")
      return None

  video_info = analyze_video(FLAGS.video_file)

  image_list = create_images(FLAGS.video_file, FLAGS.image_dir)
  
  label_dict = label_images(image_list)
  print label_dict
 
if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--image-dir',
      type=str,
      default='',
      help='The path to the output image files.'
  )
  parser.add_argument(
      '--video-file',
      type=str,
      default='',
      help='The inputs video files.'
  )
  FLAGS, unparsed = parser.parse_known_args()
  tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)
