"""
Provide easy and fast boot command
"""
from hive.main import Hive
import click
from hive.src.task import DataUpdateTask, CleanDataTask

bool_map = {"false": False, "true": True}


def fix_bool(name):
    if name not in ["false", "true"]:
        raise TypeError(f"error type of {name.__name__}")
    else:
        return bool_map[name]


@click.command()
@click.option("--name", default="hive", prompt="hive")
@click.option("--path", help="the dirname of file_save_path", default="./")
@click.option("--ff", help="format of file", default="csv")
@click.option("--cf", help="config of file", default="config.json")
@click.option("--rd", help="uri of redis", default="127.0.0.1:6379")
@click.option("--trade_dispatch", default="false", help="open trade dispatcher or not")
@click.option("--tick_save", default="true", help="save tick data or not")
@click.option("--tick_dispatch", default="false", help="dispatch tick data or not")
def run_command(name, path, ff, cf, rd, trade_dispatch, tick_save, tick_dispatch):
    if ff not in ["csv", "parquet", "h5"]:
        raise TypeError("错误的文件导出格式 请检查你的ff参数")
    trade_dispatch = fix_bool(trade_dispatch)
    tick_save = fix_bool(tick_save)
    tick_dispatch = fix_bool(tick_dispatch)
    config_file = {"name": name,
                   "path": path,
                   "ff": ff,
                   "cf": cf,
                   "redis": rd,
                   "trade_dispatch": trade_dispatch,
                   "tick_save": tick_save,
                   "tick_dispatch": tick_dispatch
                   }
    insert = DataUpdateTask()
    clean = CleanDataTask()
    hive = Hive()
    hive.config.from_mapping(config_file)
    hive.insert(insert, clean)
    hive.run()
