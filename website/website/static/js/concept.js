// Copyright (c) 2020 HAICOR Project Team
// 
// This software is released under the MIT License.
// https://opensource.org/licenses/MIT

class Search {
    constructor(controller, text, speech, submit, result) {
        this.controller = controller;

        this.search_bar = new SearchBar(this, text, speech, submit);
        this.search_result = new SearchResult(this, result);
    }

    search(text, speech) {
        this.search_result.search(text, speech);
    }
}

class SearchBar {
    constructor(controller, text, speech, submit) {
        this.controller = controller;

        this.text_field = document.querySelector(text);
        this.speech_field = document.querySelector(speech);
        this.submit_field = document.querySelector(submit);

        this.text_field.addEventListener("input", () => this.speech_field.value = "u");
        this.submit_field.addEventListener("click", () => this.search());
    }

    search() {
        this.controller.search(
            this.text_field.value.toLowerCase().replace(/\s+/g, "_"),
            this.speech_field.value
        )
    }

    loading(flag) {
        this.submit_field.value = flag ? "loading" : "submit";
    }
}

class SearchResult {
    constructor(controller, result) {
        this.controller = controller;

        this.result_container = document.querySelector(result);
    }

    search(text, speech) {
        let query = `/api/search/${text}`;

        if (speech != "u") query += `/${speech}`;

        this.controller.search_bar.loading(true);

        fetch(query)
            .then(data => data.json())
            .then(data => this.display(data.concepts))
            .then(this.controller.search_bar.loading(false))
            .catch(error => console.log(error));
    }

    display(concept_ids) {
        this.result_container.innerHTML = "";

        if (concept_ids.length === 0) {
            this.result_container.innerHTML = `
                <span id="concept-not-found">No Result Found</span>
            `;
        } else {
            let counter = 100; // breaker

            for (var id of concept_ids) {
                if (--counter === 0)
                    break;

                fetch(`/api/concept/${id}`)
                    .then(data => data.json())
                    .then(data => {
                        var uri_tag = document.createElement("em");
                        uri_tag.style.display = "block";
                        uri_tag.innerText = data.uri;

                        var id_tag = document.createElement("span");
                        id_tag.style.display = "block";
                        id_tag = document.innerText = `ID: ${data.id}`;

                        var card = document.createElement("div");
                        card.setAttribute("class", "card");

                        card.append(uri_tag);
                        card.append(id_tag);

                        this.result_container.append(card);
                    });
            }
        }
    }
}

export {
    Search,
    SearchBar,
    SearchResult,
};