from django.db import models
from wagtail.core.models import Page
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from base.blocks import BaseStreamBlock


class ClassIndexPage(Page):
    intro = StreamField(
        BaseStreamBlock(), verbose_name="Introduction to Trainings", blank=True
    )

    content_panels = Page.content_panels + [
        StreamFieldPanel('intro')
    ]

    # Allows child objects (e.g. BreadPage objects) to be accessible via the
    # template. We use this on the HomePage to display child items of featured
    # content
    def children(self):
        return self.get_children().specific().live()


class TrainingPage(Page):
    sub_title = models.CharField(max_length=100, blank=True, null=True)
    intro = models.CharField(max_length=250)
    body = StreamField(
        BaseStreamBlock(), verbose_name="Training Body", blank=True)
    header_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    content_panels = Page.content_panels + [
        FieldPanel('sub_title'),
        FieldPanel('intro'),
        StreamFieldPanel('body'),
        ImageChooserPanel('header_image')
    ]