"""General-purpose test script for image-to-image translation.

Once you have trained your model with train.py, you can use this script to test the model.
It will load a saved model from '--checkpoints_dir' and save the results to '--results_dir'.

It first creates model and dataset given the option. It will hard-code some parameters.
It then runs inference for '--num_test' images and save results to an HTML file.

Example (You need to train models first or download pre-trained models from our website):
    Test a CycleGAN model (both sides):
        python test.py --dataroot ./datasets/maps --name maps_cyclegan --model cycle_gan

    Test a CycleGAN model (one side only):
        python test.py --dataroot datasets/horse2zebra/testA --name horse2zebra_pretrained --model test --no_dropout

    The option '--model test' is used for generating CycleGAN results only for one side.
    This option will automatically set '--dataset_mode single', which only loads the images from one set.
    On the contrary, using '--model cycle_gan' requires loading and generating results in both directions,
    which is sometimes unnecessary. The results will be saved at ./results/.
    Use '--results_dir <directory_path_to_save_result>' to specify the results directory.

    Test a pix2pix model:
        python test.py --dataroot ./datasets/facades --name facades_pix2pix --model pix2pix --direction BtoA

See options/base_options.py and options/test_options.py for more test options.
See training and test tips at: https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix/blob/master/docs/tips.md
See frequently asked questions at: https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix/blob/master/docs/qa.md
"""
import os
from options.test_options import TestOptions
from data import create_dataset
from models import create_model
from util.visualizer import save_images
from util import html
import torch


if __name__ == '__main__':
    opt = TestOptions().parse()  # get test options
    # hard-code some parameters for test
    opt.num_threads = 0   # test code only supports num_threads = 1
    opt.batch_size = 1    # test code only supports batch_size = 1
    opt.serial_batches = True  # disable data shuffling; comment this line if results on randomly chosen images are needed.
    opt.no_flip = True    # no flip; comment this line if results on flipped images are needed.
    opt.display_id = -1   # no visdom display; the test code saves the results to a HTML file.
    dataset = create_dataset(opt)  # create a dataset given opt.dataset_mode and other options
    model = create_model(opt)      # create a model given opt.model and other options
    model.setup(opt)               # regular setup: load and print networks; create schedulers
    # create a website
    web_dir = os.path.join(opt.results_dir, opt.name, '{}_{}'.format(opt.phase, opt.epoch))  # define the website directory
    if opt.load_iter > 0:  # load_iter is 0 by default
        web_dir = '{:s}_iter{:d}'.format(web_dir, opt.load_iter)
    print('creating web directory', web_dir)
    webpage = html.HTML(web_dir, 'Experiment = %s, Phase = %s, Epoch = %s' % (opt.name, opt.phase, opt.epoch))
    # test with eval mode. This only affects layers like batchnorm and dropout.
    # For [pix2pix]: we use batchnorm and dropout in the original pix2pix. You can experiment it with and without eval() mode.
    # For [CycleGAN]: It should not affect CycleGAN as CycleGAN uses instancenorm without dropout.
    if opt.eval:
        model.eval()
    for i, data in enumerate(dataset):
        if i >= opt.num_test:  # only apply our model to opt.num_test images.
            break

        # print(data['A_paths'])
        # if "r00b8d4a2t" not in data['A_paths'][0]:
        #     continue
        if "r0c5e9567t" in data['A_paths'][0]:
            x = 962
            y = 2112
        elif "r15d1c836t" in data['A_paths'][0]:
            x = 512
            y = 1280
        elif "r00b8d4a2t" in data['A_paths'][0]:
            x = 1344
            y = 1160
        elif "r07db8a54t" in data['A_paths'][0]:
            x = 956
            y = 2588
        elif "r0279b17bt" in data['A_paths'][0]:
            x = 826
            y = 549
        elif "r00de2590t" in data['A_paths'][0]:
            x = 2042
            y = 1639
        else:
            continue

        cur_data = {
            'A': data['A'][:, :, x:x + 512, y:y + 512],
            'B': data['B'][:, :, x:x + 512, y:y + 512],
            'A_paths': data['A_paths'],
            'B_paths': data['B_paths'],
        }

        # bs, c, w, h = data['A'].shape
        # cs = opt.crop_size
        #
        # cur_data = {'A': data['A'][:, :, int(w / 2 - 256):int(w / 2 + 256), int(h / 2 - 256):int(h / 2 + 256)],
        #             'B': data['B'][:, :, int(w / 2 - 256):int(w / 2 + 256), int(h / 2 - 256):int(h / 2 + 256)],
        #             'A_paths': data['A_paths'], 'B_paths': data['B_paths']}

        # cur_data = {'A': data['A'][:, :, 1344:1344+512, 1160:1160+512], 'B': data['B'][:, :, 1344:1344+512, 1160:1160+512],
        #             'A_paths': data['A_paths'], 'B_paths': data['B_paths']}
        model.set_input(cur_data)  # unpack data from data loader
        model.test()  # run inference
        visuals = model.get_current_visuals()  # get image results

        # w = int((w // cs) * cs)
        # h = int((h // cs) * cs)
        # fake = torch.empty(bs, c, w, h)
        # for k in range(0, w, cs):
        #     for j in range(0, h, cs):
        #         cur_data = {'A': data['A'][:, :, k:k+cs, j:j+cs], 'B': data['B'][:, :, k:k+cs, j:j+cs],
        #                     'A_paths': data['A_paths'], 'B_paths': data['B_paths']}
        #         model.set_input(cur_data)  # unpack data from data loader
        #         model.test()  # run inference
        #         visuals = model.get_current_visuals()  # get image results
        #         fake[:, :, k:k+cs, j:j+cs] = visuals['fake_B'].detach().float().cpu()
        # visuals = {
        #     "real_A": data['B'],
        #     "real_B": data['A'],
        #     "fake_B": fake,
        # }
        # model.set_input(data)  # unpack data from data loader
        # model.test()           # run inference
        # visuals = model.get_current_visuals()  # get image results
        img_path = model.get_image_paths()     # get image paths
        if i % 5 == 0:  # save images to an HTML file
            print('processing (%04d)-th image... %s' % (i, img_path))
        save_images(webpage, visuals, img_path, aspect_ratio=opt.aspect_ratio, width=opt.display_winsize)
    webpage.save()  # save the HTML
