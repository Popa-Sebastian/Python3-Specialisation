class City:
    def __init__(self, n, p, s):
        self.name = n
        self.population = p
        self.state = s
    def __str__(self):
        return '{}, {} (pop: {})'.format(self.name, self.population, self.state)

city_tuples = zip(cityNames, populations, states)
cities = [City(n, p, s) for (n, p, s) in city_tuples]