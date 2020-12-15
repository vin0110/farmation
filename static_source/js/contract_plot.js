// set the dimensions and margins of the graph
var margin = {top: 10, right: 100, bottom: 60, left: 60},
    width = 530 - margin.left - margin.right,
    height = 300 - margin.top - margin.bottom;

// append the svg object to the body of the page
var svg = d3.select("#contract_plot")
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var linecolors = ['#f00', '#f80', '#0d0', '#00f', '#f0f', '#08f',
		  '#a00', '#aa0', '#0a0', '#00a', '#a0a', '#0aa',
		  '#800', '#880', '#080', '#008', '#808', '#088'];

// nest the entries by month
var dataNest = d3.nest()
    .key(function(d) { return d.month; })
    .entries(data);

// Add X axis
var x = d3.scaleLinear()
    .domain([])
    .range([ 0, width ]);

var skip = width / data.length;

svg.append("g")
    .attr("transform", "translate(0," + height + ")")
    .call(d3.axisBottom(x));

// Add Y axis
var y = d3.scaleLinear()
    .domain([0, Math.ceil(d3.max(data, function(d) { return +d.max; }))])
    .range([ height, 0 ]);

svg.append("g")
    .call(d3.axisLeft(y));

// vertical lines
svg.selectAll("vertical")
    .data(data)
    .enter()
    .append("line")
    .attr("x1", function(d,i) {return 30 + skip*i})
    .attr("x2", function(d,i) {return 30 + skip*i})
    .attr("y1", function(d) { return y(d.min)} )
    .attr("y2", function(d) { return y(d.max)} )
    .attr("stroke", "black");

// box
svg.selectAll("boxes")
    .data(data)
    .enter()
    .append("rect")
    .attr("x", function(d,i) {return 10 + skip*i})
    .attr("y", function(d) {return y(d.q3)})
    .attr("height", function(d) { return y(d.q1)-y(d.q3)} )
    .attr("width", function(d) { return 40} )
    .attr("stroke", "black")
    .style("fill", "#69b3a2");

// mean
svg.selectAll("mean")
    .data(data)
    .enter()
    .append("line")
    .attr("x1", function(d,i) {return 10 + skip*i})
    .attr("x2", function(d,i) {return 50 + skip*i})
    .attr("y1", function(d) { return y(d.mean)} )
    .attr("y2", function(d) { return y(d.mean)} )
    .attr("stroke", "red");

// median
svg.selectAll("median")
    .data(data)
    .enter()
    .append("line")
    .attr("x1", function(d,i) {return 10 + skip*i})
    .attr("x2", function(d,i) {return 50 + skip*i})
    .attr("y1", function(d) { return y(d.med)} )
    .attr("y2", function(d) { return y(d.med)} )
    .attr("stroke", "black");

// x labels
svg.selectAll('xlabels')
    .data(data)
    .enter()
    .append("text")
    .attr("x", function(d,i) {return 30 + skip*i})
    .attr("y", height + margin.top + 25)
    .style("text-anchor", "middle")
    .text(function(d) { return d.month });


/*
// x label
svg.append("text")
        .attr("x", width/2 )
        .attr("y", height + margin.top + 25)
        .style("text-anchor", "middle")
        .text("Hedge quantity (%)");
*/

// y label
svg.append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 0 - margin.left)
        .attr("x", 0 - (height / 2))
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text("$ per bushel");
