from django import template
from socialMedia.models import Reaction  # import your Reaction model

register = template.Library()

@register.filter
def check_reaction_type(post, user_id):
    post_reactions = Reaction.objects.filter(post=post, user_id=user_id)
    if post_reactions.exists():
        return post_reactions.first().reaction
    else:
        return None
