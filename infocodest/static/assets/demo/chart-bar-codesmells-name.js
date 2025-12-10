enviarSeleccion();

function enviarSeleccion() {
  // Obtener el valor seleccionado
  var proyecto = document.getElementById("postId").value;
  var repo = document.getElementById("nameId").value;
  // console.log("Seleccion : " + proyecto)
  // console.log("Repositorio : " + repo);

  // Enviar la selección a la API
  enviarAPI(proyecto, repo);
}

async function enviarAPI(seleccion, name) {
  var urlAPI = "http://localhost:5000/api/aplicacion/" + seleccion +"/" + name
  // console.log("url : " +urlAPI);
  const response = await fetch(urlAPI);
    const data = await response.json();
    // console.log(data);
    labels = data.fecha;
    values = data.codesmells;

  new Chart(document.getElementById("codesmellsBarChart"), {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "# Code Smells",
        backgroundColor: "rgba(2,117,216,1)",
        borderColor: "rgba(2,117,216,1)",
        data: values,
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