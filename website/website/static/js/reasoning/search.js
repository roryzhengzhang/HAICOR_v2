// Copyright (c) 2020 HAICOR Project Team
// 
// This software is released under the MIT License.
// https://opensource.org/licenses/MIT

class Search {
    constructor(card, text, speech, submit, result) {
        this.card = document.querySelector(card).cloneNode(true);

        this.text = document.querySelector(text);
        this.speech = document.querySelector(speech);
        this.submit = document.querySelector(submit);
        this.result = document.querySelector(result);

        this.text.addEventListener("input", () => this.speech.value = "u");
        this.submit.addEventListener("click", () => this.search());
    }

    search() {
        let query = `/api/search/${this.text_to_uri(this.text.value)}`
        if (this.speech.value != "u") query += `/${this.speech.value}`;

        this.loading(true);
        fetch(query)
            .then(response => response.json())
            .then(data => this.display(data.concepts))
            .then(() => this.loading(false))
            .catch(error => {});
    }

    select(id) {
        console.log(id);
    }

    display(data) {
        this.result.innerHTML = "";

        if (data.length === 0) this.result.innerHTML = "<h3>No concept found</h3>"
        for (var concept of data) {
            var concept_card = this.card.cloneNode(true);

            if (concept.speech)
                concept_card.childNodes[1].innerHTML = `<h3>${this.uri_to_text(concept.text)} <code style="text-align: right;">${concept.speech}</code><small>${concept.uri}</small></h3>`;
            else
                concept_card.childNodes[1].innerHTML = `<h3>${this.uri_to_text(concept.text)}<small>${concept.uri}</small></h3>`;

            for (var external of concept.externals) {
                var link = document.createElement("a");

                link.href = external;
                link.target = "_blank";
                link.innerHTML = "External source";
                link.style.display = "block";

                concept_card.childNodes[1].append(link);
            }

            concept_card.childNodes[3].value = concept.id;
            concept_card.childNodes[3].master = this;
            concept_card.childNodes[3].onclick = function () {
                this.master.select(this.value);
            }

            this.result.append(concept_card);
        }
    }

    loading(state) {
        this.submit.value = state ? "Loading ..." : "Submit";
    }

    text_to_uri(text) {
        return text.toLowerCase().replace(/\s+/g, "_");
    }

    uri_to_text(text) {
        return text.toLowerCase().replace(/_/g, " ");
    }
}

export {
    Search
};