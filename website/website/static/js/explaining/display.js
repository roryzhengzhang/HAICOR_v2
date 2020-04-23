// Copyright (c) 2020 HAICOR Project Team
// 
// This software is released under the MIT License.
// https://opensource.org/licenses/MIT

//import * as d3 from "d3";

import API from "./api.js";
import Utility from "./utility.js";

export default class Display {
    constructor(master, svg, source, target) {
        this.master = master;
        this.source = source;
        this.target = target;

        // svg setup
        this.dim = {
            width: 1000,
            height: 1000,
            node_radius: 10
        };

        this.svg = d3.select(svg)
            .attr("viewBox", `0 0 ${this.dim.width} ${this.dim.height}`)
            .attr("preserveAspectRatio", "xMidYMid meet");

        // force directed graph setup
        this.node_data = [];
        this.edge_data = [];
        this.candidates = [];

        this.graph = d3.forceSimulation(this.node_data)
            .force("charge", d3.forceManyBody().strength(-100))
            .force("center", d3.forceCenter(this.dim.width / 2, this.dim.height / 2))
            .force(
                "link", d3.forceLink().links(this.edge_data)
                .distance(15 * this.dim.node_radius)
                .id(x => x.id)
            )
            .force("x", d3.forceX(this.dim.width / 2).strength(0.01))
            .force("y", d3.forceY(this.dim.height / 2).strength(0.01))
            .on("tick", () => this.ticked());

        this.edges = this.svg.append("g").attr("id", "edges");
        this.nodes = this.svg.append("g").attr("id", "nodes");
        this.edge_labels = this.svg.append("g").attr("id", "edge-labels");
        this.node_labels = this.svg.append("g").attr("id", "node-labels");
    }

    ticked() {
        // edge manipulations
        let edges = this.edges.selectAll("line").data(this.edge_data);

        edges.enter().append("line")
            .classed("required", d => !d.concrete)
            .attr("stroke-width", this.dim.node_radius / 2.5)
            .on("click", data => this.edge_select(data));

        edges.exit().remove();

        edges.classed("selected", d => d.selected)
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        // node manipulations
        let nodes = this.nodes.selectAll("circle").data(this.node_data, d => d.id);

        nodes.enter().append("circle")
            .attr("r", this.dim.node_radius)
            .call(
                d3.drag()
                .on("start", d => this.drag_started(d))
                .on("drag", d => this.dragging(d))
                .on("end", d => this.drag_ended(d))
            )
            .on("click", data => this.node_select(data))
            .append("title")
            .text(d => d.uri);

        nodes.exit().remove();

        nodes.classed("selected", d => d.selected)
            .attr("cx", d => d.x)
            .attr("cy", d => d.y);

        // edge label manipulations
        let edge_labels = this.edge_labels.selectAll("text").data(this.edge_data);

        edge_labels.enter().append("text")
            .attr("text-anchor", "middle")
            .on("click", data => this.edge_toggle(data));

        edge_labels.exit().remove();

        edge_labels.text(d => d.relations[d.relation].relation)
            .attr("x", d => (d.source.x + d.target.x) / 2)
            .attr("y", d => (d.source.y + d.target.y) / 2);

        // node label manipulations
        let node_labels = this.node_labels.selectAll("text").data(this.node_data, d => d.id);

        node_labels.enter().append("text")
            .attr("transform", `translate(0 ${-1.5 * this.dim.node_radius})`)
            .attr("text-anchor", "middle")
            .text(d => Utility.uri_to_text(d.text));

        node_labels.exit().remove();

        node_labels.attr("x", d => d.x).attr("y", d => d.y);
    }

    // control functions
    insert(data) {
        if (this.node_data.map(d => d.id).includes(data.id))
            return; // duplicate concept

        let concept = {
            id: data.id,
            uri: data.uri,
            text: data.text,
            selected: false
        }

        this.node_data.push(concept);

        this.graph.nodes(this.node_data);

        this.graph.alphaTarget(1).restart();
    }

    remove() {
        this.node_data = this.node_data.filter(d => !d.selected);
        this.edge_data = this.edge_data.filter(
            d => !d.selected &&
            this.node_data.map(d => d.id).includes(d.source.id) &&
            this.node_data.map(d => d.id).includes(d.target.id)
        );

        this.graph.nodes(this.node_data);
        this.graph.force("link").links(this.edge_data);

        this.unselect();
        this.graph.alphaTarget(1).restart();
    }

    unselect() {
        this.candidates = [];

        for (var node of this.node_data)
            node.selected = false;

        for (var edge of this.edge_data)
            edge.selected = false;

        this.graph.alphaTarget(1).restart();
    }

    async connect() {
        if (this.candidates.length != 3)
            return; // invalid selection for connection

        let [source, middle, target] = this.candidates;

        let data = await fetch(API.assertion_search(source, middle, target))
            .then(response => response.json())
            .catch(error => console.log(error));

        // insert nodes
        for (var id of data.left.path)
            await fetch(API.concept(id))
            .then(response => response.json())
            .then(data => this.insert(data))
            .catch(error => console.log(error));

        for (var id of data.right.path)
            await fetch(API.concept(id))
            .then(response => response.json())
            .then(data => this.insert(data))
            .catch(error => console.log(error));

        // insert edges
        if (data.left.connected && data.left.path.length == 0)
            // require more detail
            this.assertion_required(source, middle);

        for (var i = 0; i < data.left.path.length - 1; ++i)
            this.assertion_concrete(data.left.path[i], data.left.path[i + 1]);

        if (data.right.connected && data.right.path.length == 0)
            // require more detail
            this.assertion_required(middle, target);

        for (var i = 0; i < data.right.path.length - 1; ++i)
            this.assertion_concrete(data.right.path[i], data.right.path[i + 1]);

        // remove required edge that are explained
        this.unselect();

        for (var assertion of this.edge_data)
            if (assertion.source.id == source && assertion.target.id == target && assertion.required)
                assertion.selected = true;

        this.remove();
    }

    // utility functions
    node_select(node) {
        node.selected = !node.selected;

        if (node.selected)
            this.candidates.push(node.id);
        else
            this.candidates = this.candidates.filter(d => d != node.id);

        this.ticked();
    }

    edge_select(edge) {
        edge.selected = !edge.selected;

        this.ticked();
    }

    edge_toggle(edge) {
        edge.relation = (edge.relation + 1) % edge.relations.length;

        this.ticked();
    }

    async assertion_concrete(source, target) {
        let data = await fetch(API.assertion(source, target))
            .then(response => response.json())
            .catch(error => console.log(error));

        for (var link of this.edge_data)
            if (link.source == data.source_id && link.target == data.target_id)
                return; // duplicate assertion

        let assertion = {
            source: data.source_id,
            target: data.target_id,
            concrete: true,
            selected: false,
            relation: 0,
            relations: data.relations
        };

        this.edge_data.push(assertion);

        this.graph.force("link").links(this.edge_data);

        this.graph.alphaTarget(1).restart();
    }

    async assertion_required(source, target) {
        let assertion = {
            source: source,
            target: target,
            concrete: false,
            selected: false,
            relation: 0,
            relations: ["?"]
        }

        this.edge_data.push(assertion);

        this.graph.force("link").links(this.edge_data);

        this.graph.alphaTarget(1).restart();
    }

    // node dragging functions
    drag_started(node) {
        if (!d3.event.active) this.graph.alphaTarget(0.3).restart();

        node.fx = node.x;
        node.fy = node.y;
    }

    dragging(node) {
        node.fx = d3.event.x;
        node.fy = d3.event.y;
    }

    drag_ended(node) {
        if (!d3.event.active) this.graph.alphaTarget(0);

        node.fx = null;
        node.fy = null;
    }
}