window.onload = function () {
  file = window.location.hash.substr(1);
  if (file === ""){
    document.querySelector("#root_failed").innerHTML = "No file was found or given."
    document.querySelector("#root_failed").hidden = false;
    return;
  }
  fetch(new Request(file)).then((response) => {
    if(response.status == 200) return response.json();
  }).then((results) => {
    // Add to doc
    document.querySelector("#root_name").innerHTML = results.test.name;
    console.log(results);
    stats = getStats(results);
    document.querySelector("#stats_passed").innerHTML = stats.passedTestGroups;
    document.querySelector("#stats_total").innerHTML = stats.failedTestGroups + stats.passedTestGroups;
    updateProgressBar(stats);
    addToDoc(results);
    console.log(stats);
  }).catch((err) => {
    console.error("Error processing", err);
    document.querySelector("#root_failed").innerHTML = "Error finding file. " + err.message;
    document.querySelector("#root_failed").hidden = false;
  });
}

function getStats(result, stats) {
  let obj = stats ? stats : {
    failedTestGroups: 0,
    passedTestGroups: 0,
    failedTests: 0,
    passedTests: 0
  };
  if(result.results) {
    result.results.forEach((item) => {
      obj = getStats(item, obj);
    });
    if(result.result) {
      obj.passedTestGroups += 1
    } else {
      obj.failedTestGroups += 1
    }
  } else {
    if(result.result) {
      obj.passedTests += 1
    } else {
      obj.failedTests += 1
    }
  }
  return obj
}

function addNavButton(result) {
  const type = result.result ? "success" : "danger";
  const html = `<button type="button" class="list-group-item list-group-item-${type}">
      ${result.test.name}
    </button>
  </li>`;
  document.querySelector("#testgroups").innerHTML += html;
}

function updateProgressBar(stats) {
  const passed = document.querySelector("#stat_passed_pb");
  const failed = document.querySelector("#stat_failed_pb");
  const total = stats.passedTests + stats.failedTests;
  passed.style.width =  Math.ceil((stats.passedTests/total)*100) +  "%";
  passed.innerHTML = stats.passedTests;
  failed.style.width =  Math.floor((stats.failedTests/total)*100) +  "%";
  failed.innerHTML = stats.failedTests;
}

function addToDoc(results) {
  const article = document.querySelector("article#results");
  article.classList.add("test");
  article.classList.add("root");
  results.results.forEach((result) => {
    addSection(result, article);
  });
}

function addSection(result, parent) {
  if(result.results) {
    addNavButton(result);
    parent.innerHTML += `<h3>${result.test.name}</h3>`;
    result.results.forEach((childtest) => {
      addSection(childtest, parent);
    });
  }
  else {
    const type = result.result ? "success" : "danger";
    error = result.error != null ? `
    <p class="text-danger">Error:${result.error.message}</p>
    ` : "";
    parent.innerHTML += `<div class="panel panel-${type}">
      <div class="panel-heading"><a onclick="toggleTestDetails(event)">${result.test.name}</a></div>
      <div class="panel-body" hidden>
        <p class="text-muted">Test took ${Math.round(result.time,2)}s to complete.</p>
        ${error}
        <h4>Log</h4>
        <pre>
        ${result.log.join("\n")}
        </pre>
      </div>
    </div>`;
  }
}

function toggleTestDetails(ev) {
  const body = ev.target.parentNode.parentNode.children[1];
  $(body).slideToggle(100);
}
