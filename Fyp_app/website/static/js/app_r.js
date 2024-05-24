

// working code starts here
document.addEventListener('DOMContentLoaded', function() {
    var audioContext;
    var oscillator;
    var gainNode;
    var frequencies = [500, 1000, 2000, 3000, 4000, 6000, 8000];
    var currentFrequencyIndex = 0;
    var decibels = 0; // Starting decibels
    var isLeft = true;

    // function generateAudio(frequency, decibels) {
    //     audioContext = new (window.AudioContext || window.webkitAudioContext)();
    //     gainNode = audioContext.createGain();
    //     gainNode.gain.value = Math.pow(10, (decibels - 60) / 20); // Convert decibels to gain value

    //     oscillator = audioContext.createOscillator();
    //     oscillator.connect(gainNode);
    //     gainNode.connect(audioContext.destination);

    //     oscillator.type = 'sine';
    //     oscillator.frequency.value = frequency;
    //     oscillator.start();
    //     isPlaying = true;
    // }


    



    function generateAudio(frequency, decibels) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        gainNode = audioContext.createGain();
        pannerNode = audioContext.createStereoPanner(); // Create StereoPannerNode
        gainNode.gain.value = Math.pow(10, (decibels - 40) / 20); // Convert decibels to gain value

        oscillator = audioContext.createOscillator();
        oscillator.connect(gainNode);
        gainNode.connect(pannerNode); // Connect to pannerNode
        pannerNode.connect(audioContext.destination); // Connect pannerNode to destination

        oscillator.type = 'sine';
        oscillator.frequency.value = frequency;
        oscillator.start();
        isPlaying = true;

        // Set the stereo panning to play only in the right ear\
        pannerNode.pan.value = 1;
    }

    function playNextFrequency() {
        if (currentFrequencyIndex < frequencies.length) {
            var nextFrequency = frequencies[currentFrequencyIndex];
            decibels = 0;
            generateAudio(nextFrequency, decibels);
        } else {
            // All frequencies have been played
            isPlaying = false;
            alert("All frequencies tested press OK to go to Report");
            window.location.href = '/report';
        }
    }

    document.getElementById('startButton_R').addEventListener('click', function() {
        playNextFrequency();
        // Show the audio playing indicator
        document.querySelector('.audio-playing-indicator').style.display = 'block';
        // Hide the start button
        this.style.display = 'none';
        // Show the sound player controls
        document.getElementById('soundPlayer').style.display = 'block';
        // Show notification
        document.getElementById('notification').style.display = 'block';
        // Hide the continue button        
    });
// can hear is stopbutton
    document.getElementById('stopButton_R').addEventListener('click', function() {
        if (isPlaying) {
            oscillator.stop();
            isPlaying = false; // Set isPlaying to false when audio is stopped
        }     
          
        
        // Send frequency and decibel to the database
        var currentFrequency = frequencies[currentFrequencyIndex];

        var data = {
            frequency: currentFrequency,
            decibels: decibels
        };
    
        fetch('/add_audiogram_R', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Failed to add audiogram');
            }
        })
        .then(data => {
            console.log(data.message);
            currentFrequencyIndex++ ;

            playNextFrequency();
        })
        .catch(error => {
            console.error('Error:', error);
        });
        // Here you should send the data to the database using an appropriate method (e.g., AJAX)
        console.log("Frequency:", currentFrequency, "Decibels:", decibels);
        // Play the next frequency
        // playNextFrequency();
        
    });

    document.getElementById('cannotHearButton_R').addEventListener('click', function() {
            // Increment decibels by 10 for the same frequency
        decibels += 10;
            // Log the updated decibels
        console.log("Decibels increased to:", decibels, frequencies[currentFrequencyIndex]);
                
            // Play the audio again with the updated decibel level
        generateAudio(frequencies[currentFrequencyIndex], decibels);
    });
            
    document.getElementById('exitButton_R').addEventListener('click', function() {
        if (isPlaying) {
            oscillator.stop(); // Stop the oscillator if it's playing
            isPlaying = false;
        }
        if (audioContext) {
            audioContext.close(); // Close the audio context
        }
    
        // Reload the page
        history.go(0);

        // window.location.href = '/report';
    });
});
// ////////////ends here//////////////





