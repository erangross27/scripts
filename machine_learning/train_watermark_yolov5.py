"""
YOLOv5 Training Script

This script sets up and runs a training process for YOLOv5 object detection model.
It includes the following main components:

1. Importing necessary libraries and YOLOv5 modules
2. Defining hyperparameters for YOLOv5 training
3. Setting up command-line argument parsing for various training options
4. Creating a data.yaml file with dataset information
5. Initializing device and callbacks
6. Running the training process

The script is designed to be run from the command line with various optional arguments
to customize the training process. It uses a pre-defined set of hyperparameters and
allows for further customization through command-line options.

Usage:
    python script_name.py [arguments]

For a full list of available arguments, run:
    python script_name.py --help
"""

import torch
import yaml
from pathlib import Path
import argparse

# Import YOLOv5 repository
import sys
sys.path.append('/home/erangross/Downloads/yolov5')  # Adjust this path to where your YOLOv5 is located

from train import train # type: ignore
from utils.general import increment_path # type: ignore
from utils.torch_utils import select_device # type: ignore
from utils.callbacks import Callbacks # type: ignore


def main():
    """
    Main.
    """
    # Define hyperparameters for YOLOv5 training
    hyp = {
        'lr0': 0.01,  # Initial learning rate
        'lrf': 0.1,  # Final OneCycleLR learning rate (lr0 * lrf)
        'momentum': 0.937,  # SGD momentum/Adam beta1
        'weight_decay': 0.0005,  # Optimizer weight decay
        'warmup_epochs': 3.0,  # Warmup epochs
        'warmup_momentum': 0.8,  # Warmup initial momentum
        'warmup_bias_lr': 0.1,  # Warmup initial bias lr
        'box': 0.05,  # Box loss gain
        'cls': 0.5,  # Cls loss gain
        'cls_pw': 1.0,  # Cls BCELoss positive_weight
        'obj': 1.0,  # Obj loss gain (scale with pixels)
        'obj_pw': 1.0,  # Obj BCELoss positive_weight
        'iou_t': 0.20,  # IoU training threshold
        'anchor_t': 4.0,  # Anchor-multiple threshold
        'fl_gamma': 0.0,  # Focal loss gamma (efficientDet default gamma=1.5)
        'hsv_h': 0.015,  # Image HSV-Hue augmentation (fraction)
        'hsv_s': 0.7,  # Image HSV-Saturation augmentation (fraction)
        'hsv_v': 0.4,  # Image HSV-Value augmentation (fraction)
        'degrees': 0.0,  # Image rotation (+/- deg)
        'translate': 0.1,  # Image translation (+/- fraction)
        'scale': 0.5,  # Image scale (+/- gain)
        'shear': 0.0,  # Image shear (+/- deg)
        'perspective': 0.0,  # Image perspective (+/- fraction), range 0-0.001
        'flipud': 0.0,  # Image flip up-down (probability)
        'fliplr': 0.5,  # Image flip left-right (probability)
        'mosaic': 1.0,  # Image mosaic (probability)
        'mixup': 0.0,  # Image mixup (probability)
        'copy_paste': 0.0  # Segment copy-paste (probability)
    }

    # Define and parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', type=str, default='yolov5s.pt', help='initial weights path')
    parser.add_argument('--cfg', type=str, default='/home/erangross/Downloads/yolov5/models/yolov5s.yaml', help='model.yaml path')
    parser.add_argument('--data', type=str, default='/home/erangross/Downloads/organized_dataset/data.yaml', help='dataset.yaml path')
    parser.add_argument('--hyp', type=str, default=hyp, help='hyperparameters')
    parser.add_argument('--epochs', type=int, default=200)
    parser.add_argument('--batch-size', type=int, default=16, help='total batch size for all GPUs')
    parser.add_argument('--imgsz', '--img', '--img-size', type=int, default=640, help='train, val image size (pixels)')
    parser.add_argument('--rect', action='store_true', help='rectangular training')
    parser.add_argument('--resume', nargs='?', const=True, default=False, help='resume most recent training')
    parser.add_argument('--nosave', action='store_true', help='only save final checkpoint')
    parser.add_argument('--notest', action='store_true', help='only test final epoch')
    parser.add_argument('--noval', action='store_true', help='skip validation')
    parser.add_argument('--noautoanchor', action='store_true', help='disable autoanchor check')
    parser.add_argument('--evolve', action='store_true', help='evolve hyperparameters')
    parser.add_argument('--bucket', type=str, default='', help='gsutil bucket')
    parser.add_argument('--cache', type=str, nargs='?', const='ram', help='--cache images in "ram" (default) or "disk"')
    parser.add_argument('--image-weights', action='store_true', help='use weighted image selection for training')
    parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--multi-scale', action='store_true', help='vary img-size +/- 50%%')
    parser.add_argument('--single-cls', action='store_true', help='train multi-class data as single-class')
    parser.add_argument('--adam', action='store_true', help='use torch.optim.Adam() optimizer')
    parser.add_argument('--sync-bn', action='store_true', help='use SyncBatchNorm, only available in DDP mode')
    parser.add_argument('--local_rank', type=int, default=-1, help='DDP parameter, do not modify')
    parser.add_argument('--workers', type=int, default=8, help='maximum number of dataloader workers')
    parser.add_argument('--project', default='runs/train', help='save to project/name')
    parser.add_argument('--entity', default=None, help='W&B entity')
    parser.add_argument('--name', default='exp', help='save to project/name')
    parser.add_argument('--exist-ok', action='store_true', help='existing project/name ok, do not increment')
    parser.add_argument('--quad', action='store_true', help='quad dataloader')
    parser.add_argument('--linear-lr', action='store_true', help='linear LR')
    parser.add_argument('--label-smoothing', type=float, default=0.0, help='Label smoothing epsilon')
    parser.add_argument('--upload_dataset', action='store_true', help='Upload dataset as W&B artifact table')
    parser.add_argument('--bbox_interval', type=int, default=-1, help='Set bounding-box image logging interval for W&B')
    parser.add_argument('--save_period', type=int, default=-1, help='Log model after every "save_period" epoch')
    parser.add_argument('--artifact_alias', type=str, default="latest", help='version of dataset artifact to be used')
    parser.add_argument('--freeze', nargs='+', type=int, default=[0], help='Freeze layers: backbone=10, first3=0 1 2')
    parser.add_argument('--noplots', action='store_true', help='save no plot files')
    parser.add_argument('--seed', type=int, default=0, help='Global training seed')
    parser.add_argument('--optimizer', type=str, choices=['SGD', 'Adam', 'AdamW'], default='SGD', help='optimizer')
    parser.add_argument('--cos-lr', action='store_true', help='cosine LR scheduler')
    parser.add_argument('--patience', type=int, default=100, help='EarlyStopping patience (epochs without improvement)')
    opt = parser.parse_args()

    # Set save_dir
    opt.save_dir = str(increment_path(Path(opt.project) / opt.name, exist_ok=opt.exist_ok))

    # Create data.yaml file
    data_yaml = {
        'train': '/home/erangross/Downloads/organized_dataset/images/train',
        'val': '/home/erangross/Downloads/organized_dataset/images/val',
        'nc': 1,  # number of classes
        'names': ['watermark']  # class names
    }

    with open(opt.data, 'w') as f:
        yaml.dump(data_yaml, f)

    # Initialize
    device = select_device(opt.device)

    # Initialize callbacks
    callbacks = Callbacks()

    # Train
    train(hyp, opt, device, callbacks)

if __name__ == '__main__':
    main()
