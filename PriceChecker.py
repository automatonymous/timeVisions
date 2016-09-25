import csv
import time
from lxml import html
from ebaysdk.finding import Connection as Finding
from ebaysdk.shopping import Connection as Shopping
import Inventory_Request as iR


def request_builder(search_term, itemFilters):  ## takes an individual search term, queries eBay, and returns a list of prices, or no data
	decoded_search_term = search_term.decode('utf-8', 'ignore')
	final_search_term = decoded_search_term.replace("&", '&amp;')
	_price_results = []
	try:
		api = Finding(config_file='ebay_api.yaml')
		response = api.execute('findItemsAdvanced', {'keywords': final_search_term, 'itemFilter': itemFilters})
		_response = response.dom()
		price_results = _response.xpath("//convertedCurrentPrice/text()")
	except BaseException as e:
		print('SKETTI!')
		response = ['No Data', 'No Data']
		return response
	else:
		for result in price_results:
			try:
				_price_results.append(float(result))
			except:
				_price_results.append(0.00)
	return _price_results

def file_write(_output):  ## pass a list/dict/iterable - writes to .csv - final output
	print('Writing '+str(len(_output))+' rows to .csv')
	with open('Search_Results.csv', 'w') as results:
		results_csv = csv.writer(results, dialect='excel', lineterminator='\n')
		results_csv.writerow(['Search Term', 'Our Price', 'High', 'Low', 'Average'])
		for row in _output:
			results_csv.writerow([row, _output[row][0], _output[row][1], _output[row][2], _output[row][3]])
	return 'Done'

def filters():  ## constructs filters for search
	item_filters = [{'name': 'ListingType', 'value': 'FixedPrice'},
					{'name': 'Condition', 'value': 'New'},
					{'name': 'BuyItNowAvailable', 'value': 'False'},
					{'name': 'ExcludeSeller', 'value': 'timevisions'},
					{'name': 'HideDuplicateItems', 'value': 'True'}
					#{'name': 'LocatedIn', 'value': ['US', 'DE', 'BR', 'RU'] }, 				# see what we want to use
					#{'name': 'ListedIn', 'value': ['US', 'DE', 'BR', 'RU'] }, 					# see what we want to use
					#{'name': 'AvailableTo', 'value': ['US', 'DE', 'BR', 'RU', 'GB'] },			# see what we want to use
					]
	return item_filters

def construction(_searches, _prices):  ## builds results as lists
	raw_data = {}
	count = 0
	total_count = str(len(_searches))
	itemFilters = filters()
	print 'Searching for items:'
	for term in _searches:
		raw_data[term] = []
		print(term.rjust(30, ' ')+'. . . '+str(count + 1).rjust(3, ' ')+' / '+total_count)
		raw_data[term].extend([float(_prices[count]), (request_builder(term, itemFilters))])
		count += 1
	return raw_data
	
def avg(any_list):
	_total = 0.0
	_count = 0.0
	_averg = 0.0
	for item in any_list:
		_total += float(item)
		_count += 1
	_averg = round(_total/_count, 2)
	return _averg
	
def median(any_list):
	longness = len(any_list)
	new_list = any_list.sort()
	med = 0
	if longness % 2 == 0:
		med = (new_list[longness/2]+new_list[(longness/2)+1])/2
	else:
		med = new_list[(longness/2)+.5]
	return med

def transformer(raw_data, search_terms):
	_output = {}
	print('Evaluating '+str(len(search_terms))+' rows of data...')
	counter = 0
	for term in search_terms:
		_output[term] = []
		try:
			maximum = max(raw_data[term][1])
		except:
			maximum = 0.00
		try:
			minimum = min(raw_data[term][1])
		except:
			minimum = 0.00
		try:
			average = avg(raw_data[term][1])
		except:
			average = 0.00
		try:
			_output[term].extend([raw_data[term][0], maximum, minimum, average])
		except:
			_output[term].extend(['Data loss','Data loss','Data loss','Data loss'])
	return _output

inventory_brands, inventory_models, inventory_prices = iR.get_the_data(iR.get_inventory_item_ids())
search_terms = iR.search_term_builder(inventory_brands, inventory_models)
raw_data = construction(search_terms, inventory_prices)
#print('Search Terms: '+str(len(search_terms))+'     Raw Data: '+str(len(raw_data)))
_output = transformer(raw_data, search_terms)
#print('Search Terms: '+str(len(search_terms))+'     Output: '+str(len(_output)))
print(file_write(_output))

