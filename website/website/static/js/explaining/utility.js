// Copyright (c) 2020 HAICOR Project Team
// 
// This software is released under the MIT License.
// https://opensource.org/licenses/MIT

export default class Utility {
    static text_to_uri(content) {
        return content.toLowerCase().replace(/\s+/g, '_');
    }

    static uri_to_text(content) {
        return content.replace(/_/g, ' ');
    }
}