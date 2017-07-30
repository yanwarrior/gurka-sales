import factory
import random
from factory.django import DjangoModelFactory


class ProductFactory(DjangoModelFactory):

	@factory.sequence
	def sku(n):
		return 'SKU-%d' % n

	@factory.sequence
	def name(n):
		return 'PRODUCT-%d' % n

	base_price = factory.lazy_attribute(lambda o: random.randint(100, 2000))
	price = factory.lazy_attribute(lambda o: random.randint(1000, 20000))
	stock = factory.lazy_attribute(lambda o: random.randint(1, 100))
	stock_min = factory.lazy_attribute(lambda o: random.randint(1, 5))

	class Meta:
		model = 'sales.Product'


class OrderFactory(DjangoModelFactory):
	pass

