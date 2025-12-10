getData();
async function getData() {
  const response = await fetch(
    "http://localhost:5000/api/charts_data"
  );
  const data = await response.json();
  console.log(data);
  labels = data.labels;
  values = data.values;

  new Chart(document.getElementById("demo2BarChart"), {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Revenue",
        backgroundColor: [
          "#3a90cd",
          "#8e5ea2",
          "#3bba9f",
          "#e8c3b9",
          "#c45850",
          "#CD9C5C",
          "#40E0D0",
        ],
        borderColor: "rgba(2,117,216,1)",
        data: values,
      }],
    },
    options: {
      legend: { display: false },
      title: {
        display: true,
        text: "Proyectos",
      },
    }
  });
}