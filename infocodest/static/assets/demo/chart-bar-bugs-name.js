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
  console.log("url : " +urlAPI);
  const response = await fetch(urlAPI);
  const data = await response.json();


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