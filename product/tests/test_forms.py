


from product.forms import ReviewForm

def test_review_form_valid():
    form_data = {"content": "Excellent product", "rating": 5}
    form = ReviewForm(data=form_data)
    assert form.is_valid()


def test_review_form_invalid_rating():
    form_data = {"content": "Nice", "rating": 6}  # out of range
    form = ReviewForm(data=form_data)
    assert not form.is_valid()
    assert "rating" in form.errors


def test_review_form_missing_content():
    form_data = {"rating": 4}
    form = ReviewForm(data=form_data)
    assert not form.is_valid()
    assert "content" in form.errors
