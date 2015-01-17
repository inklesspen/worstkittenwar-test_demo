import os
import sys
import transaction

from pyramid.paster import (
    setup_logging,
    bootstrap,
    )

from pyramid.scripts.common import parse_vars

from ..models import (
    MyModel,
    Base,
    )


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    # Configure the application, so we can access the registry.
    env = bootstrap(config_uri, options=options)
    # Generate a DBSession using the sessionmaker:
    DBSession = env['registry']['db_sessionmaker']()
    # The SQLAlchemy engine is accessible as the session's bind.
    engine = DBSession.bind
    Base.metadata.create_all(engine)
    with transaction.manager:
        model = MyModel(name='one', value=1)
        DBSession.add(model)
    # Not strictly necessary, as everything gets unwound when main returns anyway.
    # But it's a good habit to keep.
    env['closer']()
