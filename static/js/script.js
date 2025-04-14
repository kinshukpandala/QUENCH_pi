// ====================
// THEME TOGGLE
// ====================
const toggle = document.getElementById("themeToggle");
const html = document.documentElement;

// Apply saved theme on load
const savedTheme = localStorage.getItem("theme") || "light";
html.setAttribute("data-theme", savedTheme);

// Toggle theme on button click
toggle.addEventListener("click", () => {
    const current = html.getAttribute("data-theme");
    const newTheme = current === "light" ? "dark" : "light";
    html.setAttribute("data-theme", newTheme);
    localStorage.setItem("theme", newTheme);
});

// ====================
// DATE & TIME DISPLAY
// ====================
function updateTime() {
    const now = new Date();
    const formatted = now.toLocaleString('en-GB', {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: true
    });
    const datetimeElement = document.getElementById("datetime");
    if (datetimeElement) {
        datetimeElement.textContent = formatted;
    }
}
setInterval(updateTime, 1000);
updateTime();

// ====================
// PAGE LOAD TRANSITION
// ====================
window.addEventListener("DOMContentLoaded", () => {
    document.body.classList.add("fade-in");
});

// ====================
// ANALYTICS CHART
// ====================
const analyticsChartCanvas = document.getElementById('analyticsChart').getContext('2d');
let analyticsChart;

const filterButtons = document.querySelectorAll('.filter-btn');
let currentRange = '1D';

function generateDummyData(range) {
    const today = new Date();
    let days = 0;
    switch (range) {
        case '1D': days = 1; break;
        case '3D': days = 3; break;
        case '5D': days = 5; break;
        case '7D': days = 7; break;
        case '9D': days = 9; break;
        default: days = 5;
    }

    const data = [];
    for (let i = days - 1; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(today.getDate() - i);
        const formattedDate = date.toISOString().slice(0, 10);
        data.push({
            date: formattedDate,
            revenue: Math.floor(Math.random() * 100) + 20,
            volume: (Math.random() * 5).toFixed(1)
        });
    }
    return data;
}

function updateAnalyticsChart(data) {
    const labels = data.map(d => d.date);
    const revenueData = data.map(d => d.revenue);
    const volumeData = data.map(d => d.volume);

    if (analyticsChart) {
        analyticsChart.destroy();
    }

    analyticsChart = new Chart(analyticsChartCanvas, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Revenue (₹)',
                    data: revenueData,
                    backgroundColor: 'rgba(128, 0, 255, 0.7)',
                    borderColor: 'rgba(128, 0, 255, 1)',
                    borderWidth: 1,
                    yAxisID: 'y-revenue',
                    barThickness: 15,
                    categoryPercentage: 0.7,
                    barPercentage: 0.45
                },
                {
                    label: 'Water Dispensed (Liters)',
                    data: volumeData,
                    backgroundColor: 'rgba(0, 199, 162, 0.7)',
                    borderColor: 'rgba(0, 199, 162, 1)',
                    borderWidth: 1,
                    yAxisID: 'y-volume',
                    barThickness: 15,
                    categoryPercentage: 0.7,
                    barPercentage: 0.45
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                'y-revenue': {
                    type: 'linear',
                    position: 'left',
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Revenue (₹)',
                        font: {
                            size: 12
                        }
                    },
                    ticks: {
                        font: {
                            size: 10
                        }
                    }
                },
                'y-volume': {
                    type: 'linear',
                    position: 'right',
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Water Dispensed (Liters)',
                        font: {
                            size: 12
                        }
                    },
                    grid: {
                        drawOnChartArea: false
                    },
                    ticks: {
                        callback: function (value) {
                            return value + 'L';
                        },
                        font: {
                            size: 10
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 10
                        },
                        align: 'center'
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    align: 'center',
                    labels: {
                        font: {
                            size: 11
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            let label = context.dataset.label || '';
                            if (context.parsed.y !== null) {
                                label += ': ' + context.parsed.y;
                                if (context.dataset.yAxisID === 'y-volume') {
                                    label += 'L';
                                }
                            }
                            return label;
                        },
                        titleFont: {
                            size: 12
                        },
                        bodyFont: {
                            size: 11
                        }
                    }
                }
            },
            layout: {
                padding: {
                    left: 20,
                    right: 20
                }
            }
        }
    });
}

updateAnalyticsChart(generateDummyData(currentRange));

filterButtons.forEach(button => {
    button.addEventListener('click', function () {
        const range = this.getAttribute('data-range');
        if (range !== currentRange) {
            currentRange = range;
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            const newData = generateDummyData(currentRange);
            updateAnalyticsChart(newData);
        }
    });
});

// Function to fetch system health data from the server
async function updateSystemHealth() {
    try {
        const res = await fetch("/system");
        const data = await res.json();

        document.getElementById("espStatus").textContent = data.esp_status;
        document.getElementById("espStatus").style.color = data.esp_status === "Connected" ? "lime" : "red";
        document.getElementById("wifiStrength").textContent = data.wifi_strength;
        document.getElementById("temperature").textContent = `${data.cpu_temperature} °C`;

        const memPercent = (data.memory_used / data.memory_total) * 100;
        document.getElementById("memUsageBar").style.width = `${memPercent}%`;
        document.getElementById("memUsed").textContent = data.memory_used;
        document.getElementById("memTotal").textContent = data.memory_total;

    } catch (err) {
        console.error("Health fetch error:", err);
    }
}

setInterval(updateSystemHealth, 1000); // Refresh every 1s
updateSystemHealth(); // Initial load

// ====================
// 🚰 WATER LEVEL TRACKER
// ====================
