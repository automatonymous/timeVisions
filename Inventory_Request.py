from lxml import html
from ebaysdk.finding import Connection as Finding
from ebaysdk.shopping import Connection as Shopping
	
def get_inventory_item_ids():  ## queries timevisions' inventory, returns itemIds
	print 'Generating Inventory',
	inventory_item_ids = []
	try:
		api = Finding(config_file='ebay_api.yaml')
		response = api.execute('findItemsIneBayStores', {'storeName': 'Time-Visions-Watches'})  # ebay store find thing
		pages = response.dom()
		pages_ = int(pages.xpath("//totalPages/text()")[0])
		for page in range(1, pages_+1):
			response = api.execute('findItemsIneBayStores', 
			{'storeName': 'Time-Visions-Watches',
			 'paginationInput': {'entriesPerPage':100, 'pageNumber':page}})
			inventory = response.dom()
			inventory_ = inventory.xpath("//itemId/text()")
			for i in inventory_:
				inventory_item_ids.append(i)
			print '.',
		print '.'
	except BaseException as e:
		response = [e, 'No Data']
		return response
	return inventory_item_ids

def get_the_data(inventory_item_ids):
	inventory_brands = []
	inventory_models = []
	inventory_prices = []
	print_counter = 1
	print_total = str(len(inventory_item_ids))
	api = Shopping(config_file='ebay_api.yaml')
	for item in inventory_item_ids:
		print('Getting details for listing  - '+str(print_counter).rjust(4, ' ')+' / '+print_total+' --- '+item)
		_response = api.execute('GetSingleItem', {'ItemID':item, 'IncludeSelector': 'ItemSpecifics'})
		converted_response = _response.dom()
		## this must not transmit empty list nodes, the if statement checks for empty lists... empty lists are 'falsy'
		if not converted_response.xpath("//NameValueList[Name ='Brand']/Value/text()"):
			inventory_brands += ['No brand here =/']
		else:
			inventory_brands += converted_response.xpath("//NameValueList[Name ='Brand']/Value/text()")
		if not converted_response.xpath("//NameValueList[Name ='Model']/Value/text()"):
			inventory_models += ['No model here =/']
		else:
			inventory_models += converted_response.xpath("//NameValueList[Name ='Model']/Value/text()")
		if not converted_response.xpath("//ConvertedCurrentPrice/text()"):
			inventory_prices += ['No price here =/']
		else:
			inventory_prices += converted_response.xpath("//ConvertedCurrentPrice/text()")
		print_counter += 1
	return inventory_brands, inventory_models, inventory_prices

def search_term_builder(inventory_brands, inventory_models):
	search_terms = []
	records = len(inventory_brands)
	for i in range(0, records):
		search_terms.append(str(inventory_brands[i])+' '+str(inventory_models[i]))
	print('Preparing to search '+str(len(search_terms))+' items...')
	return search_terms