// Load DOM elements
const autoTimeInput = document.getElementById('autoTime');

// Autoupdate clocks
function updateClocks() {
    const now = new Date();
    const hours = ('0' + now.getHours()).slice(-2);
    const minutes = ('0' + now.getMinutes()).slice(-2);

    const time = `${hours}:${minutes}`;

    // Form update input time if it is set to autoupdate
    autoTimeInput.value = time;
    
    // Form update describtion text time
    document.getElementById("manualTimeDescription").innerHTML = `Passer urets tid ikke? Opdater tiden automatisk til ${time} eller indstil den manuelt.`
}

function setCurrentAlarmTimes() {
    fetch("/alarmData")
        .then((response) => {response.json()})
        .then((json) => console.log(json))
}

setInterval(updateClocks, 1000);