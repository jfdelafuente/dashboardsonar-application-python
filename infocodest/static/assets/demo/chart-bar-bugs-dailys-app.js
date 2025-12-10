enviarSeleccion();

function enviarSeleccion() {
  // Obtener el valor seleccionado
  var proyecto = document.getElementById("postId").value;
  console.log("Seleccion : " + proyecto)
  // console.log("Repositorio : " + repo);

  // Enviar la selección a la API
  enviarAPI(proyecto);
}

async function enviarAPI(seleccion) {
  var urlAPI = "http://localhost:5000/api/daily/" + seleccion
  console.log("url : " +urlAPI);
  const response = await fetch(urlAPI);
  const data = await response.json();
  console.log("data: " +data);

  new Chart(document.getElementById("bugsBarChart"), {
    type: "bar",
    data: {
      labels: data.fecha,
      datasets: [{
        label: "# Bugs",
        backgroundColor: "rgba(2,117,216,1)",
        borderColor: "rgba(2,117,216,1)",
        data: data.bugs,
      }],
    },
    options: {
      legend: { display: false },
      title: {
        display: false,
        text: "# Bugs",
      },
      scales: {
        xAxes: [
          {
            time: {
              unit: "time",
              displayFormats: {
                quarter: "DD MMM YYYY"
              },
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