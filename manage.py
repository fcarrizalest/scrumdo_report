from flask_script import Manager

from scrum.scrumdoapi import create_app

from scrum.manage import CronCommand,LogCommand

manager = Manager(create_app())

manager.add_command('cron', CronCommand())

manager.add_command('log', LogCommand())



if __name__ == "__main__":
    manager.run()