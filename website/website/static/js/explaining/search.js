// Copyright (c) 2020 HAICOR Project Team
// 
// This software is released under the MIT License.
// https://opensource.org/licenses/MIT

import API from "./api.js";
import Utility from "./utility.js";

export default class Search {
    constructor(master, text, speech, submit, template, container) {
        this.master = master;

        this.search_bar = new SearchBar(this, text, speech, submit);
        this.search_result = new SearchResult(this, template, container);
    }

    async search(text, speech) {
        let query = API.concept_search(text, speech);

        this.search_bar.ready(false);
        fetch(query).then(response => response.json())
            .then(result => {
                this.search_bar.ready(true);
                this.search_result.display(result.concepts);
            })
            .catch(error => console.log(error));
    }
}

class SearchBar {
    constructor(master, text, speech, submit) {
        this.master = master;

        this.inputs = {
            text: document.querySelector(text),
            speech: document.querySelector(speech),
            submit: document.querySelector(submit)
        }

        this.ready(true);
        this.inputs.submit.addEventListener("click", () => this.submit());
        this.inputs.text.addEventListener("input", () => this.inputs.speech.value = '?');
    }

    ready(state) {
        this.inputs.submit.value = state ? "Submit" : "Searching..."
    }

    async submit() {
        if (this.inputs.text.value == "") return;

        this.master.search(
            Utility.text_to_uri(this.inputs.text.value),
            this.inputs.speech.value
        );
    }
}

class SearchResult {
    constructor(master, template, container) {
        this.master = master;

        this.template = document.querySelector(template);
        this.container = document.querySelector(container);
    }

    display(results) {
        this.clear();

        for (var result of results) {
            this.container.append(this.render(result));
        }
    }

    clear() {
        this.container.innerHTML = "";
    }

    render(result) {
        /* HTML Specific */
        let content = this.template.cloneNode(true);

        if (result.speech == null)
            content.querySelector(".concept-speech").classList.add("hidden");

        if (result.externals.length == 0)
            content.querySelector(".concept-externals").classList.add("hidden");

        content.querySelector(".concept-uri").textContent = result.uri;
        content.querySelector(".concept-text").textContent = Utility.uri_to_text(result.text);
        content.querySelector(".concept-speech").textContent = result.speech;

        for (var external of result.externals) {
            let link = document.createElement("a");

            link.href = external;
            link.target = "_blank";
            link.textContent = "External link";
            link.style.display = "block";

            content.querySelector(".concept-externals").append(link);
        }

        let button = content.querySelector(".concept-button");

        button.master = this;
        button.result = result;
        button.onclick = function () {
            this.master.insert(this.result);
        }

        return content;
    }

    insert(result) {
        this.master.master.insert(result);
    }
}