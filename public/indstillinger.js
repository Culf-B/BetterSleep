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

async function setCurrentAlarmTimes() {
    response = await fetch("/alarmData");
    json = await response.json();
    
    // Get inputs by id and set their value to the currently selected alarm times
    document.getElementById("time1").value = json.morningTime;
    document.getElementById("time2").value = json.nightTime;
}

setInterval(updateClocks, 1000);