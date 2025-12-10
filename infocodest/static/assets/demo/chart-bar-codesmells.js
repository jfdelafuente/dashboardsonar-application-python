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
    values = data.codesmells;

  new Chart(document.getElementById("codesmellsBarChart"), {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Code Smells",
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