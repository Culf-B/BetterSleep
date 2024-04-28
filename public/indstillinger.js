// Load DOM elements
const manualTimeBox = document.getElementById('manualTimeBox');
const manualTimeInput = document.getElementById('manualTime');

// Autoupdate clocks
function updateClocks() {
    const now = new Date();
    const hours = ('0' + now.getHours()).slice(-2);
    const minutes = ('0' + now.getMinutes()).slice(-2);

    const time = `${hours}:${minutes}`;

    // Form update input time if it is set to autoupdate
    if (manualTimeBox.checked == false) {
        manualTimeInput.value = time;
    }
    // Form update describtion text time
    document.getElementById("manualTimeDescription").innerHTML = `Passer urets tid ikke? Opdater tiden automatisk til ${time} eller indstil den manuelt.`
}
setInterval(updateClocks, 1000);

// Manual time form
manualTimeBox.checked = false;
manualTimeInput.disabled = true;

manualTimeBox.addEventListener('change', function() {
    if (manualTimeBox.checked) {
        manualTimeInput.disabled = false;
    } else {
        manualTimeInput.disabled = true;
    }
});