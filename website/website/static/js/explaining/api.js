// Copyright (c) 2020 HAICOR Project Team
// 
// This software is released under the MIT License.
// https://opensource.org/licenses/MIT

export default class API {
    static concept(id) {
        return `/api/concept/${id}`;
    }

    static concept_search(text, speech) {
        if (speech == '?')
            return `/api/search/${text}`;
        else
            return `/api/search/${text}/${speech}`;
    }

    static assertion(source, target) {
        return `/api/assertion/${source}/${target}`;
    }

    static assertion_search(source, middle, target) {
        return `/api/reason/${source}/${middle}/${target}`;
    }
}