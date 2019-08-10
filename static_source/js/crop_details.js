var chartA = c3.generate({
    bindto: '#chartA',
    data: {
      columns: [
        ['data1', 10, 20, 10, 30, 50, 40],
        ['data2', 50, 20, 10, 40, 15, 25]
      ]
    }
});