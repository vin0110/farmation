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
    nFields = 10  # @@@ simple 1000 acre farm
    # acreage = 100

    nCrops = crops.count()
    farm = crops.first().scenario.farm

    partitions = mkPartitions(nFields, nCrops)
    max_mean = (None, 0.)
    min_std = (None, 1e10)
    min_q1 = (None, 1e10)
    max_q2 = (None, 0.)
    max_q3 = (None, 0.)

    # build price, yields, and cost arrays
    crop_names = []
    Prices = {}
    Yields = {}
    Costs = {}
    plen = 100
    ylen = 100
    for crop in crops.all():
        cropdata = crop.data
        crop_name = cropdata.name
        crop_names.append(crop_name)
        farmcrop = farm.crops.get(data=cropdata)
        Prices[crop_name] = json.loads(cropdata.prices)
        yields = json.loads(cropdata.yields)
        y_override = farmcrop.yield_override * crop.yield_override
        Yields[crop_name] = list(map(lambda x: x*y_override, yields))
        Costs[crop_name] = cropdata.cost
        plen = min(len(Prices[crop_name]), plen)
        ylen = min(len(Yields[crop_name]), ylen)

    for partition in partitions:
        mean = 0.0
        q1 = 0.0
        q3 = 0.0

        valid = True
        for i in range(len(partition)):
            pacres = partition[i] * 100		# partition is by fields @@@
            if pacres < crops[i].lo_acres or \
               (crops[i].hi_acres > 0 and pacres > crops[i].hi_acres):
                # not a valid partition
                valid = False
                break

        if not valid:
            continue

        nets = computeNets(partition, crop_names, Prices, Yields, Costs,
                           plen, ylen)
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


def computeNets(partition, crop_names, Prices, Yields, Costs, plen, ylen,
                field_size=100):
    '''computer nets for a partition'''
    nets = []

    for y in range(ylen):
        for p in range(plen):
            net = 0.0
            for part in range(len(partition)):
                if partition[part] == 0:
                    continue
                crop = crop_names[part]
                per_acre = Prices[crop][p] * Yields[crop][y] - Costs[crop]
                net += partition[part] * field_size * per_acre
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
