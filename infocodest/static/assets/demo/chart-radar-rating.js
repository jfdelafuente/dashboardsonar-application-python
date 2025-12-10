enviarSeleccion();

function enviarSeleccion() {
  // Obtener el valor seleccionado
  var aplicacion = document.getElementById("postId").value;
  var name = document.getElementById("nameId").value;

  // Enviar la selección a la API
  enviarAPI(aplicacion, name);
}

async function enviarAPI(aplicacion, name) {
  var urlAPI = "http://localhost:5000/api/rating/" + aplicacion + "/" + name;
  console.log("url : " + urlAPI);
  const response = await fetch(urlAPI);
  const data_json = await response.json();
  labels = ["Reliability Rating", "Security Rating", "Sqale Rating"];
  values = [
    data_json.reliability_rating[0],
    data_json.security_rating[0],
    data_json.sqale_rating[0],
  ];
  console.log(values);

  const marksData = {
    labels: labels,
    datasets: [
      {
        data: values,
        backgroundColor: "rgba(54, 162, 235, 0.5)",
        borderColor: "rgb(54, 162, 235)",
        borderWidth: 2,
      },
    ],
  };

  const chartOptions = {
    scales: {
      r: {
        beginAtZero: false,
        min: 0,
        max: 5,
        ticks: {
          stepSize: 1,
        },
      },
    },
  };

  new Chart(document.getElementById("radarChart"), {
    type: "radar",
    data: marksData,
    options: chartOptions,
  });
}
