
from options.test_options import TestOptions
from data import create_dataset
from models import create_model
from videoProcess import  *
from util.visualizer import save_images
from util import html
from PIL import Image
from flask import Flask, flash, redirect, jsonify, request, render_template, send_from_directory
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
from os import path
from shutil import copyfile
import io, glob, base64, shutil, os.path, time
# Init server
app = Flask('braces2teeth')
app.config['UPLOAD_FOLDER'] = 'datasets'
CORS(app)
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

fileName = ''
def uploadFile():
    f = request.files['file']
    global fileName 
    fileName = f.filename[0:-4]
    f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
    opt = TestOptions().parse()
    opt.num_threads = 0
    opt.batch_size = 1
    opt.serial_batches = True  
    opt.no_flip = True
    opt.display_id = -1
    return opt


@app.route('/process', methods=['POST'])
def processImage():
    # Pre-processing
    if (path.exists('results')):
        shutil.rmtree('results')
    if (path.exists('datasets')):
        shutil.rmtree('datasets')
    os.mkdir('datasets')
    opt = uploadFile()  
    dataset = create_dataset(opt)
    model = create_model(opt) 
    model.setup(opt)
    # create a website
    web_dir = os.path.join(opt.results_dir, opt.name, '{}_{}'.format(opt.phase, opt.epoch))  # define the website directory
    if opt.load_iter > 0:  # load_iter is 0 by default
        web_dir = '{:s}_iter{:d}'.format(web_dir, opt.load_iter)
    print('creating web directory', web_dir)
    webpage = html.HTML(web_dir, 'Experiment = %s, Phase = %s, Epoch = %s' % (opt.name, opt.phase, opt.epoch))
    if opt.eval:
        model.eval()
    
    for i, data in enumerate(dataset):
        if i >= opt.num_test:  # only apply our model to opt.num_test images.
            break
        model.set_input(data)  # unpack data from data loader
        model.test()           # run inference
        visuals = model.get_current_visuals()  # get image results
        img_path = model.get_image_paths()     # get image paths
        print('processing (%04d)-th image... %s' % (i, img_path))
        save_images(webpage, visuals, img_path, aspect_ratio=opt.aspect_ratio, width=opt.display_winsize)
    with open("results/braces2teeth/test_latest/images/" + fileName + "_fake.png", "rb") as img_file:
        my_string = base64.b64encode(img_file.read())
    return my_string


@app.route('/processvideo', methods=['POST'])
def processVideo():
    # preprocess
    if (path.exists('results')):
        shutil.rmtree('results', ignore_errors=True)
    if (path.exists('datasets')):
        shutil.rmtree('datasets', ignore_errors=True)
    os.makedirs('datasets/test')
    opt = uploadFile()

    # extract video
    video = video2Images('datasets/' + fileName + '.mp4', 'datasets/test')
    centeringAndSave('datasets/test')
    resizeAllFile('datasets/test')
    duplicate('datasets/test')
    # process
    # opt.dataroot = 'datasets/test'
    dataset = create_dataset(opt)
    model = create_model(opt) 
    model.setup(opt)
    # create a website
    web_dir = os.path.join(opt.results_dir, opt.name, '{}_{}'.format(opt.phase, opt.epoch))  # define the website directory
    if opt.load_iter > 0:  # load_iter is 0 by default
        web_dir = '{:s}_iter{:d}'.format(web_dir, opt.load_iter)
    print('creating web directory', web_dir)
    webpage = html.HTML(web_dir, 'Experiment = %s, Phase = %s, Epoch = %s' % (opt.name, opt.phase, opt.epoch))
    if opt.eval:
        model.eval()
    
    for i, data in enumerate(dataset):
        if i >= opt.num_test:  # only apply our model to opt.num_test images.
            break
        model.set_input(data)  # unpack data from data loader
        model.test()           # run inference
        visuals = model.get_current_visuals()  # get image results
        img_path = model.get_image_paths()     # get image paths
        print('processing (%04d)-th image... %s' % (i, img_path))
        save_images(webpage, visuals, img_path, aspect_ratio=opt.aspect_ratio, width=opt.display_winsize)
    
    # concat each pair image
    concatPairImage('results/braces2teeth/test_latest/images/', 'results')
    images2Video('results/concat', 30, fileName)
    return "Hello"

@app.route('/processvideo', methods=['GET'])
def getVideo():
    """Download a file."""
    
    return send_from_directory('', 'video.mp4', as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='6868')