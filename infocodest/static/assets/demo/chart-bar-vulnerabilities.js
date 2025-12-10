enviarSeleccion();

function enviarSeleccion() {
  // Obtener el valor seleccionado
  var seleccion = document.getElementById("postId").value;
  console.log("Seleccion :" + seleccion);

  // Enviar la selección a la API
  enviarAPI(seleccion);
}

async function enviarAPI(seleccion) {
  var urlAPI = "http://localhost:5000/api/aplicacion/" + seleccion
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
        label: "Vulnerabilities",
        backgroundColor: "rgba(2,117,216,1)",
        borderColor: "rgba(2,117,216,1)",
        data: values,
      }],
    },
    options: {
      legend: { display: false },
      title: {
        display: false,
        text: "Proyectos",
      },
    }
  });
}