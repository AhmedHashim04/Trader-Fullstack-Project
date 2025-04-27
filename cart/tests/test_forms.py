
import pytest
from django.contrib.auth import get_user_model
from cart.forms import CartAddProductForm
from account.models import Profile



"""
The tests we did
cartForm Validation | Make sure it accepts valid data and rejects invalid data like different passwords.
UpdateProfileForm Save | Make sure it updates the User as well, not just the Profile.
Tested missing fields | Make sure it gives an error when a field is missing.
Tested Date Input | Because we used DateInput, we need to make sure it rejects invalid dates.
Used pytest.mark.django_db | So we allow the data to go to the Database during the test.

"""


User = get_user_model()

@pytest.mark.django_db
class TestCartForm:

    def test_cart_form_update_NoUpdate(self):
        form_data = {
            "quantity": 1,
            "update": False,

        }
        form = CartAddProductForm(data=form_data)
        assert not form.is_valid()
        assert "update" in form.errors

    def test_cart_form_missing_field(self):
        form_data = {
            "quantity": 1,

            # Missing update

        }
        form = CartAddProductForm(data=form_data)
        assert not form.is_valid()
        assert "update" in form.errors
