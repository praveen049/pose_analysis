import tensorflow as tf
import sys
import os.path
import argparse
from tensorflow.python.platform import gfile

def create_images(video_file, image_dir, image_count):
    extensions = ['jpg','jpeg','JPG','JPEG']
    file_list = []

    for extension in extensions:
        file_glob = os.path.join(image_dir, '*.' + extension)
        file_list.extend(gfile.Glob(file_glob))
    if not file_list:
        print('No image files created from the video')
        return None
    if len(file_list) != image_count:
        print ('Wrong number of files created. Configured: ' + image_count)
        return None
    return file_list

def label_images(image_list):
    print ("inside lavel images")
    for image in image_list:
        image_data = tf.gfile.FastGFile(image, 'rb').read()
        # Loads label file, strips off carriage return
        label_lines = [line.rstrip() for line 
                       in tf.gfile.GFile("../image_classification/tf_files/flower_photos/retrained_labels.txt")]
        # Unpersists graph from file
        with tf.gfile.FastGFile("../image_classification/tf_files/flower_photos/retrained_graph.pb", 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            _ = tf.import_graph_def(graph_def, name='')
        with tf.Session() as sess:
            # Feed the image_data as input to the graph and get first prediction
            softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
   
            predictions = sess.run(softmax_tensor, \
             {'DecodeJpeg/contents:0': image_data})
   
            # Sort to show labels of first prediction in order of confidence
            top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]
   
            for node_id in top_k:
                human_string = label_lines[node_id]
                score = predictions[0][node_id]
                print('%s (score = %.5f)' % (human_string, score))

    
def main(_):
  if not tf.gfile.Exists(FLAGS.video_file):
     print ("Video file '" + FLAGS.video_file + "'does not exist")
     return None
  if not tf.gfile.Exists(FLAGS.image_dir):
     print ("Image directory '" + FLAGS.image_dir + "' does not exist")
     return None
  image_list = create_images(FLAGS.video_file, FLAGS.image_dir,
                              FLAGS.images)
  print len(image_list)
  label_list = label_images(image_list)
 

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
  parser.add_argument(
      '--sections',
      type=int,
      default='1',
      help='The number of section to split the video into.'
  )
  parser.add_argument(
      '--images',
      type=int,
      default='20',
      help='The number of image per section.'
  )
  FLAGS, unparsed = parser.parse_known_args()
  tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)
