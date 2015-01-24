from pyramid.response import Response
from pyramid.httpexceptions import HTTPSeeOther
import sqlalchemy as sa
import mimetypes

from .models import (
    Kitten,
    )


def worst(request):
    return {
        'kittens': request.db_session.query(Kitten).order_by(Kitten.votes.desc()).all()
    }


def see_choices(request):
    # We need two random kittens from the database. This is a surprisingly complex topic.
    # If we have only a few kittens, we could simply load them all in and do the random
    # selection in Python, but this quickly gets unwieldy.
    # There are a variety of ways to do random selection in SQL, with different
    # tradeoffs. See this article for details:
    # https://www.periscope.io/blog/how-to-sample-rows-in-sql-273x-faster.html

    # Since this is an example app and not something which needs to scale, we're going
    # to go with the very simple order-by-random option.
    kittens = request.db_session.query(Kitten).order_by(sa.func.random()).limit(2).all()
    kittens[0].views += 1
    kittens[1].views += 1
    return {
        'kittens': kittens
    }


def vote(request):
    # If we had set up a session, we could store the randomly selected kitten ids
    # in the session and only let viewers vote once per choice. Exercise for the reader!
    kitten_id = request.POST['kitten']
    # Also ignoring exceptions here; if the user enters a kitten id that does not exist,
    # a 500 error will result.
    kitten = request.db_session.query(Kitten).filter_by(id=kitten_id).one()
    kitten.votes += 1
    # would be better to generate a url using routes here! I just haven't set up
    # the routes yet.
    return HTTPSeeOther('/')


def kitten_photo(request):
    kitten_id = request.matchdict['kitten']
    kitten = request.db_session.query(Kitten).filter_by(id=kitten_id).one()

    content_type = mimetypes.types_map[kitten.file_extension]
    return Response(kitten.file_data, content_type=content_type)
