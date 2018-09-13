from django.db import models
from django import forms
from wagtail.core.models import Page
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from modelcluster.fields import ParentalManyToManyField
from wagtail.images.edit_handlers import ImageChooserPanel
from base.blocks import BaseStreamBlock
from wagtail.snippets.models import register_snippet
from django.db.models import Count
from wagtail.contrib.routable_page.models import RoutablePageMixin, route


@register_snippet
class CoachCategory(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=80)

    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Coach Category"
        verbose_name_plural = "Coach Categories"


class CoachIndexPage(RoutablePageMixin, Page):
    intro = StreamField(
        BaseStreamBlock(), verbose_name="List of Trainers", blank=True
    )
    content_panels = Page.content_panels + [
        StreamFieldPanel('intro')
    ]

    # Allows child objects (e.g. BreadPage objects) to be accessible via the
    # template. We use this on the HomePage to display child items of featured
    # content

    def get_trainers(self):
        return CoachPage.objects.descendant_of(self).live()

    def children(self):
        return self.get_children().specific().live()

    def get_context(self, request, *args, **kwargs):
        # Update context to include only published posts, ordered by reverse-chron
        context = super(CoachIndexPage, self).get_context(request, *args, **kwargs)
        context['coach_index_page'] = self
        context['trainer_pages'] = self.trainer_pages
        context['available_categories'] = CoachCategory.objects.values('name', 'slug').annotate(Count('name'))[:5]
        return context

    @route(r'^category/(?P<category>[-\w]+)/$')
    def trainer_by_category(self, request, category, *args, **kwargs):
        self.search_type = 'category'
        self.search_term = category
        self.trainer_pages = self.get_trainers().filter(categories__slug=category)
        return Page.serve(self, request, *args, **kwargs)

    @route(r'^$')
    def trainer_list(self, request, *args, **kwargs):
        self.trainer_pages = self.get_trainers()
        return Page.serve(self, request, *args, **kwargs)


class CoachPage(Page):
    name = models.CharField(max_length=100, blank=True, null=True)
    intro = models.CharField(max_length=250)
    role = models.CharField(max_length=100, blank=True, null=True)
    desc = StreamField(BaseStreamBlock(), verbose_name="Description", blank=True)
    categories = ParentalManyToManyField('coach.CoachCategory', blank=True)

    header_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    content_panels = Page.content_panels + [
        FieldPanel('name'),
        FieldPanel('intro'),
        FieldPanel('role'),
        StreamFieldPanel('desc'),
        ImageChooserPanel('header_image'),
        FieldPanel('categories', widget=forms.CheckboxSelectMultiple)
    ]

    @property
    def coach_index_page(self):
        return self.get_parent().specific

    def get_context(self, request, *args, **kwargs):
        context = super(CoachPage, self).get_context(request, *args, **kwargs)
        context['coach_index_page'] = self.coach_index_page
        return context

