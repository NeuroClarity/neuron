

window.onload = function() {

    webgazer.setRegression('ridge') //different regression modules can be used.. Refer documentation

    //////////// TEST //////////////
    var test = document.getElementById("title");
    test.innerHTML = "<h2> Video Player Loaded </h2>";
    ///////////// END //////////////
    webgazer.setTracker('clmtrackr') //three trackers are available by default, refer documentation

    webgazer.setGazeListener(function(data, clock) {
        /* data: is an object containing an x and y key which are the x and y prediction coordinates (no bounds limiting) , clock: elapsed time in milliseconds since webgazer.begin() was called */
    }).begin().showPredictionPoints(true); /* shows a square every 100 milliseconds where current prediction is */


    var width = 320;
    var height = 240;
    var topDist = '0px';
    var leftDist = '0px';

    var setup = function() {

        var video = document.getElementById('video-player');
        video.style.display = 'block';
        video.style.position = 'absolute';
        video.style.top = topDist;
        video.style.left = leftDist;
        video.width = width;
        video.height = height;
        video.style.margin = "0px";

        //////////// TEST //////////////
        var test = document.getElementById("title");
        test.innerHTML = "<h2> Video Player Loaded </h2>";
        ///////////// END //////////////

        webgazer.params.imgWidth = width;
        webgazer.params.imgHeight = height;


        var overlay = document.createElement('canvas');

        overlay.id = 'overlay';
        overlay.style.position = 'absolute';
        overlay.width = width;
        overlay.height = height;
        overlay.style.top = topDist;
        overlay.style.left = leftDist;
        overlay.style.margin = '0px';

        var myCanvas=get('canvas');

        myCanvas.width=screen.width;
        myCanvas.height=screen.height;


        document.body.appendChild(overlay);

        var cl = webgazer.getTracker().clm;


        function drawLoop() {

            requestAnimFrame(drawLoop);
            overlay.getContext('2d').clearRect(0,0,width,height);

            if (cl.getCurrentPosition()) {
                cl.draw(overlay);
            }

        }

        drawLoop();

    };

    function checkIfReady() {
        //////////// TEST //////////////
        var test = document.getElementById("title");
        test.innerHTML = "<h2> Video Player Loaded </h2>";
        ///////////// END //////////////
        if (webgazer.isReady()) {
            setup();
        } else {
            setTimeout(checkIfReady, 100);
        }
    }

    checkIfReady()
    setTimeout(checkIfReady,100);

};    //The window.onload function which we started in step 3a ends here

window.onbeforeunload = function() {
    webgazer.end(); //Saves the data even if you reload the page.

}

/*Helper Function*/
function get(id) {
    return document.getElementById(id);
}


function stopTracking() {
    webgazer.end(); //Save Webgaze Data
    var dataset=JSON.parse(window.localStorage.webgazerGlobalData); //Read Data from Local Webstorage

    //create data in the form of “simpleheat” input
    var data=[];
    for(var i=0;i<dataset.data.length;i++) {
        data.push(dataset.data[i].screenPos);
    }

    //Hide the Video Overlay
    get('overlay').style.display='none';

    //Display The Heat Map
    get('canvas').style.display='block';
    generateHeatMap(data);
};


function generateHeatMap(data) {
    /*A heat map generator using “simpleheat.js” (https://github.com/mourner/simpleheat) to show your most viewed areas in a heatmap representation*/

    window.requestAnimationFrame= window.requestAnimationFrame||  window.mozRequestAnimationFrame|| window.webkitRequestAnimationFrame ||  window.msRequestAnimationFrame;
    var heat = simpleheat("canvas").data(data).max(18), frame;

    function draw() {
        console.time('draw');
        heat.draw();
        console.timeEnd('draw');
        frame = null;
    }

    draw();
}
