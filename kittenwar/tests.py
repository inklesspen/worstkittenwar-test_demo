import unittest
import transaction

from pyramid import testing
from .models import MyModel, Base


class TestMyViewSuccessCondition(unittest.TestCase):
    def setUp(self):
        settings = {'sqlalchemy.url': 'sqlite:///:memory:'}
        self.config = testing.setUp(settings=settings)
        self.config.include('.models')
        self.db_session = self.config.registry['db_sessionmaker']()
        engine = self.db_session.bind
        Base.metadata.create_all(engine)
        with transaction.manager:
            model = MyModel(name='one', value=55)
            self.db_session.add(model)

    def tearDown(self):
        testing.tearDown()

    def test_passing_view(self):
        from .views import my_view
        request = testing.DummyRequest(db_session=self.db_session)
        info = my_view(request)
        self.assertEqual(info['one'].name, 'one')
        self.assertEqual(info['project'], 'kittenwar')


class TestMyViewFailureCondition(unittest.TestCase):
    def setUp(self):
        settings = {'sqlalchemy.url': 'sqlite:///:memory:'}
        self.config = testing.setUp(settings=settings)
        self.config.include('.models')
        self.db_session = self.config.registry['db_sessionmaker']()

    def tearDown(self):
        testing.tearDown()

    def test_failing_view(self):
        from .views import my_view
        request = testing.DummyRequest(db_session=self.db_session)
        info = my_view(request)
        self.assertEqual(info.status_int, 500)
