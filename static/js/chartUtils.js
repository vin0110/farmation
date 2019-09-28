
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
    points = [ [ triple[ 0 ], 0],
        [ triple[ 1 ], peakHeight ],
        [ triple[ 2 ], 0]
    ];
    return points
}

//Appends common options for triangle charts to 'options'.
function setTriChartOptions( stats, options ) {
    var hi = stats[ 'maxHi' ]
    var lo = stats[ 'minLo' ]
    var maxHeight = stats[ 'maxHeight' ]

    const HOR_PADDING_FACTOR = 0.05
    const VER_PADDING_FACTOR = 1.10

    // Determining bounds for X-axis.
    var horizOffset = ( hi - lo ) * HOR_PADDING_FACTOR 
    var xAxisUpperBound = Math.round( hi + horizOffset )
    var xAxisLowerBound = Math.round( lo - horizOffset )

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

function sleep( ms ) {
    return new Promise( resolve => setTimeout( resolve, ms ));
}

// Builds a rows.length x 4 array and sorts it by its first column. 
// This is needed for building a datable 
async function buildDataTable( triples, rows ) {

    var dtable = new google.visualization.DataTable();

    dtable.addColumn( 'number', 'value' )
    dtable.addColumn( 'number', 'Best worse case' )
    dtable.addColumn( 'number', 'Best expected' )
    dtable.addColumn( 'number', 'Best best case' )
    dtable.addColumn( {type:'string', role:'tooltip'} )

    var formatter = new Intl.NumberFormat( 'en-US', {
      style: 'currency',
      currency: 'USD',
    })

    for ( var i in triples ) {
        var triple = triples[ i ][ 'points' ]
        var baseIdx =  i * 3
        rows[ baseIdx     ][ 0 ]       = triple[ 0 ][ 0 ]
        rows[ baseIdx     ][ + i + 1 ] = triple[ 0 ][ 1 ]
        rows[ baseIdx     ][ 4 ]       = 'Min: '  + formatter.format( triple[ 0 ][ 0 ] )

        rows[ baseIdx + 1 ][ 0 ]       = triple[ 1 ][ 0 ]
        rows[ baseIdx + 1 ][ + i + 1 ] = triple[ 1 ][ 1 ]
        rows[ baseIdx + 1 ][ 4 ]       = 'Peak: ' + formatter.format( triple[ 1 ][ 0 ] )

        rows[ baseIdx + 2 ][ 0 ]       = triple[ 2 ][ 0 ]
        rows[ baseIdx + 2 ][ + i + 1 ] = triple[ 2 ][ 1 ]
        rows[ baseIdx + 2 ][ 4 ]       = 'Max: '  + formatter.format( triple[ 2 ][ 0 ] )
    }

    rows.sort( (a, b) => {
        if ( a[ 0 ] === b[ 0 ] ) {
            return 0
        } else { 
            return ( a[ 0 ] < b[ 0 ] ) ? -1 : 1
        }
    });

    rows.forEach( row => {
        dtable.addRow( row )
    })
 
    return dtable
}

// Given an array of triples 
async function setupMultiTriangle( triples, options ) {

    for ( var triple of triples ) {
        triple[ 'points' ] = getCoordinates( triple[ 'values' ] )
    }

    var stats = {
        'maxHi' : Math.max( ...triples.map( trip => trip[ 'values' ][ 2 ]) ),
        'minLo' : Math.min( ...triples.map( trip => trip[ 'values' ][ 0 ]) ),
        'maxHeight' : Math.max( ...triples.map( trip => trip[ 'points' ][ 1 ][ 1 ]) ),
        'minHeight' : Math.min( ...triples.map( trip => trip[ 'points' ][ 1 ][ 1 ]) ),
    }

    // Sets options for the bounds of the chart, which are dependent
    // on the values stores in 'stats'.
    setTriChartOptions( stats, options )


    var rows = Array.from( Array( 9 ), _ => Array( 5 ).fill( null ) );
    console.log( rows )
    var dtable = await buildDataTable( triples, rows )
    console.log( dtable )

    return dtable
}

async function setupTriangle( triple ) {
    // Converts [lo, peak, hi] to x-y coordinates. 
    triple = await getCoordinates( triple )

    // Adding annotations for points.
    triple[ 0 ].push( 'Minimum: ' + triple[ 0 ][ 0 ] )
    triple[ 1 ].push( 'Peak: ' + triple[ 1 ][ 0 ] ) 
    triple[ 2 ].push( 'Maximum: ' + triple[ 2 ][ 0 ] )

    var dtable = new google.visualization.DataTable();
    dtable.addColumn('number', 'value')
    dtable.addColumn('number', 'relative probability')
    dtable.addColumn( {type:'string', role:'tooltip'} )
    dtable.addRows( [
        triple[ 0 ],
        triple[ 1 ],
        triple[ 2 ]
    ]);
    return dtable
}

function drawChart( chartWrapper, chartType, dtable, options ) {
    chartWrapper.setChartType( chartType )
    chartWrapper.setDataTable( dtable ) 
    chartWrapper.setOptions( options )
    chartWrapper.draw()
}