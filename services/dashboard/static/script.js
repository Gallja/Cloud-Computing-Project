const eventSource = new EventSource("/stream");
const grid = document.getElementById("dashboard-grid");

eventSource.onmessage = function (event) {
    const data = JSON.parse(event.data);
    updateOrCreateCard(data);
};

function updateOrCreateCard(data) {
    const cardId = "card-" + data.city.replace(/\s+/g, '');
    let card = document.getElementById(cardId);

    const timeIcon = data.is_day === 1 ? "Giorno" : "Notte";

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
                        <span class="label">Temperatura</span>
                        <span class="value temp">${data.temperature}°C</span>
                    </div>
                    <div class="metric">
                        <span class="label">Vento</span>
                        <span class="value wind">${data.windspeed} km/h</span>
                    </div>
                    <div class="metric code">
                        <span class="label">Codice Meteo:</span> ${data.weathercode}
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
            alert("Stress test avviato.");
        })
        .catch(error => console.error('Errore:', error));
}