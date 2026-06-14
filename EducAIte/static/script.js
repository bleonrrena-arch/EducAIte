function handleEnter(event) {
  if (event.key === "Enter" || event.keyCode === 13) {
    event.preventDefault();
    generateLecture();
  }
}

function openNav() {
  document.getElementById("mySidebar").classList.add("open");
  refreshSidebar();
}

function closeNav() {
  document.getElementById("mySidebar").classList.remove("open");
}

async function currentTopic() {
  return document.getElementById("topic").value;
}

async function generateLecture() {
  const topic = await currentTopic();
  const output = document.getElementById("output");
  const errorDiv = document.getElementById("error");
  const loading = document.getElementById("loading");
  const validation = document.getElementById("validation");

  output.innerHTML = "";
  errorDiv.innerText = "";

  if (!topic.trim()) {
    errorDiv.innerText = "Please enter a topic before generating.";
    return;
  }

  loading.style.display = "flex";

  try {
    const inputSection = document.querySelector(".input-section");
    inputSection.classList.add("fade-out");

    await new Promise((resolve) => setTimeout(resolve, 500));

    const introResponse = await fetch("/generate_intro", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic }),
    });
    const introData = await introResponse.json();
    if (introData.introduction) {
      const introEl = document.createElement("div");
      introEl.innerHTML = introData.introduction;
      output.appendChild(introEl);
    }

    const bodyResponse = await fetch("/generate_body", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic, introduction: introData.introduction }),
    });
    const bodyData = await bodyResponse.json();
    if (bodyData.body) {
      const bodyEl = document.createElement("div");
      bodyEl.innerHTML = bodyData.body;
      output.appendChild(bodyEl);
      const saveBtn = document.createElement("div");

      saveBtn.style.textAlign = "center";
      saveBtn.style.margin = "2rem 0";
      saveBtn.innerHTML = `<button onclick="saveLecture()" id="save-lecture">Save Lecture</button>`;
      output.appendChild(saveBtn);
    }

    const quizResponse = await fetch("/generate_quiz", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic, body: bodyData.body }),
    });
    const quizData = await quizResponse.json();
    if (quizData.quiz) {
      const quizEl = document.createElement("div");
      quizEl.innerHTML = quizData.quiz;
      output.appendChild(quizEl);

      quizEl.querySelectorAll("[id]").forEach((el) => {
        el.id = `${el.id}_0`;
      });
      quizEl.querySelectorAll("[name]").forEach((el) => {
        el.name = `${el.name}_0`;
      });
      quizEl.querySelectorAll("[for]").forEach((el) => {
        el.htmlFor = `${el.htmlFor}_0`;
      });

      const firstValidationBtn = quizEl.querySelector("#validation_0");
      if (firstValidationBtn) {
        firstValidationBtn.removeAttribute("onclick");
        firstValidationBtn.addEventListener("click", function () {
          validateQuiz(quizEl);
        });
        firstValidationBtn.classList.add("validation");
      }

      const quizBtn = document.createElement("div");

      quizBtn.style.textAlign = "center";
      quizBtn.style.margin = "2rem 0";
      quizBtn.innerHTML = `<button onclick="generateQuiz()" id="generate-quiz">Generate Quiz</button>`;
      output.appendChild(quizBtn);
    }

    inputSection.classList.remove("fade-out");
  } catch (err) {
    errorDiv.innerText = "Error: " + err.message;
  } finally {
    loading.style.display = "none";
  }
}

async function generateQuiz() {
  const topic = document.getElementById("topic")?.value || document.body.dataset.topic || "";

  const output = document.getElementById("output");
  const errorDiv = document.getElementById("error");
  const loading = document.getElementById("loading");
  const existingBtn = document.querySelector("#generate-quiz")?.closest("div");
  if (existingBtn) existingBtn.remove();
  errorDiv.innerText = "";
  loading.style.display = "flex";

  try {
    await new Promise((resolve) => setTimeout(resolve, 500));

    const allQuizzes = document.getElementsByClassName("quizz");
    const lastQuiz = allQuizzes.length > 0 ? allQuizzes[allQuizzes.length - 1].innerHTML : "";

    const bodyContent = document.querySelector(".lecbody")?.innerHTML || "";

    const quizResponse = await fetch("/generate_quiz", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic, body: bodyContent, quiz: lastQuiz }),
    });
    const quizData = await quizResponse.json();

    if (quizData.quiz) {
      const newQuizEl = document.createElement("div");
      newQuizEl.innerHTML = quizData.quiz;

      const quizIndex = document.getElementsByClassName("quizz").length;
      newQuizEl.querySelectorAll("[id]").forEach((el) => {
        el.id = `${el.id}_${quizIndex}`;
      });
      newQuizEl.querySelectorAll("[name]").forEach((el) => {
        el.name = `${el.name}_${quizIndex}`;
      });
      newQuizEl.querySelectorAll("[for]").forEach((el) => {
        el.htmlFor = `${el.htmlFor}_${quizIndex}`;
      });

      const validationBtn = newQuizEl.querySelector("#validation_" + quizIndex);
      if (validationBtn) {
        validationBtn.removeAttribute("onclick");
        validationBtn.addEventListener("click", function () {
          validateQuiz(newQuizEl);
        });
        validationBtn.classList.add("validation");
      }

      const key = newQuizEl.querySelector(".key");
      if (key) key.style.display = "none";

      output.appendChild(newQuizEl);

      const quizBtn = document.createElement("div");
      quizBtn.style.textAlign = "center";
      quizBtn.style.margin = "2rem 0";
      quizBtn.innerHTML = `<button onclick="generateQuiz()" id="generate-quiz">Generate Another Quiz</button>`;
      output.appendChild(quizBtn);
    }
  } catch (err) {
    errorDiv.innerText = "Error: " + err.message;
  } finally {
    loading.style.display = "none";
  }
}

async function independent_quiz() {
  const body = document.getElementById("topic").value;
  const fileInput = document.getElementById("file");
  const output = document.getElementById("output");
  const errorDiv = document.getElementById("error");
  const loading = document.getElementById("loading");
  const existingBtn = document.querySelector("#generate-quiz")?.closest("div");
  if (existingBtn) existingBtn.remove();
  errorDiv.innerText = "";

  if (!body.trim() && fileInput.files.length === 0) {
    errorDiv.innerText = "Please enter text or upload a file.";
    errorDiv.style.display = "flex";
    return;
  }

  const fileName = fileInput.files[0].name.toLowerCase();

  if (!fileName.endsWith(".pdf") && !fileName.endsWith(".txt")) {
    errorDiv.innerText = "The uploaded file type is not allowed. Please upload either a PDF or a text file.";
    errorDiv.style.display = "flex";
    return;
  }

  if (fileInput.files[0].size > 20971520) {
    errorDiv.innerText = "The uploaded file is too large. Please upload a file smaller than 20MB.";
    errorDiv.style.display = "flex";
    return;
  }

  loading.style.display = "flex";

  const formData = new FormData();
  formData.append("body", body);

  if (fileInput.files.length > 0) {
    formData.append("file", fileInput.files[0]);
  }

  try {
    const allQuizzes = document.getElementsByClassName("quizz");
    const lastQuiz = allQuizzes.length > 0 ? allQuizzes[allQuizzes.length - 1].innerHTML : "";

    const response = await fetch("/independentQuiz", { method: "POST", body: formData, quiz: lastQuiz });
    const quizData = await response.json();

    if (!response.ok || quizData.error) {
      errorDiv.innerText = quizData.error || "Something went wrong.";
      errorDiv.style.display = "flex";
      return;
    }

    if (quizData.quiz) {
      const quizEl = document.createElement("div");
      quizEl.innerHTML = quizData.quiz;

      const quizIndex = document.getElementsByClassName("quizz").length;
      quizEl.querySelectorAll("[id]").forEach((el) => {
        el.id = `${el.id}_${quizIndex}`;
      });
      quizEl.querySelectorAll("[name]").forEach((el) => {
        el.name = `${el.name}_${quizIndex}`;
      });
      quizEl.querySelectorAll("[for]").forEach((el) => {
        el.htmlFor = `${el.htmlFor}_${quizIndex}`;
      });

      const key = quizEl.querySelector(".key");
      if (key) key.style.display = "none";

      const validationBtn = quizEl.querySelector("#validation_" + quizIndex);
      if (validationBtn) {
        validationBtn.removeAttribute("onclick");
        validationBtn.addEventListener("click", function () {
          validateQuiz(quizEl);
        });
      }

      output.appendChild(quizEl);

      const quizBtn = document.createElement("div");
      quizBtn.style.textAlign = "center";
      quizBtn.style.margin = "2rem 0";
      quizBtn.innerHTML = `<button onclick="independent_quiz()" id="generate-quiz">Generate New Quiz</button>`;
      output.appendChild(quizBtn);
    }
  } catch (err) {
    errorDiv.innerText = "Error: " + err.message;
  } finally {
    loading.style.display = "none";
  }
}

function validateQuiz(container) {
  const keyDiv = container.querySelector(".key");
  const answers = JSON.parse(keyDiv.textContent.replace(/'/g, '"'));

  let score = 0;
  let total = Object.keys(answers).length;
  let feedback = "";

  for (let q in answers) {
    let userAnswer;

    // Find all radios with this name within the container (name was suffixed)
    const allInputs = Array.from(container.querySelectorAll(`[name]`));
    const radios = allInputs.filter((el) => el.type === "radio" && el.name.startsWith(q + "_"));

    if (radios.length > 0) {
      for (let r of radios) {
        if (r.checked) {
          userAnswer = r.value;
          break;
        }
      }
    } else {
      const input = allInputs.find((el) => el.id && el.id.startsWith(q + "_"));
      if (input) userAnswer = input.value.trim();
    }

    if (userAnswer) {
      if (userAnswer.toLowerCase() === answers[q].toLowerCase()) {
        score++;
        feedback += `Question ${q.slice(1)}: Correct<br>`;
      } else {
        feedback += `Question ${q.slice(1)}: Incorrect (Correct: ${answers[q]})<br>`;
      }
    } else {
      feedback += `Question ${q.slice(1)}: No answer provided<br>`;
    }
  }

  container.querySelector("[id^='quiz-result']").innerHTML = `<h3>Your Score: ${score}/${total}</h3>` + feedback;
}

function toggleServicesDropdown() {
  document.getElementById("services-dropdown").classList.toggle("open");
}

async function saveLecture() {
  const saveBtn = document.getElementById("save-lecture");
  const title = document.querySelector(".lecture-title")?.outerHTML || "";
  const intro = document.querySelector(".introduction")?.outerHTML || "";
  const body = document.querySelector(".lecbody")?.outerHTML || "";
  const conclusion = document.querySelector(".conclusion")?.outerHTML || "";
  const popup = document.getElementById("popup");
  const topic = await currentTopic();
  const text = document.getElementById("popup-text");

  const lectureHTML = title + intro + body + conclusion;
  if (!lectureHTML.trim()) {
    alert("Nothing to save yet.");
    return;
  }

  const res = await fetch("/save_lecture", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ topic, html: lectureHTML }),
  });
  const data = await res.json();
  if (data.success)
    ((text.innerHTML = `The lecture with the topic<br><strong>${topic}</strong><br> has been saved successfully!`),
      (popup.style.display = "flex"),
      refreshSidebar(),
      (saveBtn.style.display = "none"));
  else alert("Failed to save lecture.");
}

async function closePopup() {
  const popup = document.getElementById("popup");
  popup.style.display = "none";
}

function loadLecture(key) {
  window.location.href = `/Lecture/${key}`;
}

async function deleteLecture(key) {
  if (!confirm("Delete this saved lecture?")) return;
  const res = await fetch(`/delete_lecture/${key}`, { method: "DELETE" });
  const data = await res.json();
  if (data.success) {
    if (window.location.pathname === `/Lecture/${key}`) {
      window.location.href = "/LectureGenerator";
    } else {
      await refreshSidebar();
    }
  } else alert("Failed to delete.");
}

async function refreshSidebar() {
  const listDiv = document.getElementById("sidebar-lecture-list");
  const res = await fetch("/get_lectures");
  const lectures = await res.json();
  const keys = Object.keys(lectures).sort().reverse();

  if (keys.length === 0) {
    listDiv.innerHTML = `<p class="sidebar-empty">No saved lectures yet.</p>`;
    return;
  }
  listDiv.innerHTML = keys
    .map(
      (key) => `
  <a href="javascript:void(0)" onclick="loadLecture('${key}')">
    <span>${lectures[key].topic}</span>
    <button class="delete-btn" onclick="event.stopPropagation(); deleteLecture('${key}')"><i class="fa fa-trash-o" style="font-size:20px"></i></button>
  </a>
`,
    )
    .join("");
}

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        observer.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.15 },
);

document.querySelectorAll(".card, .step, .cta-banner").forEach((el) => observer.observe(el));
