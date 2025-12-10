enviarSeleccion();

function enviarSeleccion() {
  // Obtener el valor seleccionado
  var proyecto = document.getElementById("postId").value;
  var repo = document.getElementById("nameId").value;

  // Enviar la selección a la API
  enviarAPI(proyecto, repo);
}

async function enviarAPI(seleccion, name) {
  var urlAPI = "http://localhost:5000/api/kpis/" + seleccion + "/" + name;
  // console.log("url : " +urlAPI);
  const response = await fetch(urlAPI);
  const data = await response.json();
  // console.log(data);
  labels = data.fecha;
  values = data.coverage;
  let sup_value = values.map(function(element) {
    return 100;
  });
  let inf_value = values.map(function(element) {
    return 70;
  });

  console.log(sup_value)

  new Chart(document.getElementById("coverageBarChart"), {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "% umbral sup",
          borderColor: "rgba(0,255,0,1)",
          backgroundColor: "rgba(0,255,0,.2)",
          data: sup_value,
        },
        {
          label: "% umbral inf",
          borderColor: "rgba(0,255,0,1)",
          data: inf_value,
        },
        {
          label: "% Coverage",
          borderColor: "rgba(2,117,216,1)",
          backgroundColor: "rgba(2,117,216,.3)",
          data: values,
        },
      ],
    },
    options: {
      legend: { display: false },
      title: {
        display: false,
        text: "% Coverage",
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
    },
  });
}
