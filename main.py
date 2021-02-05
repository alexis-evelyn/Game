#!/bin/python3

# https://docs.python.org/3/library/pickle.html
# https://docs.python.org/3/library/hmac.html#module-hmac
import os
from math import pi, sin, cos
from typing import List

from doltpy.core import Dolt
from panda3d.core import Point3

from direct.actor.Actor import Actor
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.interval.IntervalGlobal import Sequence
from direct.gui.OnscreenText import OnscreenText


# From: https://docs.panda3d.org/1.10/python/introduction/tutorial/index
class MyApp(ShowBase):
    def __init__(self, repo: Dolt):
        ShowBase.__init__(self)

        # Load the environment model.
        self.scene = self.loader.loadModel("models/environment")

        # Re-parent the model to render.
        self.scene.reparentTo(self.render)

        # Apply scale and position transforms on the model.
        self.scene.setScale(0.25, 0.25, 0.25)
        self.scene.setPos(-8, 42, 0)

        # Add the spinCameraTask procedure to the task manager.
        self.taskMgr.add(self.spin_camera_task, "SpinCameraTask")

        # Load and transform the panda actor.
        self.pandaActor = Actor("models/panda-model", {"walk": "models/panda-walk4"})
        self.pandaActor.setScale(0.005, 0.005, 0.005)
        self.pandaActor.reparentTo(self.render)

        # Loop its animation.
        self.pandaActor.loop("walk")

        # Create the four lerp intervals needed for the panda to
        # walk back and forth.
        posInterval1 = self.pandaActor.posInterval(13, Point3(0, -10, 0), startPos=Point3(0, 10, 0))
        posInterval2 = self.pandaActor.posInterval(13, Point3(0, 10, 0), startPos=Point3(0, -10, 0))
        hprInterval1 = self.pandaActor.hprInterval(3, Point3(180, 0, 0), startHpr=Point3(0, 0, 0))
        hprInterval2 = self.pandaActor.hprInterval(3, Point3(0, 0, 0), startHpr=Point3(180, 0, 0))

        # Create and play the sequence that coordinates the intervals.
        self.pandaPace = Sequence(posInterval1, hprInterval1, posInterval2, hprInterval2, name="pandaPace")
        self.pandaPace.loop()

        random_tweet_query: str = '''
            select * from tweets order by rand() limit 1;
        '''

        tweet: List[dict] = repo.sql(query=random_tweet_query, result_format='csv')
        tweet_text = OnscreenText(text=tweet[0]["text"], pos=(-0.5, 0.02), scale=0.07)

    # Define a procedure to move the camera.
    def spin_camera_task(self, task):
        angle_degrees = task.time * 6.0
        angle_radians = angle_degrees * (pi / 180.0)
        self.camera.setPos(20 * sin(angle_radians), -20 * cos(angle_radians), 3)
        self.camera.setHpr(angle_degrees, 0, 0)

        return Task.cont


if __name__ == "__main__":
    working_directory: str = "working"
    tweets_directory: str = os.path.join(working_directory, "tweets")

    if not os.path.exists(working_directory):
        print("Creating Working Directory...")
        os.mkdir(working_directory)

    # TODO: Thread Me
    if not os.path.exists(tweets_directory):
        print("Cloning Tweets Repo...")
        repo: Dolt = Dolt.clone(remote_url="alexis-evelyn/presidential-tweets", new_dir=tweets_directory)
    else:
        repo: Dolt = Dolt(repo_dir=tweets_directory)

    app = MyApp(repo=repo)
    app.run()
