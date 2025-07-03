import pandas as pd
from faker import Faker
import random

fake = Faker()
Faker.seed(42)
random.seed(42)

brands = [    'zara', 'h&m', 'myntra', 'ajio', 'nykaa', 'amazon', 'flipkart',
        'shein', 'forever21', 'mango', 'uniqlo', 'nike', 'adidas', 'puma',
        'levis', 'tommy hilfiger', 'calvin klein', 'gucci', 'prada', 'chanel',
        'dior', 'versace', 'balenciaga', 'louis vuitton', 'hermes', 'burberry',
        'ralph lauren', 'armani', 'dolce gabbana', 'valentino', 'givenchy',
        'saint laurent', 'bottega veneta', 'celine', 'fendi', 'moschino',
        'off white', 'supreme', 'stone island', 'moncler', 'canada goose',
        'patagonia', 'north face', 'columbia', 'under armour', 'reebok',
        'converse', 'vans', 'new balance', 'asics', 'jordan', 'yeezy',
        'biba', 'w', 'global desi', 'fabindia', 'max fashion', 'lifestyle',
        'pantaloons', 'westside', 'reliance trends', 'shoppers stop',
        'central', 'brand factory', 'vero moda', 'only', 'jack jones',
        'selected', 'pieces', 'name it', 'vila', 'y.a.s', 'object',
        'mamalicious', 'junarose', 'carmakoma', 'noisy may', 'jdy',

        # New/Trending (2024–2025)
        'urbanic', 'suta', 'snitch', 'daisy', 'bewakoof', 'tata cliq',
        'zouk', 'nirvanaa styles', 'house of masaba', 'the label life',
        'styched', 'campus sutra', 'ek by ekta kapoor', 'the souled store',
        'march tee', 'tistabene', 'nush', 'folklore', 'postfold', 'zivame',
        'clovia', 'amanté', 'savlani', 'sazo', 'fable street', 'truebrowns',
        'paul and shark', 'koovs', 'alkemi', 'nush', 'rare rabbit',
        
        # Digital-First D2C
        'go colors', 'the pant project', 'thesvaya', 'bunaai', 'libas',
        'rangriti', 'rustorange', 'aachho', 'indya', 'melange',
        'fab alley', 'zouk', 'lavie', 'mast and harbour', 'here & now'  ]
products = [    'dress', 'top', 'shirt', 'blouse', 'tshirt', 't-shirt', 'tank top',
            'crop top', 'sweater', 'hoodie', 'cardigan', 'blazer', 'jacket',
            'coat', 'jeans', 'pants', 'trousers', 'leggings', 'shorts',
            'skirt', 'saree', 'kurti', 'salwar', 'lehenga', 'anarkali',
            'palazzo', 'churidar', 'dupatta', 'scarf', 'stole', 'shawl',
            'shoes', 'heels', 'sneakers', 'sandals', 'boots', 'flats',
            'bag', 'purse', 'handbag', 'backpack', 'clutch', 'sling bag',
            'jewelry', 'necklace', 'earrings', 'bracelet', 'ring', 'watch',
            'sunglasses', 'hat', 'cap', 'belt', 'scarf', 'tie', 'bow tie',
            'suit', 'formal wear', 'casual wear', 'party wear', 'ethnic wear',
            'western wear', 'indo western', 'fusion wear', 'traditional wear']
categories = ["Men", "Women", "Unisex","Kids"]
sub_categories = {
    "T-shirt": "Topwear", "Jeans": "Bottomwear", "Shirt": "Topwear", "Dress": "One-piece",
    "Jacket": "Outerwear", "Shorts": "Bottomwear", "Skirt": "Bottomwear", "Hoodie": "Outerwear"
}
payment_modes = ["Card", "Cash", "UPI", "Wallet"]
locations = [    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai",
    "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Surat",
    "Lucknow", "Chandigarh", "Indore", "Nagpur", "Bhopal",
    "Coimbatore", "Kochi", "Visakhapatnam", "Noida", "Gurgaon",
    "Ludhiana", "Kanpur", "Vadodara", "Raipur", "Patna"]
sizes=["XS","S","M","L","XL","XXL","XXXL"]
colors = ["Black", "White", "Blue", "Red", "Green", "Pink", "Yellow", "Beige"]
sales_channels = ["Online", "Offline", "App"]
# age_groups = ["18-24", "25-34", "35-44", "45-54", "55+"]
genders = ["Male", "Female", "Other"]
return_reasons = ["Defective", "Size Issue", "Changed Mind", "Damaged", "Late Delivery", "Color Mismatch"]


def generate_row(i):
    product = random.choice(products)
    brand = random.choice(brands)
    category = random.choice(categories)
    sub_category = sub_categories.get(product, "General")
    size = random.choice(sizes)
    color = random.choice(colors)
    price = random.randint(499, 2999)
    discount = random.choice([0, 10, 20, 30, 40])
    final_price = round(price * (1 - discount / 100), 2)
    date_of_sale = fake.date_between(start_date='-60d', end_date='today')
    quantity = random.randint(1, 5)
    payment_mode = random.choice(payment_modes)
    store_location = random.choice(locations)
    sales_channel = random.choice(sales_channels)
    customer_id = f"CUST{i:05d}"
   # customer_age_group = random.choice(age_groups)
    customer_gender = random.choice(genders)
    return_status = random.choice([True, False])
    return_reason = random.choice(return_reasons) if return_status else ""
    co2_saved = round(random.uniform(0.0, 5.0), 2) if return_status else 0.0
    rating = round(random.uniform(3.0, 5.0), 1)
    review_text = fake.sentence(nb_words=8) if random.random() < 0.5 else ""
    delivery_days = random.randint(1, 7)

    return [
        i + 1, date_of_sale, brand, product, category, sub_category, size, color, price,
        discount, final_price, quantity, payment_mode, store_location, sales_channel,
        customer_id, customer_gender, return_status, return_reason,
        co2_saved, rating, review_text, delivery_days
    ]

# Generate 500 rows
data = [generate_row(i) for i in range(1000)]

df = pd.DataFrame(data, columns=[
    "transaction_id", "date_of_sale", "brand", "product_name", "category", "sub_category",
    "size", "color", "price", "discount_percent", "final_price", "quantity", "payment_mode",
    "store_location", "sales_channel", "customer_id", "customer_gender",
    "return_status", "return_reason", "co2_saved", "rating", "review_text", "delivery_days"
])


# Save to CSV
df.to_csv("synthetic_retail_data.csv", index=False)

print("✅ Synthetic dataset created: synthetic_retail_data.csv")
