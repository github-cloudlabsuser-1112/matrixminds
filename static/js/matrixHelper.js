
async function clearCharts() {
    if (document.getElementById("callissues")) {
        document.getElementById("callissues").innerHTML = "";
    }
    var x = document.getElementById("progresscontainer_1");
    x.style.display = 'block';
  }

async function drawSummaryCharts() {
    
    document.getElementById("dashboard").style.backgroundColor = "#003F61";
    document.getElementById("i-dashboard").style.color = "#FFFF";
    const url = '/summarychart';
    const categoryElement = document.getElementById("callissues");
    const sentimentElement = document.getElementById("callsentiment");
    const emotionElement = document.getElementById("callemotion");
    const avgTimeElement = document.getElementById("avgTimeElement");
    formData = new FormData()
    //formData.append("file", rfpfile.files[0], rfpfile.files[0].name);
    
    
    var req = fetch(url, {
        method: 'POST'
        }); // returns a promise

    req.then(function(response) {
      if (response.ok) {
          response.json().then(data=>{
            const categorySummary = data.categoryresponse;
            const sentimentSummary = data.sentimentresponse;
            const emotionSummary = data.emotionresponse;
            const avgTimeSummary = data.avgtimeresponse;
            Plotly.newPlot( categoryElement, categorySummary);
            var layout = {
                height: 215,
                width: 270,
                margin: {"t": 0, "b": 0, "l": 0, "r": 0},
                showlegend: false
                }
            Plotly.newPlot( sentimentElement, sentimentSummary,layout);
            Plotly.newPlot( emotionElement, emotionSummary,layout);
            Plotly.newPlot( avgTimeElement, avgTimeSummary,layout);
            var x = document.getElementById("progresscontainer_1");
            x.style.display = 'none';
          })
      } else {
        // status was something else
      }
    }, function(error) {
      console.error('failed due to network error or cross domain')
    })

}