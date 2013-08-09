from django import template

register = template.Library()

@register.inclusion_tag('coupon.html')
def show_coupon(coupon):
    return {'coupon': coupon}

@register.inclusion_tag('category_filters.html')
def show_category_filters(categories, form_path):
    return {'categories': categories, 'form_path': form_path}
