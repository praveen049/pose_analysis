import tensorflow as tf
import sys
import argparse
from tensorflow.python.platform import gfile

def create_images(video_file, image_dir, image_count):
    print ("inside create images")

def label_images(image_list):
    print ("inside lavel images")
    
def main(_):
  if not tf.gfile.Exists(FLAGS.video_file):
     print ("Video file '" + FLAGS.video_file + "'does not exist")
     return None
  if not tf.gfile.Exists(FLAGS.image_dir):
     print ("Image directory '" + FLAGS.image_dir + "' does not exist")
     return None
  image_list = create_images(FLAGS.video_file, FLAGS.image_dir,
                              FLAGS.images)
  label_list = label_images(image_list)
 

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--image_dir',
      type=str,
      default='',
      help='The path to the output image files.'
  )
  parser.add_argument(
      '--video_file',
      type=str,
      default='',
      help='The inputs video files.'
  )
  parser.add_argument(
      '--sections',
      type=str,
      default='1',
      help='The number of section to split the video into.'
  )
  parser.add_argument(
      '--images',
      type=str,
      default='20',
      help='The number of image per section.'
  )
  FLAGS, unparsed = parser.parse_known_args()
  tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)
