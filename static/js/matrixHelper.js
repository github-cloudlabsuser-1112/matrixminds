
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


async function createTranscript() {
    
    const fileAudio = document.getElementById("fileAudio");
    const transcriptElement = document.getElementById("transciptwindow");
    const step2Element = document.getElementById("step2");
    const prgContainer = document.getElementById("progresscontainer");

    const stepperElement = document.getElementById("stepperRow");
    
    stepperElement.style.display = 'block';

    prgContainer.style.display = 'block';
    transcriptElement.style.display='none';
    const url = '/createTranscript';
    formData = new FormData()
    formData.append("file", fileAudio.files[0], "audioFile.mp3");
    step2Element.classList.add("active");

    var req = fetch(url, {
        method: 'POST',
        body: formData /* or aFile[0]*/
        }); // returns a promise

    req.then(function(response) {
      if (response.ok) {
          response.json().then(data=>{
            const result = data.response;
            var transcriptHTML = '<B>CALL TRANSCRIPT</B><br>'+'<pre>'+result+'</pre><br>';
            transcriptElement.innerHTML = transcriptHTML;
            prgContainer.style.display = 'none';
            transcriptElement.style.display='block';
            step2Element.classList.add("completed");
            step2Element.classList.remove("active");
            generateInsight();
          })
          //const result = JSON.parse(event.data);
          
          //summaryHTML+='<span style="font-size:11px;">This description was formed from information found <b><a target="_blank" href="'+joblink+'">here</a></b>';
          
      } else {
        // status was something else
      }
    }, function(error) {
      console.error('failed due to network error or cross domain')
    })
    
}

async function generateInsight() {
    const transcript= document.getElementById("transciptwindow").innerText;
    const url = '/generateInsights';
    const prgContainer = document.getElementById("progresscontainer");
    const callinsightsContainer = document.getElementById("callInsights");
    
    prgContainer.style.display = 'block';
    const step3Element = document.getElementById("step3");
    step3Element.classList.add("active");

    formData = new FormData()
    formData.append("calltranscript", transcript);

    var req = fetch(url, {
        method: 'POST',
        body: formData /* or aFile[0]*/
        }); // returns a promise

    req.then(function(response) {
      if (response.ok) {
          response.json().then(data=>{
            const category = data.category;
            const sentiment = data.sentiment;
            const emotion = data.emotion;
            const summary = data.summary;

            prgContainer.style.display = 'none';
            callinsightsContainer.style.display='block';

            const callCategoryCont = document.getElementById("callCategory");
            const calEmotionCont = document.getElementById("callEmotion");
            const callSentimentCont = document.getElementById("callsent");
            const callSummaryCont = document.getElementById("callSummary");
            
            var callcatgHTML = '<B>CATEGORY</B><BR>'+'<pre>'+category+'</pre>';
            var callEmotHTML = '<B>EMOTION</B><BR>'+'<pre>'+emotion+'</pre>';
            var callSentHTML = '<B>SENTIMENT</B><BR>'+'<pre>'+sentiment+'</pre>';
            var callSummaryHTML = '<B>SUMMARY OF THE CALL</B><BR>'+'<pre>'+summary+'</pre>';
            callCategoryCont.innerHTML = callcatgHTML;
            calEmotionCont.innerHTML = callEmotHTML;
            callSentimentCont.innerHTML = callSentHTML;
            callSummaryCont.innerHTML = callSummaryHTML;
            step3Element.classList.add("completed");
            step3Element.classList.remove("active");
          })
          //const result = JSON.parse(event.data);
          
          //summaryHTML+='<span style="font-size:11px;">This description was formed from information found <b><a target="_blank" href="'+joblink+'">here</a></b>';
          
      } else {
        // status was something else
      }
    }, function(error) {
      console.error('failed due to network error or cross domain')
    })
   
    
}

async function processFile() {
    
    createTranscript();
    
}

$(function(){
    $('#fileAudio').change(function() {
        var file = $('#fileAudio')[0].files[0].name;
        $('#fileupload').text(file);
    });
});