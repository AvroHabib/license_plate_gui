# Bengali_License_Plate_Recognition
Full YOLOv8 based Bangladeshi Vehicle License Plate Recognition.


## Demo
[![Watch the video demonstration]](https://drive.google.com/file/d/1H8pPJruDS8Gm2Uxu-_MeRnzxKP7c8qVX/view?usp=drive_link)


<p align="center">
  <img src="assets/v1.gif" alt="License Plate Detection Demo">
  <br>
  <em>demo.gif</em>
</p>



## Overview

This project aims to achieve real-time license plate detection and is designed for implementation on NVIDIA Jetson platforms. 

The pipeline integrates two specialized models: one for license plate detection and another for character recognition from the extracted license plate.


This Bangla LPDB - A dataset is of two parts-

1. Bangladeshi vehicle images with visible Bangla license plates which includes 1928 images.

2. Cropped Bangla license plate which includes 2662 images (720 synthetic images, 1942 images manually cropped from part-1).

 

Each image also contains its corresponding annotated text file in YOLO format. For Part-1 and Part-2, number of classes are 1 and 102, respectively.


Dataset link: [Bangla LPDB-A](https://zenodo.org/records/4718238)




## Training and Validation
### Detection Model
| Confusion Matrix | F1 Curve | Validation-Labels | Validation-Predictions |
|:----------------:|:--------:|:----------------:|:---------------:|
| ![Confusion Matrix](assets/detection/conf.png) | ![F1](assets/detection/f1.png) | ![Validation-Labels](assets/detection/val_batch2_labels.jpg) | ![Validation-Predictions ](assets/detection/val_batch2_pred.jpg) |


### OCR Model
| Confusion Matrix | F1 Curve | Validation-Labels | Validation-Predictions |
|:----------------:|:--------:|:----------------:|:---------------:|
| ![Confusion Matrix](assets/ocr/conf.png) | ![F1](assets/ocr/f1.png) | ![Validation-Labels](assets/ocr/val_batch2_labels.jpg) | ![Validation-Predictions ](assets/ocr/val_batch2_pred.jpg) |


## Project Structure 
Folders:<br>
model-m-detection : YoloV8-m model for detection.<br>
model-m-ocr : YoloV8-m model for OCR<br>

same goes for all the models.<br>

sample-images/videos for demonstration<br> 

.ipynb files are pretty much self explanatory.<br>

dataset-process-detection/ocr.ipynb files for transforming the raw dataset into Yolo specific folder structure.<br>


model-training.ipynb : Training for YoloV8-n/s/m<br>


detection/ocr-inference.ipynb : Doing inference on sample-images.<br>

real-time-inference.ipynb : Inference on recorded video file .mp4 .




## Citation

@dataset{ataher_sams_2021_4718238,
  author       = {Ataher Sams and
                  Homaira Huda Shomee},
  title        = {Bangla LPDB - A},
  month        = apr,
  year         = 2021,
  publisher    = {Zenodo},
  version      = {v1},
  doi          = {10.5281/zenodo.4718238},
  url          = {https://doi.org/10.5281/zenodo.4718238},
}
