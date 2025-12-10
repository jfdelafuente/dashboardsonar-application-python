// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#292b2c';

getData();
async function getData() {
  const response = await fetch(
    "http://localhost:5000/api/charts_data"
  );
  const data = await response.json();
  console.log(data);
  labels = data.labels;
  values = data.values;

  new Chart(document.getElementById("myBarChart"), {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Repositorios",
        backgroundColor: "rgba(2,117,216,1)",
        borderColor: "rgba(2,117,216,1)",
        data: values,
      }],
    },
    options: {
      scales: {
        xAxes: [{
          time: {
            unit: 'month'
          },
          gridLines: {
            display: false
          }
        }],
        yAxes: [{
          ticks: {
            min: 0,
            max: 10
          },
          gridLines: {
            display: true
          }
        }],
      },
      legend: { display: false },
      title: {
        display: false,
        text: "Proyectos",
      },
    }
  });
}