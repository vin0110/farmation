import numpy as np

Prices = [
    [8.33, 10.96, 9.25, 11.63, 13.29, 13.2, 6.62, 2.27, 8.25, 2.32, 2.0, 5.76],
    [6.72, 9.32, 10.5, 11.6, 2.31, 9.59, 5.64, 14.15, 13.2, 11.05, 7.55, 6.08],
    [1.71, 2.95, 2.23, 7.91, 4.42, 12.81, 13.26, 7.56, 9.91, 3.86, 12.64,
     1.64],
    [10.93, 8.38, 6.41, 7.7, 3.24, 4.28, 6.24, 10.67, 11.34, 3.79, 12.71,
     1.85],
    [5.4, 2.09, 4.12, 11.37, 13.08, 9.98, 4.72, 11.16, 5.74, 8.62, 10.04,
     6.79],
    [6.32, 8.44, 4.67, 2.32, 6.86, 14.75, 9.78, 9.85, 7.86, 12.95, 3.96, 9.0],
    [7.85, 2.8, 10.32, 3.86, 9.65, 2.97, 8.54, 12.58, 7.34, 12.12, 4.45, 6.63],
    [14.76, 10.12, 1.86, 4.02, 6.1, 7.13, 3.47, 5.74, 9.79, 2.01, 10.95,
     14.45],
    [2.9, 4.13, 10.09, 13.92, 7.36, 3.42, 4.76, 5.93, 6.0, 5.04, 13.72, 10.83],
    [7.76, 6.6, 5.46, 11.88, 4.2, 6.21, 12.59, 12.65, 11.54, 6.38, 13.53,
     12.21],
    [5.81, 13.02, 9.2, 5.72, 2.27, 14.38, 4.89, 9.84, 8.95, 2.38, 9.46, 8.95],
    [12.53, 13.94, 8.71, 2.9, 2.02, 2.7, 7.19, 7.26, 2.65, 6.31, 8.77, 10.51],
    [9.85, 9.95, 9.02, 2.82, 4.5, 4.58, 4.64, 3.7, 9.9, 8.09, 12.35, 9.13],
    [11.25, 12.64, 6.69, 2.09, 4.24, 11.89, 4.84, 2.26, 5.65, 11.7, 13.1,
     13.84]
]

Yields = [
    [1.91, 8.12, 6.88, 2.44, 9.22, 1.34, 3.97, 8.82, 8.87, 8.58, 8.41, 0.81],
    [1.83, 3.5, 3.47, 2.65, 3.86, 9.2, 1.01, 7.65, 4.71, 2.92, 3.54, 9.09],
    [7.5, 7.74, 8.98, 5.25, 4.44, 9.07, 4.53, 9.06, 7.59, 4.3, 3.34, 4.36],
    [8.43, 2.7, 6.32, 7.92, 1.41, 8.89, 5.21, 5.95, 4.71, 4.88, 8.27, 8.01],
    [5.7, 5.55, 9.75, 6.02, 3.92, 9.88, 7.99, 7.22, 7.81, 9.6, 4.55, 9.04],
    [1.48, 8.21, 7.35, 3.63, 8.38, 8.3, 2.62, 7.5, 5.55, 5.09, 5.96, 7.41],
    [3.27, 8.8, 2.43, 9.76, 4.84, 7.24, 3.01, 2.26, 5.37, 8.16, 5.9, 9.95],
    [4.86, 6.43, 7.41, 3.59, 2.54, 8.03, 5.13, 9.64, 4.49, 4.9, 6.15, 4.24],
    [8.89, 3.44, 9.06, 8.91, 4.07, 7.23, 2.18, 7.62, 5.68, 3.21, 9.22, 4.22],
    [8.02, 1.93, 9.12, 7.18, 6.88, 4.41, 8.01, 0.86, 0.89, 2.42, 2.6, 9.05],
    [9.98, 6.1, 1.95, 9.4, 2.23, 4.13, 1.0, 1.29, 3.68, 8.27, 9.58, 2.3],
    [3.51, 3.29, 4.14, 3.72, 4.26, 2.93, 1.45, 6.13, 7.28, 9.55, 8.81, 2.64],
    [9.5, 8.99, 2.28, 0.87, 9.37, 6.89, 9.46, 7.75, 9.63, 8.12, 1.18, 9.88],
    [3.81, 9.13, 8.03, 7.47, 4.32, 6.68, 2.98, 9.8, 2.99, 1.61, 4.12, 5.31],
    [3.85, 2.34, 2.36, 9.91, 4.14, 7.94, 1.82, 4.86, 4.15, 4.43, 5.87, 0.94],
    [9.16, 5.02, 7.31, 8.68, 3.74, 6.31, 2.74, 5.23, 0.91, 4.42, 5.45, 6.75],
    [3.78, 3.03, 6.15, 1.73, 2.18, 7.56, 7.88, 5.99, 9.61, 6.35, 4.73, 6.26],
    [4.59, 1.17, 8.4, 8.85, 3.65, 3.35, 7.56, 9.3, 0.76, 0.97, 5.94, 6.23],
    [8.89, 7.36, 0.95, 7.76, 9.21, 1.62, 8.01, 3.1, 2.25, 2.59, 8.16, 9.03],
    [6.99, 2.61, 2.46, 9.23, 7.03, 0.82, 4.89, 6.51, 4.33, 0.79, 4.29, 8.63]
]

Cost = [7.8, 9.92, 1.9, 3.92, 5.61, 7.59, 9.88, 6.04, 9.04, 9.29, 2.3, 3.37]



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
    min_std = (None, 1e10)
    min_q1 = (None, 1e10)
    max_q2 = (None, 0.)
    max_q3 = (None, 0.)

    crop_names = [c['name'] for c in crops]

    for partition in partitions:
        mean = 0.0
        q1 = 0.0
        q3 = 0.0

        valid = True
        for i in range(len(partition)):
            pacres = partition[i] * 100		# partition is by fields @@@
            if pacres < crops[i]['lo'] or \
               (crops[i]['hi'] > 0 and pacres > crops[i]['hi']):
                # not a valid partition
                valid = False
                break

        if not valid:
            continue

        nets = computeNets(crop_names, partition)
        mean = np.average(nets)
        std = np.std(nets)
        q1, q2, q3 = np.percentile(nets, [25, 50, 75])

        if mean > max_mean[1]:
            print('new mean', max_mean[1], mean)
            max_mean = (partition, mean)
        if std < min_std[1]:
            print('new std', min_std[1], std)
            min_std = (partition, std)
        if q1 < min_q1[1]:
            print('new q1', min_q1[1], q1)
            min_q1 = (partition, q1)
        if q2 > max_q2[1]:
            print('new q2', max_q2[1], q2)
            max_q2 = (partition, q2)
        if q3 > max_q3[1]:
            print('new q3', max_q3[1], q3)
            max_q3 = (partition, q3)

    return (max_mean, min_std, min_q1, max_q2, max_q3)


def computeNets(crop_names, partition, field_size=100):
    '''computer nets for a partition'''
    nets = []

    for y in range(len(Yields)):
        for p in range(len(Prices)):
            net = 0.0
            for part in range(len(partition)):
                if partition[part] == 0:
                    continue
                # @@@ need to find right crop
                crop = part
                per_acre = Prices[p][crop] * Yields[y][crop] - Cost[part]
                net += partition[part] * field_size * per_acre
            nets.append(net)

    return nets
