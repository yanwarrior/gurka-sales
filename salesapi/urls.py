from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^products/$', views.ProductList.as_view(), name='list'),
	url(r'^delall/products/$', views.ProductDeleteBulk.as_view(), name='delete-bulk'),
	url(r'^products/(?P<sku>[\w-]+)/$', views.ProductDetail.as_view(), name='detail'),
	url(r'^orders/$', views.OrderList.as_view(), name='order-list'),
	url(r'^orders/(?P<order_number>[\w-]+)/$', views.OrderDetail.as_view(), name='order-list'),
	url(r'^report/products/stock/$', views.ReportProductStockMin.as_view(), name='report-product-stock'),
	url(r'^reports/omzet/$', views.ReportOmzet.as_view(), name='report_omzet'),
]