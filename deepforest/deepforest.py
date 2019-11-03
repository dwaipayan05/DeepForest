"""
.. module:: deepforest
   :platform: Unix, Windows
   :synopsis: A module for individual tree crown detection using deep learning neural networks. see Weinstein et al. Remote Sensing. 2019

.. moduleauthor:: Ben Weinstein <ben.weinstein@weecology.org>

"""
import os
from deepforest import utilities
from deepforest import predict
from deepforest.retinanet_train import main as retinanet_train
from keras_retinanet.models import convert_model
from matplotlib import pyplot as plt

class deepforest:
    ''' Class for training and predicting tree crowns in RGB images
    
    Args:
        saved_model (str): Path to model saved on disk from keras.model.save(). Default is None
    
    Attributes:
        model: A keras training model from keras-retinanet
    '''
    
    def __init__(self, saved_model=None):
        self.saved_model = saved_model
        
        #Read config file
        self.config = utilities.read_config()
        
        #Load model if needed
        if self.saved_model is not None:
            self.model = utilities.read_model(self.saved_model, self.config)
        else:
            self.model = None
            
    def train(self, annotations, input_type="fit_generator", list_of_tfrecords=None, comet_experiment=None, images_per_epoch=None):
        '''Train a deep learning tree detection model using keras-retinanet
        This is the main entry point for training a new model based on either existing weights or scratch
        
        Args:
            annotations (str): Path to csv label file, labels are in the format -> path/to/image.jpg,x1,y1,x2,y2,class_name
            comet_experiment: A comet ml object to log images. Optional.
            list_of_tfrecords: Ignored if input_type != "tfrecord", list of tf records to process
            input_type: "fit_generator" or "tfrecord"
            images_per_epoch: number of images to override default config of # images in annotations file / batch size. Useful for debug
        Returns:
            model (object): A trained keras model
            prediction model: with bbox nms
            trained model: without nms
        '''
        arg_list = utilities.format_args(annotations, self.config, images_per_epoch)
        
        print("Training retinanet with the following args {}".format(arg_list))
        
        #Train model
        self.model, self.prediction_model, self.training_model = retinanet_train(args=arg_list, input_type = input_type, list_of_tfrecords = list_of_tfrecords, comet_experiment = comet_experiment)
    
    def use_release(self):
        '''Use the latest DeepForest model release from github and load model. Optionally download if release doesn't exist
        
        Returns:
            model (object): A trained keras model
        '''        
        #Download latest model from github release
        saved_model = utilities.use_release()  
        
        #load saved model
        self.saved_model = saved_model
        self.model = utilities.read_model(self.saved_model, self.config)
        
    def predict_image(self, image_path, return_plot=True, show=False):
        '''Predict tree crowns based on loaded (or trained) model
        
        Args:
            image_path (str): Path to image on disk
            show (bool): Plot the predicted image with bounding boxes. Ignored if return_plot=False
            return_plot: Whether to return image with annotations overlaid, or just a numpy array of boxes
        Returns:
            predictions (array): if return_plot, an image. Otherwise a numpy array of predicted bounding boxes
        '''     
        #Check for model save
        
        if(self.saved_model is None):
            raise ValueError("Model currently has no weights, either train a new model using deepforest.train, loading existing model, or use prebuilt model (see deepforest.use_release()")
        
        #convert model to prediction
        self.prediction_model = convert_model(self.model)
        
        if return_plot:
            image = predict.predict_image(self.prediction_model, image_path, return_plot=return_plot)            
            #cv2 channel order
            if show:
                plt.imshow(image[:,:,::-1])
                plt.show()             
            return image
        else:
            boxes = predict.predict_image(self.prediction_model, image_path, return_plot=return_plot)            
            return boxes            

