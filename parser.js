// ==UserScript==
// @name         Парсер sdamgia.ru
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  По нажатию кнопки вы можете получить все задачи и ответы на них в формате json
// @author       t138szx
// @match        https://soc-ege.sdamgia.ru/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=sdamgia.ru
// @grant        none
// ==/UserScript==

(function(open) {
    XMLHttpRequest.prototype.open = function() {
        this.addEventListener("readystatechange", function() {

            if (this.readyState == 4 && window.location.href.search("test") != -1) {
                main();
            }
        }, false);
        open.apply(this, arguments);
    };
})(XMLHttpRequest.prototype.open);

function main() {
    let check = document.getElementById("global_temp");
    if (check) return;

    let button = document.createElement("button");
    button.style.position = "fixed";
    button.style.top = "0";
    button.style.left = "0";
    button.style.zIndex = "1000";
    button.style.backgroundColor = "white";
    button.innerHTML = "Получить задачи";
    document.body.appendChild(button);

    let input = document.createElement("input");
    input.id = "input_id";
    input.style.position = "fixed";
    input.style.top = "0";
    input.style.left = "100px";
    input.style.zIndex = "1000";
    input.placeholder = "Введите номер: ";
    document.body.appendChild(input);
    button.addEventListener("click", function() {

        let number = document.getElementById("input_id").value;
        steal(number);
    });
    let global = document.createElement("div");
    global.id = "global_temp";
    document.body.appendChild(global);
}

function steal(task_num) {
    let json = {
        "task_num": task_num,
        "tasks": []
    };

    let problems = document.getElementsByClassName("prob_view");
    let tasks = [];
    for (let i = 0; i < problems.length; i++) {
        let problem = problems[i].childNodes[0];
        let problem_text = problem.childNodes[0].childNodes[0].childNodes[1].innerText;
        let explain_button = problem.childNodes[1].childNodes[1].childNodes[0];
        explain_button.click();

        let answer_text = problem.childNodes[0].childNodes[1].innerText;
        let explain_text;

        if (answer_text.search("Пояснение.") != -1) {
            let answer = answer_text.split("Ответ:");
            answer_text = "Ответ:" + answer[1];
            explain_text = answer[0];
        }

        let task = {
            "problem_text": problem_text,
            "answer_text": answer_text,
            "explain_text": explain_text
        };

        tasks.push(task);
    }
    json.tasks = tasks;
    download(JSON.stringify(json), "tasks_" + task_num + ".json", "text/plain");
}


function download(content, fileName, contentType) {
    var a = document.createElement("a");
    var file = new Blob([content], {
        type: contentType
    });
    a.href = URL.createObjectURL(file);
    a.download = fileName;
    a.click();
}