from crate.theme.rtd.conf.cloud_cli import *  # noqa

extensions.append("sphinxarg.ext")  # type:ignore # noqa:F405

html_static_path = ["_static"]
html_context = {"extra_css_files": ["_static/sphinxarg.css"]}
