export async function getMeasureHistory() {

    const url = "https://softwarequality-cfmpro-tc.shared-nonprod.cloud.si.orange.es/api/measures/search_history"

    let params = {
        component: "com.orange.crm4telcoosp.application.java:crm4telco",
        metrics: "complexity"
    };

    url += "?" + new URLSearchParams(params).toString();

    let headers = {
      Accept: "application/json"
    };
  
    let fetchData = {
      method: "GET",
      headers: headers,
      mode: "no-cors",
      credentials: "include"
    };

    var request = new Request(url, fetchData);

    fetch(request)
      .then(res => res.json())
      .then(json => { console.log(json);} )
      .catch(err => console.log(err));

}

export async function getDimensions() {
  const dimensionsQuery = {
    dimensions: [
      'Artworks.widthCm',
      'Artworks.heightCm'
    ],
    measures: [
      'Artworks.count'
    ],
    filters: [
      {
        member: 'Artworks.classification',
        operator: 'equals',
        values: [ 'Painting' ]
      },
      {
        member: 'Artworks.widthCm',
        operator: 'set'
      },
      {
        member: 'Artworks.widthCm',
        operator: 'lt',
        values: [ '500' ]
      },
      {
        member: 'Artworks.heightCm',
        operator: 'set'
      },
      {
        member: 'Artworks.heightCm',
        operator: 'lt',
        values: [ '500' ]
      }
    ]
  };

  const resultSet = await cubeApi.load(dimensionsQuery);

  return resultSet.tablePivot().map(row => ({
    width: parseInt(row['Artworks.widthCm']),
    height: parseInt(row['Artworks.heightCm']),
    count: parseInt(row['Artworks.count'])
  }));
}