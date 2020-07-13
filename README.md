# Neuron

##  Queue Local Dev

  * Configure venv with python version `3.6`
  * `pip install -r requirements.txt`
  * `python main.py`


## neuron.eye_tracking_website

Neuron.eye is based on eye tracking technology written in javascript. It will continously recalibrate through mouse clicks and after the video is over it will create a heatmap of where the sight was focused. 

### INSTRUCTIONS:
```sh
# Clone the repository and download NodeJS
# Move into the eye_tracking_website directory and download the additional dependencies
cd eye_tracking_website
npm install
# Run the webpage index.html as a server
browser-sync start --server --files "*"
```

## neuron.eeg_ml_models
This is where the finished ML models go. 


### INSTRUCTIONS:

* Download model weight files at: https://drive.google.com/drive/u/0/folders/1aXD-mZDYMStIAuHFQOLF6Ug7m5F_zbMi
* Place eeg_net.pth inside focus_model folder
* Place nc_deap_eeg_net3.pth inside emotion_model folder

```sh
$ python3
>> from final_classifier import Final_classifier
>> classifier = Final_classifier()
>> output = classifier.predict(X)

```
#### output
NumPy.Array of shape ([2, (X.shape[1]//128) - 15, 3])
* First Dimension represents attention=0 and emotion=1
* Second dimension representes number of samples: seconds of input - 15
* Third dimension representes the labels:
    * [[Drowsy, Un-focused, Focused]]
    * [[Valence, Arousal, Dominance]]
