const eventSource = new EventSource("/stream");
const grid = document.getElementById("dashboard-grid");

eventSource.onmessage = function (event) {
    const data = JSON.parse(event.data);
    updateOrCreateCard(data);
};

function updateOrCreateCard(data) {
    const cardId = "card-" + data.city.replace(/\s+/g, '');
    let card = document.getElementById(cardId);

    const timeIcon = data.is_day === 1 ? "Day" : "Night";

    if (!card) {
        card = document.createElement("div");
        card.id = cardId;
        card.className = "weather-card";
        grid.appendChild(card);
    }

    card.innerHTML = `
                <div class="card-header">
                    <h2>${data.city}</h2>
                    <span class="time-icon">${timeIcon}</span>
                </div>
                <div class="card-body">
                    <div class="metric">
                        <span class="label">Temperature</span>
                        <span class="value temp">${data.temperature}°C</span>
                    </div>
                    <div class="metric">
                        <span class="label">Wind Speed</span>
                        <span class="value wind">${data.windspeed} km/h</span>
                    </div>
                    <div class="metric">
                        <span class="label">Precipitation</span>
                        <span class="value">${data.precipitation} mm</span>
                    </div>
                    <div class="metric">
                        <span class="label">Rain</span>
                        <span class="value">${data.rain} mm</span>
                    </div>
                    <div class="metric">
                        <span class="label">Cloud Cover</span>
                        <span class="value">${data.cloud_cover} %</span>
                    </div>
                    <div class="metric">
                        <span class="label">Surface Pressure</span>
                        <span class="value">${data.surface_pressure} hPa</span>
                    </div>
                    <div class="metric">
                        <span class="label">Sunshine Duration</span>
                        <span class="value">${data.sunshine_duration} s</span>
                    </div>
                </div>
            `;

    card.classList.add("flash-update");
    setTimeout(() => {
        card.classList.remove("flash-update");
    }, 300);
}

function startStressTest() {
    fetch('/admin/stress', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            console.log(data.status);
            alert("Stress test started.");
        })
        .catch(error => console.error('Error:', error));
}