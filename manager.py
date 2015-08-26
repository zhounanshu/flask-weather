#!usr/bin/env python
# -*- coding: utf-8 -*-
from app import *
from flask.ext.script import Manager, Shell
from instance.config import *

cnf = ProducionConfig
app = create_app(cnf)
manager = Manager(app)


def make_shell_context():
    return dict(app=app)


manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.command
def deploy():
    """Run deployment tasks."""
    pass


if __name__ == '__main__':
    manager.run()
