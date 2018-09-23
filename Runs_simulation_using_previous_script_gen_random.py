import gen_random
import plot_data


for net in ['new_manhattan']:
	for period in [1.4, 1.5, 1.6, 1.7, 1.8]:
		gen_random.gen_random(net, period)
		plot_data.plot_data(net, period, 10)

# ['new_manhattan', 'manhattan', 'simple_T', 'spider', 'principal', 'cross', 'campinas']
# [0.3, 0.5, 1, 1.5, 2]
