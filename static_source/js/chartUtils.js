
// Loads a serialized Scenario object, formats it and returns it.
async function loadScenarioData( scenario_pk ) {
    var scenarioData = await $.ajax({
        url: 'http://localhost:8000/api/v1/scenario/' + scenario_pk,
        type: 'GET',
        dataType: 'json'
    })

    var floatKeys = [ 
        'min', 'max', 'peak', 'max_partition', 'min_partition', 'peak_partition' 
    ]

    // Converting JSON to arrays and floats to ints, but only for
    // the values mapped to by 'floatKeys'.
    for (var key of floatKeys) {
        scenarioData[ key ] = JSON.parse( scenarioData[ key ])
        scenarioData[ key ] = scenarioData[ key ].map( val => Math.round( val ) ) 
    }

    return scenarioData
}

// Loads data for crops in a specific scenario and returns it.
async function loadCropData( scenario_pk ) {
    const cropData = await $.ajax({
        url: 'http://localhost:8000/api/v1/scenario/crops/' + scenario_pk,
        type: 'GET',
        dataType: 'json'
    })

    return cropData
}

// Returns coordinates for a triangle distribution from a 
// passed triple of [lo, peak, hi].
function getCoordinates( triple ) {
    base = triple[ 2 ] - triple[ 0 ]
    peakHeight = 2.0 / base
    points = [ 
        [ triple[ 0 ], 0],
        [ triple[ 1 ], peakHeight ],
        [ triple[ 2 ], 0]
    ];
    return points
}

//Appends common options for triangle charts to 'options'.
function setTriChartOptions( triples, options ) {

    var hi = Math.max( ...triples.map( trip => trip[ 'values' ][ 2 ]) )
    var lo = Math.min( ...triples.map( trip => trip[ 'values' ][ 0 ]) )
    var maxHeight = Math.max( ...triples.map( trip => trip[ 'points' ][ 1 ][ 1 ]) )

    const HOR_PADDING_FACTOR = 0.05
    const VER_PADDING_FACTOR = 1.10

    // Determining bounds for X-axis.
    var horizOffset = ( hi - lo ) * HOR_PADDING_FACTOR 
    var xAxisUpperBound = hi + horizOffset
    var xAxisLowerBound = lo - horizOffset

    // Determining upper bound for Y-axis
    var yAxisUpperBound = maxHeight * VER_PADDING_FACTOR

    // Appends additional options for the horizonatal axis.
    options[ 'hAxis' ] = {
        ...options[ 'hAxis' ],
        ...{
            viewWindow : {
                min: xAxisLowerBound,
                max: xAxisUpperBound
            }
        }
    }

    // Appends additional options for the vertical axis.
    options[ 'vAxis' ] = {
        ...options[ 'vAxis' ],
        ...{
            viewWindow: {
                max: yAxisUpperBound
            }
        }
    }
}

// Builds a datatable for plotting a single triangular distribution
async function setupTriangle( triple, options, formatter ) {

    // Converts [lo, peak, hi] to x-y coordinates. 
    triple[ 'points' ] = await getCoordinates( triple[ 'values' ])

    setTriChartOptions( [ triple ], options )

    // Adding annotations for points.
    triple[ 'points' ][ 0 ].push( 'Minimum: ' + formatter.format( triple[ 'points' ][ 0 ][ 0 ] ) )
    triple[ 'points' ][ 1 ].push( 'Peak: '    + formatter.format( triple[ 'points' ][ 1 ][ 0 ] ) )
    triple[ 'points' ][ 2 ].push( 'Maximum: ' + formatter.format( triple[ 'points' ][ 2 ][ 0 ] ) )

    // Building the datatable.
    var dtable = new google.visualization.DataTable();
    dtable.addColumn('number', 'value')
    dtable.addColumn('number', '')
    dtable.addColumn( {type:'string', role:'tooltip'} )
    dtable.addRows( [
        triple[ 'points' ][ 0 ],
        triple[ 'points' ][ 1 ],
        triple[ 'points' ][ 2 ]
    ]);
    return dtable
}

// Given a ChartWrapper, its type ('AreaChart', 'Histogram', etc), a 
// datatable and options object, this draws or redraws the chart.
function drawChart( chartWrapper, chartType, dtable, options ) {
    chartWrapper.setChartType( chartType )
    chartWrapper.setDataTable( dtable ) 
    chartWrapper.setOptions( options )
    chartWrapper.draw()
}
