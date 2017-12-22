#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()


from app import create_app, db
from app.models import Permission, User, Role, Follow, Post, Comment
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db,
                Permission=Permission, User=User, Role=Role, Follow=Follow,
                Post=Post, Comment=Comment)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test(coverage=False):
    '''
    run the unit tests.
    '''

    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)

    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary 单元测试覆盖概括.')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://{}/index.html'.format(covdir))
        COV.erase()


@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length], profile_dir=profile_dir)
    app.run()


@manager.command
def clearAlembic():
    # from flask_migrate import upgrade
    from app.models import Alembic
    Alembic.clear_A()


@manager.command
def deploy():
    """Run depolyment tasks"""
    from flask_migrate import upgrade
    from app.models import User, Role
    upgrade()
    Role.insert_roles()
    User.add_self_follows()

    u = User.query.filter_by(email='a35486882@qq.com').first()
    if u is None:
        u = User(email='a35486882@qq.com', password='l19910305', confirmed=True,
            username='梅酱', role=Role.query.filter_by(name='Administrator'))
        db.session.add(u)
        db.session.commit()
        u.add_self_follows()


@manager.command
def drop_db():
    db.drop_all()


if __name__ == '__main__':
    manager.run()

