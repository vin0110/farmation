
// Loads a serialized Scenario object, formats it and returns it.
async function loadScenarioData( scenario_pk ) {
    var scenData = await $.ajax({
        url: '/api/v1/scenario/' + scenario_pk +'/',
        type: 'GET',
        dataType: 'json'
    })

    // Pattern that matches only the iterable fields.
    var iterable = RegExp( '.*_(partition|triangle)' )
    for ( var key in scenData ) {
        if ( iterable.test( key ) ) {
            scenData[ key ] = JSON.parse( scenData[ key ])
            scenData[ key ] = scenData[ key ].map( val => Math.round( val ) ) 
        } 
    }

    return scenData
}

async function loadFarmCrop( farmcrop_pk ) {
    const farmCrop = await $.ajax({
        url: '/api/v1/farmcrop/' + farmcrop_pk + '/',
        type: 'GET',
        dataType: 'json'
    });

    return farmCrop
}
// Loads data for crops in a specific scenario and returns it.
async function loadCropData( cropdata_pk ) {
    const cropData = await $.ajax({
        url: '/api/v1/cropdata/pk/' + cropdata_pk + '/',
        type: 'GET',
        dataType: 'json'
    });

    return cropData
}

// Loads data for crops in a specific scenario and returns it.
async function loadScenCrop( crop_pk ) {
    const crop = await $.ajax({
        url: '/api/v1/crop/' + crop_pk +'/',
        type: 'GET',
        dataType: 'json'
    });

    return crop
}

async function loadScenarioCrops( scenario_pk ) {
    const cropList = await $.ajax({
        url: '/api/v1/scenario/listcrops/' + scenario_pk +'/',
        type: 'GET',
        dataType: 'json'
    });

    return cropList
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
            },
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

// Calling currencyFormatter.format( <some_number> ) will return 
// a string like $12.34.
var currencyFormatter = new Intl.NumberFormat( 'en-US', {
    style: 'currency',
    currency: 'USD',
})

// Builds a datatable for plotting a single triangular distribution
async function setupTriangle( triple, options, formatter, verticalLine ) {

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

    if ( verticalLine != undefined ) {
        dtable.addColumn( {type: 'string', role: 'annotation'} );
        dtable.addColumn( {type: 'string', role: 'annotationText'} );
    }

    dtable.addColumn('number', '')
    dtable.addColumn( {type:'string', role:'tooltip'} )

    if ( verticalLine != undefined ) {

        // Getting the y-coordinate of the triangle distribution at 
        // the x-coordinate of 'cost'.
        var intersect = getIntersection( triple[ 'points' ], verticalLine )

        for ( var row of triple[ 'points' ] ) {
            row.splice( 1, 0, null )
            row.splice( 1, 0, null )
        }

        var formattedCost = formatter.format( verticalLine )
        dtable.addRow( triple[ 'points' ][ 0 ] )
        if ( verticalLine <= triple[ 'points' ][ 1 ][ 0 ] ) {
            dtable.addRow( [ verticalLine, 'Cost', 'Cost (dollar / acre): ' + formattedCost, intersect, formattedCost ] )
            dtable.addRow( triple[ 'points' ][ 1 ] )
        } else {
            dtable.addRow( triple[ 'points' ][ 1 ] )
            dtable.addRow( [ verticalLine, 'Cost', 'Cost (dollar / acre): ' + formattedCost, intersect, formattedCost ] )
        }
        dtable.addRow( triple[ 'points' ][ 2 ] )
    } else { 
        dtable.addRows( [
            triple[ 'points' ][ 0 ],
            triple[ 'points' ][ 1 ],
            triple[ 'points' ][ 2 ]
        ]);
    }
    return dtable
}

function getIntersection( points, cost ) {
    if ( cost < points[ 0 ][ 0 ] || cost > points[ 2 ][ 0 ] ) {
        return points[ 1 ][ 1 ]
    } else if ( cost < points[ 1 ][ 0 ] ) {
        var slope = ( points[ 1 ][ 1 ] - points[ 0 ][ 1 ] ) /
                    ( points[ 1 ][ 0 ] - points[ 0 ][ 0 ] )
        return slope * ( cost - points[ 1 ][ 0 ] ) + points[ 1 ][ 1 ]
    } else if ( cost > points[ 1 ][ 0 ] ) {
        var slope = ( points[ 2 ][ 1 ] - points[ 1 ][ 1 ] ) /
                    ( points[ 2 ][ 0 ] - points[ 1 ][ 0 ] )
        return slope * ( cost - points[ 1 ][ 0 ] ) + points[ 1 ][ 1 ]
    }
}

// Given a ChartWrapper, its type ('AreaChart', 'Histogram', etc), a 
// datatable and options object, this draws or redraws the chart.
function drawChart( chartWrapper, chartType, dtable, options ) {
    chartWrapper.setChartType( chartType )
    chartWrapper.setDataTable( dtable ) 
    chartWrapper.setOptions( options )
    chartWrapper.draw()
}

var grossOptions = {
    hAxis: {
        gridlines: {
            count: 5
        },
        minorGridlines: {
            count: 0
        },
        backgroundColor: { fill:'transparent' },
        format: 'currency',
    },
    vAxis: {
        textPosition: 'none',
        gridlines: {
            count: 0
        }
    },
    legend: {
        position: 'none'
    },
    annotations: {
        style: 'line',
        stem: {
            color: 'red',
        }
    },
}

const croptypes = {
    FARM_CROP: 'farmcrop',
    SCEN_CROP: 'crop',
    CROP_DATA: 'cropdata',
}
// Draws triangular plots in every div with class 'crop-charts'.
async function drawCropCharts( htmlClass, croptype ) {
    var loadCropFnc
    switch( croptype ) {
        case croptypes.FARM_CROP:
            loadCropFnc = loadFarmCrop
            break;

        case croptypes.SCEN_CROP:
            loadCropFnc = loadScenCrop
            break;

        default:
            console.error( "Invalid croptype in drawCropCharts()!")
    }

    // Locates the generated crop chart divs.
    var cropChartDivs = document.getElementsByClassName( htmlClass )

    var chartWrappers = []
    var cropPks = []

    // Iterates through divs. Creates ChartWrappers and 
    // builds list of scenario crops' primary keys.
    for ( var i = 0; i < cropChartDivs.length; i++ ) {
    currDivId = cropChartDivs.item( i ).id

    // Each div ID is formatted as 'cropCharts_<crop_pk>'.
    cropPk = parseInt( currDivId.split( '_' )[ 1 ] )
    cropPks.push( cropPk )

    chartWrappers[ cropPk ] = new google.visualization.ChartWrapper({
        containerId: currDivId
    });
    }

    // Formats numbers as US dollars.
    var priceFormatter = new Intl.NumberFormat( 'en-US', {
    style: 'currency',
    currency: 'USD',
    })

    // For each Crop in the Scenario, draws a graph.
    cropPks.forEach( async (crop_pk) => {
    try {
        crop = await loadCropFnc( crop_pk )
    } catch ( error ) {
        console.log( error )
    }

    var grossProfit = {
        'values' : crop[ 'gross' ]
    }

    setupTriangle( grossProfit, grossOptions, priceFormatter, crop[ 'cost' ]).
        then( cropTable => drawChart( chartWrappers[ crop_pk ], 'AreaChart', cropTable, grossOptions ))
    })
}