import pytest

from leads.fixtures import ShoppingCart


@pytest.fixture
def fixture_1():
    print('run-fixture-1')
    return 1

def test_example1(fixture_1):
    num = fixture_1
    assert num == 1
    
# Tests

def test_can_add_to_cart():
    cart = ShoppingCart()
    cart.add("apple")
    
    cart.size() == 1
    
    assert cart.size() == 1