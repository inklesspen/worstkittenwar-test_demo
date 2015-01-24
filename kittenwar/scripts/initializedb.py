import os
import sys
import transaction
import json
import requests

from pyramid.paster import (
    setup_logging,
    bootstrap,
    )

from pyramid.scripts.common import parse_vars

from ..models import (
    Kitten,
    Base,
    )


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_path> <json_path> [var=value]\n'
          '(example: "%s development.ini hippos.json")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 3:
        usage(argv)
    config_uri = argv[1]
    json_path = argv[2]
    options = parse_vars(argv[3:])
    setup_logging(config_uri)
    # Configure the application, so we can access the registry.
    env = bootstrap(config_uri, options=options)
    # Generate a DBSession using the sessionmaker:
    DBSession = env['registry']['db_sessionmaker']()
    # The SQLAlchemy engine is accessible as the session's bind.
    engine = DBSession.bind
    Base.metadata.create_all(engine)
    json_data = json.load(open(json_path))
    with transaction.manager:
        for kitten_data in json_data:
            kitten = Kitten(source_url=kitten_data['source_url'],
                            credit=kitten_data['credit'])
            r = requests.get(kitten_data['download_url'])
            if r.headers['content-type'] == 'image/jpeg':
                kitten.file_extension = '.jpeg'
            elif r.headers['content-type'] == 'image/png':
                kitten.file_extension = '.png'
            kitten.file_data = r.content
            DBSession.add(kitten)
    # Not strictly necessary, as everything gets unwound when main returns anyway.
    # But it's a good habit to keep.
    env['closer']()
