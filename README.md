# Neuron.eye
Process the wave

Neuron is based on eye tracking technology written in javascript. It will continously recalibrate through mouse clicks and after the video is over it will create a heatmap of where the sight was focused. 

## How to Run
```sh
# Clone the repository and download NodeJS
# Move into the eye_tracking_website directory and download the additional dependencies
cd eye_tracking_website
npm install
# Run the webpage index.html as a server
browser-sync start --server --files "*"
```
