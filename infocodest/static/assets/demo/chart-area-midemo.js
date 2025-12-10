getData();
async function getData() {
  url =
    "https://softwarequality-cfmpro-tc.shared-nonprod.cloud.si.orange.es/api/measures/search_history";

  let params = {
    component: "com.orange.crm4telcoosp.application.java:crm4telco",
    metrics: "complexity",
  };

  url += "?" + new URLSearchParams(params).toString();

  let headers = {
    Accept: "application/json",
    "Content-Type": "application/json; charset=UTF-8",
  };

  let fetchData = {
    method: "GET",
    headers: headers,
    mode: "no-cors",
    // credentials: "include",
  };

  console.log(url);
  var request = new Request(url, fetchData);
  const response = await fetch(request)
  .then(res => {
    if(type.includes('json')) {
      const json = res.json();
      console.log('json =', json);
      return json;
    } else {
      const buffer = res.arrayBuffer();
      console.log('buffer =', buffer);
      return buffer;
    }
  })
  .then(data => {
    console.log('data =', data);
    const blob = new Blob(
      [data],
      {'type' : type},
    );
    console.log(" url blob")
    const urlBlob = URL.createObjectURL(blob);
    dom.src = urlBlob;
    link.href = urlBlob;
    link.innerText = urlBlob;
  }).catch(err => {}).finally(() => {});

  console.log("log ...")
  console.log(response);
  // data = await response.text.json();
  // console.log(data);
  //length = data.measure.length;
  //console.log(length);
  labels = [];
  values = [];
  for (i = 0; i < length; i++) {
    labels.push(data.measure.history[i].date);
    values.push(data.measure.history[i].value);
  }
  new Chart(document.getElementById("demoAreaChart"), {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Population (millions)",
          backgroundColor: [
            "#3a90cd",
            "#8e5ea2",
            "#3bba9f",
            "#e8c3b9",
            "#c45850",
            "#CD9C5C",
            "#40E0D0",
          ],
          data: values,
        },
      ],
    },
    options: {
      legend: { display: false },
      title: {
        display: true,
        text: "U.S population",
      },
    },
  });
}
