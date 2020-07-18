# nc_face_emotion_model
A CNN based pytorch implementation on facial expression recognition (FER2013 and CK+), achieving 73.112% (state-of-the-art) in FER2013 and 94.64% in CK+ dataset

## Demos ##
![Image text](https://raw.githubusercontent.com/WuJie1010/Facial-Expression-Recognition.Pytorch/master/demo/1.png)


## Dependencies ##
- Python 3.6.2
- Pytorch >=0.2.0
- OpenCV
- h5py (Preprocessing)
- sklearn (plot confusion matrix)

## Use the model for Inference ##
- Firstly, download the pre-trained model from https://drive.google.com/drive/u/0/folders/1aXD-mZDYMStIAuHFQOLF6Ug7m5F_zbMi and then put it in the base folder; Next,

```
    from nc_face_emotion_model import Emotion_model
    model = Emotion_model()
    score, predicted = model.video_predictor("your_video.mp4")
```

## FER2013 Dataset (Used for Training) ##
- Dataset from https://www.kaggle.com/c/challenges-in-representation-learning-facial-expression-recognition-challenge/data
Image Properties: 48 x 48 pixels (2304 bytes)
labels: 0=Angry, 1=Disgust, 2=Fear, 3=Happy, 4=Sad, 5=Surprise, 6=Neutral
The training set consists of 28,709 examples. The public test set consists of 3,589 examples. The private test set consists of another 3,589 examples.


###              fer2013 Accurary             ###

- Model：    VGG19 ;       PublicTest_acc：  71.496% ;     PrivateTest_acc：73.112%     <Br/>
- Model：   Resnet18 ;     PublicTest_acc：  71.190% ;    PrivateTest_acc：72.973%     

###      CK+ Accurary      ###
- Model：    VGG19 ;       Test_acc：   94.646%   <Br/>
- Model：   Resnet18 ;     Test_acc：   94.040%   

