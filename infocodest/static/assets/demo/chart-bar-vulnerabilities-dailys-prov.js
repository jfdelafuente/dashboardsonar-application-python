enviarSeleccion();

function enviarSeleccion() {
  // Obtener el valor seleccionado
  var proyecto = document.getElementById("postId").value;
  console.log("Seleccion : " + proyecto)

  // Enviar la selección a la API
  enviarAPI(proyecto);
}

async function enviarAPI(seleccion) {
  var urlAPI = "http://localhost:5000/api/daily/by_proveedor/" + seleccion
  console.log("url : " +urlAPI);
  const response = await fetch(urlAPI);
  const data = await response.json();
  console.log(data);
  labels = data.fecha;
  values = data.vulnerabilities;

  new Chart(document.getElementById("vulnerabilitiesBarChart"), {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "# Vulnerabilities",
        backgroundColor: "rgba(2,117,216,1)",
        borderColor: "rgba(2,117,216,1)",
        data: values,
      }],
    },
    options: {
      legend: { display: false },
      title: {
        display: false,
        text: "# Vulnerabilities",
      },
      scales: {
        xAxes: [
          {
            time: {
              unit: "date",
              
            },
            gridLines: {
              display: false,
            },
            ticks: {
              maxTicksLimit: 20,
            },
          },
        ],
        yAxes: [
          {
            ticks: {
              beginAtZero: true,
            },
            gridLines: {
              color: "rgba(0, 0, 0, .125)",
            },
          },
        ],
      },
    }
  });
}