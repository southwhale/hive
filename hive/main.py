import os
from datetime import datetime
from json import load
from typing import Text, Dict, List

from ctpbee.date import trade_dates

from hive.log import logger
from hive.task import Task, TaskStatus, TaskType


class Hive(object):
    def __init__(self):
        self.task_set: {Text: Task} = {}
        self.__wait_task_queue = []
        self._day = []

    def init_from_config(self):
        """ 从配置中读取Task任务 """

    @staticmethod
    def root_path() -> Text:
        """获取当前的根目录"""
        return os.environ["ROOT_PATH"]

    def insert(self, *task):
        for ta in task:
            self.task_set[ta.name] = ta

    def read_config_from_json(self, json_path: Text):
        """
        从json文件中获取配置信息
        """
        with open(json_path, "r") as fp:
            data = load(fp=fp)
        self.read_from_mapping(data)

    def read_from_mapping(self, data: Dict):
        """从字典中获取配置信息"""
        for i, v in data.items():
            setattr(self, i, v)

    def detect_task(self) -> List[Task]:
        """
        探测root_path的task本地文件内容有无发生改变

        """
        tasks = []
        import os

        # todo: 探测数据
        for file in os.listdir(self.root_path()):
            pass
        return tasks

    def hot_load_task(self, task: Task):
        """热更新当前任务"""
        if task.name in self.task_set:
            if self.task_set[task.name].status == TaskStatus.PENDING:
                self.__wait_task_queue.append(task)
            else:
                self.task_set[task.name] = task

    def run(self):
        """主体运行函数 执行Task"""
        logger.info(f"Hive Started")

        self.init_from_config()
        c = None
        while True:
            current = datetime.now()
            if c is None:
                c = current.hour
            for task_name in list(self.task_set.keys()):
                task = self.task_set[task_name]
                if task.auth_time(time=current):
                    """当前时间正确且当前进程不活跃"""

                    if task.task_type() == TaskType.LOOP and not task.alive():
                        logger.info(f"start task: {task.name}")
                        task.run()
                    elif (
                        task.task_type() == TaskType.ONCE_AGAIN
                        and not task.task_run_status()
                    ):
                        """仅当一次任务时候 运行一次"""
                        logger.info(f"start task: {task.name}")
                        task.run()

                if not task.auth_time(time=current):
                    if task.task_type() == TaskType.LOOP and task.alive():
                        """当设置为持续工作模式时候 需要手动停止"""
                        logger.info(f"stop loop task: {task.name}")
                        task.kill()

                    elif (
                        task.task_type() == TaskType.ONCE_AGAIN
                        and task.task_run_status()
                    ):
                        task = self.task_set.pop(task.name)
                        task.reset_task()
                        self.__wait_task_queue.append(task)

            # if new day, re_callback the task
            if current.hour != c and c == 0 and current.date() in trade_dates:
                for task in self.__wait_task_queue:
                    self.task_set[task.name] = task
                self.__wait_task_queue.clear()

            c = datetime.now().hour


if __name__ == "__main__":
    hive = Hive()
    hive.run()
