# EEG Analytics
This is where the finished ML models go. 

## INSTRUCTIONS:

### Getting the model
* Download model weight files at: https://drive.google.com/drive/u/0/folders/1aXD-mZDYMStIAuHFQOLF6Ug7m5F_zbMi
* Place eeg_net.pth inside focus_model folder
* Place nc_deap_eeg_net3.pth inside emotion_model folder

### Sample Usage
```sh
$ python3
>> from final_classifier import Final_classifier
>> classifier = Final_classifier()
>> output = classifier.predict(X)

```
### output
NumPy.Array of shape ([2, (X.shape[1]//128) - 15, 3])
* First Dimension represents attention=0 and emotion=1
* Second dimension representes number of samples: seconds of input - 15
* Third dimension representes the labels:
    * [[Drowsy, Un-focused, Focused]]
    * [[Valence, Arousal, Dominance]]
