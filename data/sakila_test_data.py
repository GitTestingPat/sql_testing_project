"""
Test data module for Sakila database.
Contains expected values and test data for Sakila schema validation.
"""

# === Sakila Schema Information ===

SAKILA_TABLES = {
    'actor': {
        'columns': ['actor_id', 'first_name', 'last_name', 'last_update'],
        'primary_key': 'actor_id'
    },
    'address': {
        'columns': ['address_id', 'address', 'address2', 'district', 'city_id', 
                   'postal_code', 'phone', 'location', 'last_update'],
        'primary_key': 'address_id'
    },
    'category': {
        'columns': ['category_id', 'name', 'last_update'],
        'primary_key': 'category_id'
    },
    'city': {
        'columns': ['city_id', 'city', 'country_id', 'last_update'],
        'primary_key': 'city_id'
    },
    'country': {
        'columns': ['country_id', 'country', 'last_update'],
        'primary_key': 'country_id'
    },
    'customer': {
        'columns': ['customer_id', 'store_id', 'first_name', 'last_name', 'email',
                   'address_id', 'active', 'create_date', 'last_update'],
        'primary_key': 'customer_id'
    },
    'film': {
        'columns': ['film_id', 'title', 'description', 'release_year', 'language_id',
                   'original_language_id', 'rental_duration', 'rental_rate', 'length',
                   'replacement_cost', 'rating', 'special_features', 'last_update'],
        'primary_key': 'film_id'
    },
    'film_actor': {
        'columns': ['actor_id', 'film_id', 'last_update'],
        'primary_key': ['actor_id', 'film_id']
    },
    'film_category': {
        'columns': ['film_id', 'category_id', 'last_update'],
        'primary_key': ['film_id', 'category_id']
    },
    'film_text': {
        'columns': ['film_id', 'title', 'description'],
        'primary_key': 'film_id'
    },
    'inventory': {
        'columns': ['inventory_id', 'film_id', 'store_id', 'last_update'],
        'primary_key': 'inventory_id'
    },
    'language': {
        'columns': ['language_id', 'name', 'last_update'],
        'primary_key': 'language_id'
    },
    'payment': {
        'columns': ['payment_id', 'customer_id', 'staff_id', 'rental_id', 'amount',
                   'payment_date', 'last_update'],
        'primary_key': 'payment_id'
    },
    'rental': {
        'columns': ['rental_id', 'rental_date', 'inventory_id', 'customer_id',
                   'return_date', 'staff_id', 'last_update'],
        'primary_key': 'rental_id'
    },
    'staff': {
        'columns': ['staff_id', 'first_name', 'last_name', 'address_id', 'picture',
                   'email', 'store_id', 'active', 'username', 'password', 'last_update'],
        'primary_key': 'staff_id'
    },
    'store': {
        'columns': ['store_id', 'manager_staff_id', 'address_id', 'last_update'],
        'primary_key': 'store_id'
    }
}

SAKILA_VIEWS = [
    'actor_info',
    'customer_list', 
    'film_list',
    'nicer_but_slower_film_list',
    'sales_by_film_category',
    'sales_by_store',
    'staff_list'
]

SAKILA_CATEGORIES = [
    'Action', 'Animation', 'Children', 'Classics', 'Comedy',
    'Documentary', 'Drama', 'Family', 'Foreign', 'Games',
    'Horror', 'Music', 'New', 'Sci-Fi', 'Sports', 'Travel'
]

SAKILA_RATINGS = ['G', 'PG', 'PG-13', 'R', 'NC-17']

SAKILA_LANGUAGES = ['English', 'Italian', 'Japanese', 'Mandarin', 'French', 'German']

# Expected record counts (approximate - may vary slightly)
SAKILA_EXPECTED_COUNTS = {
    'actor': 200,
    'address': 603,
    'category': 16,
    'city': 600,
    'country': 109,
    'customer': 599,
    'film': 1000,
    'film_actor': 5462,
    'film_category': 1000,
    'inventory': 4581,
    'language': 6,
    'payment': 16049,
    'rental': 16044,
    'staff': 2,
    'store': 2
}

# Sample queries for testing
SAKILA_TEST_QUERIES = {
    'top_rented_films': """
        SELECT f.title, COUNT(r.rental_id) as rental_count
        FROM film f
        JOIN inventory i ON f.film_id = i.film_id
        JOIN rental r ON i.inventory_id = r.inventory_id
        GROUP BY f.film_id, f.title
        ORDER BY rental_count DESC
        LIMIT 10
    """,
    'revenue_by_category': """
        SELECT c.name as category, SUM(p.amount) as total_revenue
        FROM category c
        JOIN film_category fc ON c.category_id = fc.category_id
        JOIN film f ON fc.film_id = f.film_id
        JOIN inventory i ON f.film_id = i.film_id
        JOIN rental r ON i.inventory_id = r.inventory_id
        JOIN payment p ON r.rental_id = p.rental_id
        GROUP BY c.category_id, c.name
        ORDER BY total_revenue DESC
    """,
    'customer_rental_history': """
        SELECT c.first_name, c.last_name, COUNT(r.rental_id) as total_rentals
        FROM customer c
        LEFT JOIN rental r ON c.customer_id = r.customer_id
        GROUP BY c.customer_id, c.first_name, c.last_name
        ORDER BY total_rentals DESC
        LIMIT 10
    """,
    'films_by_rating': """
        SELECT rating, COUNT(*) as film_count
        FROM film
        GROUP BY rating
        ORDER BY film_count DESC
    """,
    'actor_film_count': """
        SELECT a.first_name, a.last_name, COUNT(fa.film_id) as film_count
        FROM actor a
        JOIN film_actor fa ON a.actor_id = fa.actor_id
        GROUP BY a.actor_id, a.first_name, a.last_name
        ORDER BY film_count DESC
        LIMIT 10
    """
}
