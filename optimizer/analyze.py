import json
import numpy as np


def mkPartitions(size, width):
    '''partitions size elements into width buckets.
    for example mkPartitions(2, 2) returns [[0, 2], [1, 1], [2, 0]]
    '''
    partitions = []
    if width == 1:
        return [[size]]

    for i in range(size+1):
        subparts = mkPartitions(size - i, width - 1)
        for p in subparts:
            partitions.append([i] + p)
    return partitions


def positiveDistro(mu, sigma, limit=0.5, count=20, seed=None):
    '''produces a list of count many values using a normal distribution.
    if value is less than the limit, get another value.
    the seed is used to get repeatable values'''

    if seed:
        np.random.seed(seed)

    prices = np.random.normal(mu, sigma, count)
    # check for too small prices
    for i in range(count):
        while prices[i] < limit:
            prices[i] = np.random.normal(mu, sigma)

    # json cannot convert ndarray, convert to list
    return list(prices)


def cropDistro(prices, yields, cost):
    '''create discrete distribution of
    prices and yields then create the cross-product to get
    the overall prices. then look for the optimal solution.'''

    # create a discrete set of net profits
    nets = []
    for p in prices:
        for y in yields:
            nets.append(p*y - cost)

    mean = np.average(nets)
    std = np.std(nets)
    quartiles = np.percentile(nets, [25, 50, 75])
    histogram = np.histogram(nets, bins=6)

    # json cannot convert ndarray, convert to list
    # historgram is too complex for json, use pickle (and leave it alone)
    return (mean, std, list(quartiles), histogram)


def analyzeScenario(crops):
    '''analyze the scenario: find expected, pessimistic and optimistic'''
    if crops.count() > 4:
        raise ValueError('will not analyze more than 4 crops at this time')

    farm = crops.first().scenario.farm

    fields = [f.acreage for f in farm.fields.all()]

    partitions = mkPartitions(len(fields), crops.count())
    max_mean = (None, -1e10)
    min_std = (None, 1e10)
    min_q1 = (None, 1e10)
    max_q2 = (None, -1e10)
    max_q3 = (None, -1e10)

    # build price, yields, and cost arrays
    cropDict = {}
    crop_names = []
    plen = 100
    ylen = 100
    for crop in crops.all():
        thisDict = {}
        cropdata = crop.data
        crop_name = cropdata.name
        crop_names.append(crop_name)
        farmcrop = farm.crops.get(data=cropdata)
        prices = json.loads(cropdata.prices)
        thisDict['prices'] = prices
        yields = json.loads(cropdata.yields)
        y_override = farmcrop.yield_override * crop.yield_override
        thisDict['yields'] = list(map(lambda x: x*y_override, yields))
        thisDict['cost'] = cropdata.cost + farmcrop.cost_override +\
            crop.cost_override

        overs = []
        over_acres = 0
        for over in crop.price_overrides.all():
            median_yield = json.loads(cropdata.yield_stats)['median']
            acres = over.units*over.factor/median_yield
            over_acres += acres
            overs.append(dict(
                units=over.units,
                price=over.price,
                acres=acres))
        thisDict['overs'] = overs
        thisDict['over_acres'] = over_acres
        cropDict[crop_name] = thisDict

        plen = min(len(prices), plen)
        ylen = min(len(yields), ylen)

    for partition in partitions:
        mean = 0.0
        q1 = 0.0
        q3 = 0.0

        valid = True
        for i in range(len(partition)):
            pacres = partition[i] * fields[i]
            lo, hi = crops[i].limits()
            if pacres < lo or (hi > 0 and pacres > hi):
                # not a valid partition
                valid = False
                break
            if pacres < cropDict[crop_names[i]]['over_acres']:
                # there are not enough acres in this partition to
                # fulfill the price overrides
                valid = False
                break

        if not valid:
            continue

        nets = computeNets(partition, fields, crop_names, cropDict, plen, ylen)
        mean = np.average(nets)
        std = np.std(nets)
        q1, q2, q3 = np.percentile(nets, [25, 50, 75])

        if mean > max_mean[1]:
            max_mean = (partition, mean)
        if std < min_std[1]:
            min_std = (partition, std)
        if q1 < min_q1[1]:
            min_q1 = (partition, q1)
        if q2 > max_q2[1]:
            max_q2 = (partition, q2)
        if q3 > max_q3[1]:
            max_q3 = (partition, q3)

    return (max_mean, min_std, min_q1, max_q2, max_q3)


def computeNets(partition, fields, crop_names, cropDict, plen, ylen):
    '''computer nets for a partition'''
    nets = []

    for y in range(ylen):
        for p in range(plen):
            net = 0.0
            for part in range(len(partition)):
                if partition[part] == 0:
                    continue
                crop = cropDict[crop_names[part]]
                size = partition[part] * fields[part]
                yld = size * crop['yields'][y]
                cost = size * crop['cost']
                overUnits = 0
                overRevenue = 0.
                for over in crop['overs']:
                    overUnits += over['units']
                    overRevenue += over['price'] * over['units']
                otherRevenue = (yld - overUnits) * crop['prices'][p]
                gross = overRevenue + otherRevenue - cost
                net += gross
            nets.append(net)

    return nets


def describeData(data):
    '''data is a list of floats'''
    stats = {}
    stats['average'] = np.average(data)
    steps = np.percentile(data, [10, 25, 50, 75, 90])
    stats['10'] = steps[0]
    stats['q1'] = steps[1]
    stats['median'] = steps[2]
    stats['q3'] = steps[3]
    stats['90'] = steps[4]
    stats['std'] = np.std(data)

    return stats


def mkHistogram(data, bins=6):
    '''create a histogram'''
    counts, edges = np.histogram(data, bins=bins)
    # numpy.ndarray and numpy.int64 are not json serializable
    # convert ndarray to native list and int64 to native int
    a_counts = [i for i in map(int, list(counts))]
    return {'counts': a_counts, 'edges': list(edges), }


def trianglePoints(triple):
    lo, peak, hi = triple['lo'], triple['peak'], triple['hi']
    peakHeight = 2.0 / (hi - lo)
    points = {
        'lo': {'x': lo, 'y': 0.0},
        'peak': {'x': peak, 'y': peakHeight},
        'hi': {'x': hi, 'y': 0.0}
    }
    return points


'''
    Given an array of triples (lo, peak, hi), returns an object
    with the format:
        {
            'points': trianglePoints(triple),
            'stats': <stats on group triangles>}
        }
    Where 'stats' is a dict with statistics on the set of triples
    passed in. These statistics can be used for setting common
    options for plotting this group of triangles, like axis bounds.
'''
def getTriangles(triples):
    minValue = float('inf')
    maxValue = float('-inf')
    minHeight = float('inf')
    maxHeight = float('-inf')

    # Stores sets of triangle coordinates along with stats about the data.
    points = []

    for triple in triples:
        # Calculates coordinates for this triple.
        triangle = trianglePoints(triple)
        points.append(triangle)

        # Updates stats.
        if triple['lo'] < minValue:
            minValue = triple['lo']
        if triple['hi'] > maxValue:
            maxValue = triple['hi']
        if triangle['peak']['y'] > maxHeight:
            maxHeight = triangle['peak']['y']
        if triangle['peak']['y'] < minHeight:
            minHeight = triangle['peak']['y']

    triangles = {}

    # Adding array of triangle coordinate triples.
    triangles['points'] = points

    # Adding stats about the triangles.
    triangles['stats'] = {
            'minValue': minValue,
            'maxValue': maxValue,
            'minHeight': minHeight,
            'maxHeight': maxHeight
    }
    return triangles
