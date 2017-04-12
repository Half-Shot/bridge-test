window.report = getHash();
window.onload = function () {
  getFileIndex();
  getReport(window.report.file).then(() => {
    setupOptions();
    parseReport();
  });
}

function createHash(test) {
  return window.report.file+"~"+test;
}

function setupOptions() {
  opts = JSON.parse(window.localStorage.getItem("bridgetest.opts"));
  if(!opts) {
    opts = {
      showPassed: false,
    }
    window.localStorage.setItem("bridgetest.opts", JSON.stringify(opts));
  }
  window.opts = opts;
  if(!window.test_results.result) {
    $("#showPassed").attr("checked", opts.showPassed);
    $("#showPassed").change(() => {
      window.opts.showPassed = !window.opts.showPassed;
      parseReport();
      window.localStorage.setItem("bridgetest.opts", JSON.stringify(window.opts));
    });
  } else {
    $("#showPassed").hidden = true;
    $("#showPassed").attr("disabled", true);
    $("#showPassed").attr("checked", true);
    window.opts.showPassed = true;
  }
}

function getHash(){
  const hash = window.location.hash.substr(1);
  items = hash.split("~");
  return {file: items[0], test:items[1]}
}

function getFileIndex() {
  fetch(new Request("index.json")).then((response) => {
    if(response.status == 200) return response.json();
  }).catch((err) => {
    console.error("Couldn't read test index.");
  }).then((index) => {
    index.forEach((file) => {
      document.querySelector("#dropdown_file_files").innerHTML += `
        <li><a href="#${file}" onclick="getReport("${file}");">${file}</a></li>
      `
    });
  });
}

function getReport(file) {
  console.log(`Loading '${file}'`);
  if (file === ""){
    document.querySelector("#root_info").hidden = false;
    return;
  }
  document.querySelector("#root_failed").hidden = true;
  document.querySelector("#root_passed").hidden = true;
  return fetch(new Request(file)).then((response) => {
    if(response.status == 200) return response.json();
  }).then((results) => {
    window.test_results = results;
  }).catch((err) => {
    console.error("Error processing", err);
    document.querySelector("#root_failed").innerHTML = "Error finding file. " + err.message;
    document.querySelector("#root_failed").hidden = false;
  });
}

function parseReport(){
  const results = window.test_results;
  document.querySelector(results.result ? "#root_passed" : "#root_failed").hidden = false;
  // Add to doc
  document.querySelector("#root_name").innerHTML = results.test.name;
  console.log(results);
  stats = getStats(results);
  document.querySelector("#stats_passed").innerHTML = stats.passedTestGroups;
  document.querySelector("#stats_total").innerHTML = stats.failedTestGroups + stats.passedTestGroups;
  updateProgressBar(stats);
  addToDoc(results);
  console.log(stats);
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

function addNavButton(result, link) {
  const type = result.result ? "success" : "danger";
  const label = result.result ? "Passing" : "Failing";
  const html = `<li role="presentation">
      <a href="#${link}">
        ${result.test.name}
        <span class="label label-${type}">${label}</span>
      </a>
    </li>
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
  article.innerHTML = "";
  document.querySelector("#testgroups").innerHTML = ""
  article.classList.add("test");
  article.classList.add("root");

  results.results.forEach((result) => {
    article.innerHTML += addSection(result, article);
  });
}

function addSection(result, parent) {
  const id = "_test_" + result.test.name.replace(/\s/g, '_').toLowerCase();
  const link = createHash(id);
  let html = "";
  if(result.results) {
    addNavButton(result, link);
    html += `<section data-result="${result.result}" id=${link}>`
    html += `<h3>${result.test.name}</h3>`;
    result.results.forEach((childtest) => {
      html += addSection(childtest, parent);
    });
    html += `</section>`;
    return html;
  }
  else {
    if (!window.opts.showPassed && result.result) {
      return "";
    }
    const type = result.result ? "success" : "danger";
    error = result.error != null ? `
      <p class="text-danger">Error:${result.error.message}</p>
      <h4>Vars</h4>
      <pre>${JSON.stringify(result.error.vars, null, 2)}</pre>
    ` : "";
    return`<div data-result="${result.result}" class="panel panel-${type}">
      <div class="panel-heading">
        <a href="#${id}" data-toggle="collapse" aria-expanded="false" aria-controls="${id}">${result.test.name}</a>
      </div>
      <div id="${id}" class="panel-body collapse">
        <p class="text-muted">Test took ${Math.round(result.time,2)}s to complete.</p>
        ${error}
        <h4>Log</h4>
        <pre>
        ${(result.log || ["No log file"]).join("\n")}
        </pre>
      </div>
    </div>`;
  }
}
