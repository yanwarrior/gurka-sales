import json

from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status

from salesapi.tests.factories import ProductFactory

from sales.models import Product


class TestProductsV1(APITestCase):

	def setUp(self):
		for _ in range(3):
			ProductFactory()

	def test_product_list(self):
		response = self.client.get(
			'/api-sales/products/'
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(json.loads(response.content.decode('utf-8'))), 3)
	
	def test_product_create(self):
		data = {
			"sku": "P0010",
			"name": "Ciki Ball",
			"base_price": 2000,
			"price": 1500,
			"stock": 34,
			"stock_min": 3
		}

		response = self.client.post(
			'/api-sales/products/',
			data,
			format='json'
		)

		product = Product.objects.get(sku="P0010")
		expected = 'Ciki Ball'

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(product.name, expected)

	def test_product_detail(self):
		product = Product.objects.first()
		response = self.client.get(f'/api-sales/products/{product.sku}/')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_product_detail_update(self):

		product = Product.objects.first()
		data = {
		    "name": "Ciki Ball",
		    "base_price": 4000,
		    "price": 1300,
		    "stock": 20,
		    "stock_min": 5
		}	

		response = self.client.put(
			f'/api-sales/products/{product.sku}/',
			data,
			format='json'
		)

		product_name_expected = "Ciki Ball"
		product_base_price_expected = 4000
		product_price_expected = 1300
		product_stock_expected = 20
		product_stock_min_expected = 5

		product_from_response = json.loads(
			response.content.decode('utf-8')
		)

		self.assertEqual(response.status_code, 
			status.HTTP_200_OK)

		self.assertEqual(product_from_response.get('name'), 
			product_name_expected)

		self.assertEqual(product_from_response.get('base_price'), 
			product_base_price_expected)

		self.assertEqual(product_from_response.get('price'), 
			product_price_expected)

		self.assertEqual(product_from_response.get('stock'), 
			product_stock_expected)

		self.assertEqual(product_from_response.get('stock_min'), 
			product_stock_min_expected)

	def test_product_detail_delete(self):
		product = Product.objects.first()

		response = self.client.delete(
			f'/api-sales/products/{product.sku}/',
		)

		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)