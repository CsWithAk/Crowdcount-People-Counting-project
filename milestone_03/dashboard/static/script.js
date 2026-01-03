const analyticsChart = new Chart(document.getElementById('analyticsChart'), {
    type: 'line',
    data: { labels: [], datasets: [] },
    options: { responsive: true, scales: { y: { beginAtZero: true } } }
});

const heatmapChart = new Chart(document.getElementById('heatmapChart'), {
    type: 'bubble',
    data: { datasets: [] },
    options: { responsive: true, scales: { x: { display: false }, y: { display: false } } }
});

const colors = ['#007bff', '#fd7e14', '#28a745', '#6f42c1'];
let lastAlerts = [];

function updateDashboard(data) {
    document.getElementById('total-count').textContent = data.total;
    document.getElementById('current-th').textContent = data.threshold;

    const container = document.getElementById('zones-container');
    container.innerHTML = '';
    
    Object.keys(data.zones).sort((a,b)=>a-b).forEach((zoneId, i) => {
        const count = data.zones[zoneId];
        const div = document.createElement('div');
        div.className = 'col-md-3';
        div.innerHTML = `<div class="zone-box ${'zone'+((i%4)+1)}">
            <h4>Zone ${zoneId} Count</h4>
            <h2>${count.toString().padStart(2,'0')}</h2>
        </div>`;
        container.appendChild(div);
    });

    const labels = data.history.map(h => h.time);
    analyticsChart.data.labels = labels;
    analyticsChart.data.datasets = Object.keys(data.zones).sort((a,b)=>a-b).map((id, i) => ({
        label: `Zone ${id}`,
        data: data.history.map(h => h.zones[id] || 0),
        borderColor: colors[i % 4],
        backgroundColor: colors[i % 4] + '40',
        tension: 0.3
    }));
    analyticsChart.update('none');

    heatmapChart.data.datasets = Object.keys(data.zones).sort((a,b)=>a-b).map((id, i) => ({
        label: `Zone ${id}`,
        data: [{ x: i+1, y: 3, r: Math.max(15, data.zones[id] * 3) }],
        backgroundColor: colors[i % 4]
    }));
    heatmapChart.update('none');

    const alerts = data.alerts || [];
    const alertBox = document.getElementById('alert-box');
    if (alerts.length > 0) {
        document.getElementById('alert-zones').textContent = alerts.map(z => `Zone ${z}`).join(', ');
        alertBox.classList.remove('d-none');
        if (JSON.stringify(alerts) !== JSON.stringify(lastAlerts)) {
            document.getElementById('alert-sound').play();
        }
    } else {
        alertBox.classList.add('d-none');
    }
    lastAlerts = alerts.slice();
}

document.getElementById('set-threshold-btn').onclick = () => {
    const val = document.getElementById('global-threshold').value;
    fetch('/set_threshold', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({threshold: parseInt(val)})
    });
};

document.getElementById('export-btn').onclick = () => {
    fetch('/export_csv').then(r => r.json()).then(d => {
        if (d.filename) window.location = `/download/${d.filename}`;
    });
};

setInterval(() => fetch('/data').then(r => r.json()).then(updateDashboard), 1000);