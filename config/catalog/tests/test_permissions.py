import pytest
from django.test import RequestFactory

from catalog.permission import CatalogListDetailPermission


@pytest.mark.parametrize("method", ["GET", "HEAD", "OPTIONS"])
def test_catalog_permission_allows_safe_methods(method):
	request = RequestFactory().generic(method, "/api/v1/products/")
	permission = CatalogListDetailPermission()

	assert permission.has_permission(request, view=None) is True


@pytest.mark.parametrize("method", ["POST", "PUT", "PATCH", "DELETE"])
def test_catalog_permission_denies_write_methods(method):
	request = RequestFactory().generic(method, "/api/v1/products/")
	permission = CatalogListDetailPermission()

	assert permission.has_permission(request, view=None) is False
