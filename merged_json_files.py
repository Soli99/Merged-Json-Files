import json

def manipulate_and_merge(chip7_data, istore_data, radiopop_data, output_file_path):
    # Add the suffix (name of respective sites) to 'price' and 'url' in all JSON files
    for suffix, product_list in [('chip7', chip7_data), ('istore', istore_data), ('radiopop', radiopop_data)]:
        for category, products in product_list.items():
            for product in products:
                # Check if 'price' key exists before accessing it
                if 'price' in product:
                    product[f'price_{suffix}'] = float(product.pop('price'))
                product[f'url_{suffix}'] = product.pop('url', None)

    # Create a new dictionary to store the modified istore data
    modified_istore_data = {}

    # Merge the data from istore, chip7, and radiopop based on the common keys (e.g., SKU, name, date)
    for category_key, istore_products in istore_data.items():
        modified_istore_data[category_key] = []

        for istore_product in istore_products:
            # Find corresponding product in chip7_data
            matching_chip7_products = [
                chip7_product for chip7_product in chip7_data.get(category_key, [])
                #if chip7_product.get('sku') == istore_product.get('sku') and 
                if chip7_product.get('date') == istore_product.get('date')
            ]
            if matching_chip7_products:
                chip7_product = matching_chip7_products[0]
                # Add price_chip7 and url_chip7 to istore_data
                istore_product['price_chip7'] = chip7_product.get('price_chip7', None)
                istore_product['url_chip7'] = chip7_product.get('url_chip7', None)

            # Find corresponding product in radiopop_data
            matching_radiopop_products = [
                radiopop_product for radiopop_product in radiopop_data.get(category_key, [])
                
                #if radiopop_product.get('name') == istore_product.get('name') and 
                if radiopop_product.get('date') == istore_product.get('date')
            ]
            if matching_radiopop_products:
                radiopop_product = matching_radiopop_products[0]
                # Add price_radiopop, url_radiopop, and characteristics from radiopop_data to istore_data
                istore_product['price_radiopop'] = float(radiopop_product.get('offers', {}).get('price'))
                istore_product['url_radiopop'] = radiopop_product.get('offers', {}).get('url')
                istore_product['characteristics'] = {
                        key: value for key, value in radiopop_product.get('characteristics', {}).items() if key != 'Warranty'
                #}key: value for key, value in radiopop_product.items() if key not in ['name', 'date', 'image', 'offers']
                }

            # Store modified istore product
            modified_istore_data[category_key].append(istore_product)

    # Save the modified 'istore_data' to a new file
    with open(output_file_path, 'w', encoding='utf-8') as istore_file_modified:
        json.dump(modified_istore_data, istore_file_modified, ensure_ascii=False, indent=4)
    
    print(f"Values added and saved to {output_file_path}")
    return modified_istore_data

# Example usage
with open('output_all_data_chip7.json', 'r', encoding='utf-8') as chip7_file:
    chip7_data = json.load(chip7_file)

with open('output_all_data_istore.json', 'r', encoding='utf-8') as istore_file:
    istore_data = json.load(istore_file)

with open('output_all_data_radiopop.json', 'r', encoding='utf-8') as radiopop_file:
    radiopop_data = json.load(radiopop_file)

output_file_path = 'merged_files.json'  # Change this to your desired file path
result = manipulate_and_merge(chip7_data, istore_data, radiopop_data, output_file_path)
