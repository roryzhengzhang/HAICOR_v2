// Copyright (c) 2020 HAICOR Project Team
// 
// This software is released under the MIT License.
// https://opensource.org/licenses/MIT

//import * as d3 from "d3";

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
            node_radius: 12
        };

        this.svg = d3.select(svg)
            .attr("viewBox", `0 0 ${this.dim.width} ${this.dim.height}`)
            .attr("preserveAspectRatio", "xMidYMid meet");

        // force directed graph setup
        this.node_data = [];
        this.edge_data = [];

        this.graph = d3.forceSimulation(this.node_data)
            .force("collide", d3.forceCollide().radius(5 * this.dim.node_radius))
            .force("center", d3.forceCenter(this.dim.width / 2, this.dim.height / 2))
            .force("link", d3.forceLink().links(this.edge_data).id(x => x.id))
            .force("x", d3.forceX(this.dim.width / 2))
            .force("y", d3.forceY(this.dim.height / 2))
            .on("tick", () => this.ticked());

        this.nodes = this.svg.append("g").attr("id", "nodes");
        this.edges = this.svg.append("g").attr("id", "edges");
        this.node_labels = this.svg.append("g").attr("id", "node-labels");
        this.edge_labels = this.svg.append("g").attr("id", "edge-labels");
    }

    ticked() {
        // node manipulations
        let nodes = this.nodes.selectAll("circle").data(this.node_data, d => d.id);

        nodes.enter().append("circle")
            .attr("r", this.dim.node_radius)
            .on("click", d => {
                console.log(d);
                d.selected = !d.selected;
            })
            .call(
                d3.drag()
                .on("start", d => this.drag_started(d))
                .on("drag", d => this.dragging(d))
                .on("end", d => this.drag_ended(d))
            )
            .append("title")
            .text(d => d.uri);

        nodes.exit().remove();

        nodes.classed("selected", d => d.selected)
            .attr("cx", d => d.x)
            .attr("cy", d => d.y);

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