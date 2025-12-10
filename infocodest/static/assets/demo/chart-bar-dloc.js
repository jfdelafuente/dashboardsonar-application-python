enviarSeleccion();

function enviarSeleccion() {
  // Obtener el valor seleccionado
  var proyecto = document.getElementById("postId").value;
  var repo = document.getElementById("nameId").value;
  console.log("Seleccion : " + proyecto)
  console.log("Repositorio : " + repo);

  // Enviar la selección a la API
  enviarAPI(proyecto, repo);
}

async function enviarAPI(seleccion, name) {
  var urlAPI = "http://localhost:5000/api/kpis/" + seleccion +"/" + name
  console.log("url : " +urlAPI);
  const response = await fetch(urlAPI);
  const data = await response.json();
  console.log(data);
  labels = data.fecha;
  values = data.duplicated_line_density;
  let u_value = values.map(function(element) {
    return 10;
  });

  new Chart(document.getElementById("dlocBarChart"), {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
        label: "% Duplicated Line Density",
        borderColor: "rgba(2,117,216,1)",
        data: values,
      },
      {
        label: "% umbral",
        borderColor: "rgba(0,255,0,1)",
        backgroundColor: "rgba(0,255,0,.255)",
        data: u_value,
      },
    ],
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
              callback: function(value) {
                return value + ' %';
              },
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