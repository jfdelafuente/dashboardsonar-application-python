// Set new default font family and font color to mimic Bootstrap's default styling
// Chart.defaults.global.defaultFontFamily = '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
// Chart.defaults.global.defaultFontColor = "#292b2c";

enviarSeleccion();

function enviarSeleccion() {
  enviarAPI();
}

async function enviarAPI() {
  var urlAPI = "http://localhost:5000/api/registro?limit=30";
  const response = await fetch(urlAPI);
  const data_json = await response.json();
  labels = data_json.map((row) => row.created_on);
  // values = data.map(row => row.num_app);

  const fechasFormateadas = labels.map(fecha => {
    const date = new Date(fecha);
    return `${('0' + date.getDate()).slice(-2)}-${('0' + (date.getMonth() + 1)).slice(-2)}-${date.getFullYear()}`;
  });

  const data = {
    labels: fechasFormateadas,
    datasets: [
      {
        label: "aplicaciones",
        type: "bar",
        lineTension: 0.3,
        backgroundColor: "rgba(245, 40, 145, 0.2)",
        borderColor: "rgba(245, 40, 145,1)",
        pointRadius: 5,
        pointBackgroundColor: "rgba(245, 40, 145, 1)",
        pointBorderColor: "rgba(255,255,255,0.8)",
        pointHoverRadius: 5,
        pointHoverBackgroundColor: "rgba(245, 40, 145,1)",
        pointHitRadius: 50,
        pointBorderWidth: 2,
        data: data_json.map((row) => row.num_app),
        yAxisID: "y_l",
      },
      {
        label: "repositorios",
        type: "bar",
        lineTension: 0.3,
        backgroundColor: "rgba(22,117,216,0.2)",
        borderColor: "rgba(12,117,216,1)",
        pointRadius: 5,
        pointBackgroundColor: "rgba(22,117,216,1)",
        pointBorderColor: "rgba(255,255,255,0.8)",
        pointHoverRadius: 5,
        pointHoverBackgroundColor: "rgba(22,117,216,1)",
        pointHitRadius: 50,
        pointBorderWidth: 2,
        data: data_json.map((row) => row.num_repo),
        yAxisID: "y_l",
      },
      {
        label: "quality",
        type: "line",
        lineTension: 0.3,
        backgroundColor: "rgba(244, 175, 27, 0.2)",
        borderColor: "rgba(244, 175, 27, 1)",
        pointRadius: 5,
        pointBackgroundColor: "rgba(244, 175, 27, 1)",
        pointBorderColor: "rgba(255,255,255,0.8)",
        pointHoverRadius: 5,
        pointHoverBackgroundColor: "rgba(244, 175, 27, 1)",
        pointHitRadius: 50,
        pointBorderWidth: 2,
        data: data_json.map((row) => row.num_quality),
        yAxisID: "y_r",
      },
      {
        label: "bugs",
        lineTension: 0.3,
        backgroundColor: "rgba(69,177,223,0.2)",
        borderColor: "rgba(69,177,223,1)",
        pointRadius: 5,
        pointBackgroundColor: "rgba(69,177,223,1)",
        pointBorderColor: "rgba(255,255,255,0.8)",
        pointHoverRadius: 5,
        pointHoverBackgroundColor: "rgba(69,177,223,1)",
        pointHitRadius: 50,
        pointBorderWidth: 2,
        data: data_json.map((row) => row.num_bugs),
        yAxisID: "y_r",
      },
      {
        label: "analisis",
        lineTension: 0.3,
        backgroundColor: "rgba(99,201,122,0.2)",
        borderColor: "rgba(99,201,122,1)",
        pointRadius: 5,
        pointBackgroundColor: "rgba(99,201,122,1)",
        pointBorderColor: "rgba(255,255,255,0.8)",
        pointHoverRadius: 5,
        pointHoverBackgroundColor: "rgba(99,201,122,1)",
        pointHitRadius: 50,
        pointBorderWidth: 2,
        data: data_json.map((row) => row.num_analisis),
        yAxisID: "y_r",
      },
    ],
  };

  const options = {
    responsive: true,
    interaction: {
      mode: "index",
      intersect: false,
    },
    stacked: false,
    scales: {
      x: {
        time: {
          unit: "date",
          displayFormats: {
            quarter: 'MMM YYYY'
          },
        },
      },
      y_l: {
        type: "linear",
        display: true,
        position: "left",
      },
      y_r: {
        type: "linear",
        display: true,
        position: "right",
        grid: {
          drawOnChartArea: false, // only want the grid lines for one axis to show up
        },
        min: 10000,
      },
    },
  };

  // Area Chart Example
  var ctx = document.getElementById("myAreaChart");
  var myLineChart = new Chart(ctx, {
    type: "line",
    data: data,
    options: options,
  });
  console.log(myLineChart.data);
}
