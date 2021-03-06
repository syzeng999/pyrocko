from pyrocko.plot import response
from pyrocko.example import get_example_data

# download example data
get_example_data('test_response.resp')

# read data
resps, labels = response.load_response_information(
    'test_response.resp', 'resp')

# plot response and save image
response.plot(
    responses=resps, labels=labels, filename='test_response.png',
    fmin=0.001, fmax=400., dpi=75.)
