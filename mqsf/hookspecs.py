import pluggy


hookspec = pluggy.HookspecMarker('mqsf')


@hookspec
def run_task(job_config, log_callback):
    """Run the workload"""
