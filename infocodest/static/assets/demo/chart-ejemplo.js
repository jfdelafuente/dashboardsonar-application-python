// ejemplo charts.js

var ctx = document.getElementById("myEjemploChart");
var myBarChart = new Chart(ctx, {
  type: 'bar',
  data: {
    datasets: [{
        label: 'Bugs',
        backgroundColor: "rgba(2,117,216,0.2)",
        borderColor: "rgba(2,117,216,1)",
        borderWidth: 1,
    }],
  },
  options: {
    scales: {
        y: {
            beginAtZero: true
        }
    }
  }
});

let url = 'http://localhost:5000/api/registro'
fetch(url)
    .then( response => response.json() )
    .then( datos => mostrar(datos) )
    .catch ( error => console.log(error) )



const mostrar = (articulos)    => {
    articulos.forEach(element => {
        myBarChart.data['labels'].push(element.created_on)
        myBarChart.data['datasets'][0].data.push(element.num_bugs)
    });
    console.log(myBarChart.data)
}


