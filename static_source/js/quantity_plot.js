// set the dimensions and margins of the graph
var margin = {top: 10, right: 100, bottom: 60, left: 60},
    width = 530 - margin.left - margin.right,
    height = 300 - margin.top - margin.bottom;

// append the svg object to the body of the page
var svg = d3.select("#quantity_plot")
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform",
          "translate(" + margin.left + "," + margin.top + ")");

var linecolors = ['#f00', '#f80', '#0d0', '#00f', '#f0f', '#08f',
		  '#a00', '#aa0', '#0a0', '#00a', '#a0a', '#0aa',
		  '#800', '#880', '#080', '#008', '#808', '#088'];

// Add X axis
var x = d3.scaleLinear()
    .domain([0,100])
    .range([ 0, width ]);

svg.append("g")
    .attr("transform", "translate(0," + height + ")")
    .call(d3.axisBottom(x));

// Add Y axis
var y = d3.scaleLinear()
    .domain([0, Math.ceil(d3.max(data, function(d) { return +d.gross; }))])
    .range([ height, 0 ]);

// define the line
var priceline = d3.line()
    .x(function(d) { return x(d.quantity); })
    .y(function(d) { return y(d.gross); });
      
svg.append("g")
    .call(d3.axisLeft(y));

// nest the entries by year
var dataNest = d3.nest()
    .key(function(d) { return d.year; })
    .entries(data);

var cnt = 0;

// Loop through each year
dataNest.forEach(function(d) {
    // Add the line
    svg.append("path")
        .attr("class", "line")
	.attr("stroke", linecolors[cnt%linecolors.length])
	.attr("d", priceline(d.values));
    cnt++;
});

svg.selectAll("mydots")
    .data(dataNest)
    .enter()
    .append("circle")
    .attr("cx", width+18)
    .attr("cy", function(d,i){ return 18 + i*20})
    .attr("r", 6)
    .style("fill", function(d, i){ return linecolors[i%linecolors.length]});

svg.selectAll("mylabels")
    .data(dataNest)
    .enter()
    .append("text")
    .attr("x", width+30)
    .attr("y", function(d,i){ return 20 + i*20})
    .style("font", "14px sans-serif")
    .style("fill", function(d, i){ return linecolors[i%linecolors.length]})
    .text(function(d){ return d.key})
    .attr("text-anchor", "left")
    .style("alignment-baseline", "middle");

// x label
svg.append("text")
        .attr("x", width/2 )
        .attr("y", height + margin.top + 25)
        .style("text-anchor", "middle")
        .text("Hedge quantity (%)");

// y label
svg.append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 0 - margin.left)
        .attr("x", 0 - (height / 2))
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text("$ per bushel");
