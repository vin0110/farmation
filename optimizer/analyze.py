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
    nFields, acreage = 10, 100  # @@@ simple 1000 acre farm
    nCrops = len(crops)

    partitions = mkPartitions(nFields, nCrops)
    max_mean = (None, 0.)
    min_q1 = (None, 1e10)
    max_q3 = (None, 0.)

    for p in partitions:
        mean = 0.0
        q1 = 0.0
        q3 = 0.0

        valid = True
        for i in range(len(p)):
            pacres = p[i] * 100		# partition is by fields @@@
            print('p', pacres, crops[i]['lo'], crops[i]['hi'])
            if pacres < crops[i]['lo'] or \
               (crops[i]['hi'] > 0 and pacres > crops[i]['hi']):
                # not a valid partition
                valid = False
                break

        if not valid:
            continue

        for i in range(nCrops):
            factor = acreage * p[i]
            mean += crops[i]['mean'] * factor
            q1 += crops[i]['q1'] * factor
            q3 += crops[i]['q3'] * factor

        if mean > max_mean[1]:
            print('new mean', max_mean[1], mean)
            max_mean = (p, mean)
        if q1 < min_q1[1]:
            print('new q1', min_q1[1], q1)
            min_q1 = (p, q1)
        if q3 > max_q3[1]:
            print('new q3', max_q3[1], q3)
            max_q3 = (p, q3)

    return (max_mean, min_q1, max_q3)
