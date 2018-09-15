from django.template import Library, loader
from blog.models import BlogCategory
# Tag

register = Library()


@register.simple_tag()
def post_date_url(post, blog_index_page):
    post_date = post.date
    url = blog_index_page.url + blog_index_page.reverse_subpage(
        'post_by_date_slug',
        args=(
            post_date.year,
            '{0:02}'.format(post_date.month),
            '{0:02}'.format(post_date.day),
            post.slug,
        )
    )
    return url


'''@register.inclusion_tag('blog/components/tags_list.html', takes_context=True)
def tags_list(context, limit=None):
    blog_index_page = context['blog_index_page']
    tags = Tag.objects.all()
    if limit:
        tags = tags[:limit]
    return {'blog_index_page': blog_index_page, 'request': context['request'], 'tags': tags}
'''


@register.inclusion_tag('blog/components/categories_list.html', takes_context=True)
def categories_list(context):
    blog_index_page = context['blog_index_page']
    categories = BlogCategory.objects.all()
    return {'blog_index_page': blog_index_page, 'request': context['request'], 'categories': categories}
