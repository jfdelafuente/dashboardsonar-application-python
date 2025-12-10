enviarSeleccion();

function enviarSeleccion() {
  // Obtener el valor seleccionado
  var proyecto = document.getElementById("postId").value;
  console.log("Seleccion : " + proyecto);
  // console.log("Repositorio : " + repo);

  // Enviar la selección a la API
  enviarAPI(proyecto);
}

async function enviarAPI(seleccion) {
  var urlAPI = "http://localhost:5000/api/daily/by_proveedor/" + seleccion
  console.log("url : " +urlAPI);
  const response = await fetch(urlAPI);
  const data = await response.json();
  console.log("data: " +data);

  new Chart(document.getElementById("codesmellsBarChart"), {
    type: "bar",
    data: {
      labels: data.fecha,
      datasets: [{
        label: "# Code Smells",
        backgroundColor: "rgba(2,117,216,1)",
        borderColor: "rgba(2,117,216,1)",
        data: data.codesmells,
      }],
    },
    options: {
      legend: { display: false },
      title: {
        display: false,
        text: "# Code Smells",
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