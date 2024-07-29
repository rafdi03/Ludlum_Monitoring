const ctx = document.getElementById('sensorChart').getContext('2d');
const sensorData = {
    labels: [],
    datasets: [{
        label: 'Laju Dosis µSv/jam',
        data: [],
        fill: false,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
    }]
};

const config = {
    type: 'line',
    data: sensorData,
    options: {
        scales: {
            y: {
                beginAtZero: true
            }
        },
        plugins: {
            zoom: {
                pan: {
                    enabled: true,
                    mode: 'x',
                    speed: 10,
                    threshold: 10,
                },
                zoom: {
                    wheel: {
                        enabled: true,
                    },
                    pinch: {
                        enabled: true
                    },
                    mode: 'x',
                }
            }
        }
    }
};

const sensorChart = new Chart(ctx, config);

setInterval(function() {
    fetch('/data')
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to fetch data');
        }
        console.log("Data received from server.");
        return response.json();
    })
    .then(data => {
        if (data.error) {
            console.error('Server error:', data.error);
            document.getElementById('sensorStatus').innerHTML = 'Sensor tidak terbaca';
            return;
        }

        const now = new Date();
        const timeString = `${now.getHours()}:${now.getMinutes()}:${now.getSeconds()}`;
        const currentDateTime = now.toLocaleString();

        if (sensorData.labels.length > 20) {
            sensorData.labels.shift();
            sensorData.datasets[0].data.shift();
        }
        sensorData.labels.push(timeString);
        sensorData.datasets[0].data.push(data.value);
        sensorChart.update();

        let statusText, indicatorClass;
        if (data.value < 8) {
            statusText = 'AMAN';
            indicatorClass = 'lamp safe';
        } else if (data.value >= 8 && data.value <= 10) {
            statusText = 'ALERT';
            indicatorClass = 'lamp alert';
        } else {
            statusText = 'BAHAYA';
            indicatorClass = 'lamp danger';
        }

        document.getElementById('sensorStatus').innerHTML = `
            Sensor Value: ${data.value} µSv/jam<br>
            Current Time: ${currentDateTime}<br>
            Status: ${statusText}
        `;
        document.getElementById('indicator').className = indicatorClass;
    })
    .catch(error => {
        console.error('Error fetching data:', error);
        document.getElementById('sensorStatus').innerHTML = 'Sensor tidak terbaca';
    });

}, 5000);
