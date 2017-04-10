resultFiles = ["twitter.json"]

window.onload = function () {
  resultFiles.forEach((file) => {
    fetch(new Request(file)).then((response) => {
      if(response.status == 200) return response.json();
    }).then((results) => {
      // Add to doc
      console.log(results)
      addToDoc(results)
    });
  });
}

function addToDoc(results) {
  const main = document.querySelector("main")
  const article = document.createElement("article");
  article.classList.add("test");
  article.classList.add("root");
  let header = document.createElement("header");
  header.classList.add(results.result ? "pass" : "fail");
  header.innerHTML = results.test.name;
  article.appendChild(header);
  results.results.forEach((result) => {
    article.appendChild(addSection(result, article));
  });
  main.appendChild(article);
}

function addSection(result, parent) {
  const section = document.createElement("section");
  const header = document.createElement("header");
  section.classList.add("test");
  section.classList.add("sub");
  header.classList.add(result.result ? "pass" : "fail");
  header.innerHTML = result.test.name;
  section.appendChild(header);
  if(result.results) {
    result.results.forEach((childtest) => {
      console.log(result.test);
      section.appendChild(addSection(childtest, section));
    });
  }
  else {
    const details = document.createElement("p");
    details.classList.add("details");
    section.appendChild(details);
  }
  return section;
}
