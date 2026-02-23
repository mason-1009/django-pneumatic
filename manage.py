#!/usr/bin/env python
import importlib
import os
import sys


if __name__ == "__main__":
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "tests.settings"
    )

    settings = importlib.import_module(
        os.environ.get("DJANGO_SETTINGS_MODULE")
    )

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # from pyannotate_runtime import collect_types
    # collect_types.init_types_collection()
    # with collect_types.collect():
    #     execute_from_command_line(sys.argv)
    # collect_types.dump_stats('/tmp/types.json')

    execute_from_command_line(sys.argv)
