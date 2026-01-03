// dashboard/static/script.js
let analyticsChart = null;
let heatmapChart = null;
let lastAlerts = [];

function updateDashboard(data) {
    // Update total count
    document.getElementById('total-count').innerText = data.total || 0;

    // Update zone count boxes
    const container = document.getElementById('zones-container');
    container.innerHTML = '';
    const colors = ['zone1', 'zone2', 'zone3', 'zone4'];

    const zoneIds = Object.keys(data.zones || {}).sort((a, b) => a - b);
    zoneIds.forEach((id, i) => {
        const count = data.zones[id] || 0;
        const div = document.createElement('div');
        div.className = 'col-md-3 mb-4';
        div.innerHTML = `
            <div class="zone-box ${colors[i % 4]} shadow-lg">
                <h4>Zone ${id} Count</h4>
                <h2>${count.toString().padStart(2, '0')}</h2>
            </div>`;
        container.appendChild(div);
    });

    // Update Line Chart
    const lineCtx = document.getElementById('analyticsChart').getContext('2d');
    if (analyticsChart) analyticsChart.destroy();

    analyticsChart = new Chart(lineCtx, {
        type: 'line',
        data: {
            labels: data.history.map(entry => entry.time),
            datasets: zoneIds.map((id, i) => ({
                label: `Zone ${id}`,
                data: data.history.map(entry => entry.zones[id] || 0),
                borderColor: ['#007bff', '#fd7e14', '#28a745', '#6f42c1'][i % 4],
                backgroundColor: ['#007bff40', '#fd7e1440', '#28a74540', '#6f42c140'][i % 4],
                tension: 0.4,
                fill: true
            }))
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'top' },
                title: { display: true, text: 'Real Time Crowd Analytics Over Time' }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    // Update Bubble Heatmap
    const bubbleCtx = document.getElementById('heatmapChart').getContext('2d');
    if (heatmapChart) heatmapChart.destroy();

    heatmapChart = new Chart(bubbleCtx, {
        type: 'bubble',
        data: {
            datasets: zoneIds.map((id, i) => ({
                label: `Zone ${id}`,
                data: [{
                    x: i + 1,
                    y: 3,
                    r: Math.max(15, (data.zones[id] || 0) * 4)  // Bigger bubble = more people
                }],
                backgroundColor: ['#007bff', '#fd7e14', '#28a745', '#6f42c1'][i % 4] + 'CC'
            }))
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'top' },
                title: { display: true, text: 'Crowd Density Heatmap' }
            },
            scales: {
                x: { display: false },
                y: { display: false }
            }
        }
    });

    // Alert system
    const alerts = data.alerts || [];
    const alertBox = document.getElementById('alert-box');
    const alertZones = document.getElementById('alert-zones');

    if (alerts.length > 0) {
        alertZones.textContent = alerts.map(z => `Zone ${z}`).join(', ');
        alertBox.classList.remove('d-none');
        // Play beep only on new alert
        if (JSON.stringify(alerts.sort()) !== JSON.stringify(lastAlerts.sort())) {
            document.getElementById('alert-sound').play();
        }
    } else {
        alertBox.classList.add('d-none');
    }
    lastAlerts = alerts.slice();
}

// Fetch data every second
setInterval(() => {
    fetch('/data')
        .then(response => response.json())
        .then(data => updateDashboard(data))
        .catch(err => console.error('Error fetching data:', err));
}, 1000);

// Admin Functions
function setThreshold() {
    const val = parseInt(document.getElementById('global-threshold').value) || 20;
    fetch('/set_threshold', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ threshold: val })
    }).then(() => alert('Threshold updated!'));
}

function changeCamera() {
    const src = document.getElementById('camera-source').value.trim();
    fetch('/admin/change_camera', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source: src || 0 })
    }).then(() => alert('Camera source updated!'));
}

function viewUsers() {
    fetch('/admin/users')
        .then(r => r.json())
        .then(users => {
            if (users.error) {
                alert(users.error);
                return;
            }
            const list = users.map(u => `${u.username} (${u.role})`).join('\n');
            alert("Registered Users:\n\n" + (list || "No users yet"));
        });
}

function exportPDF() {
    fetch('/export_pdf')
        .then(r => r.json())
        .then(d => {
            if (d.filename) {
                window.location = `/download/${d.filename}`;
            } else {
                alert("No data to export");
            }
        });
}

document.getElementById('export-btn').onclick = () => {
    fetch('/export_csv')
        .then(r => r.json())
        .then(d => {
            if (d.filename) {
                window.location = `/download/${d.filename}`;
            }
        });
};



