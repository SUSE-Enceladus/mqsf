import pluggy

hookimpl = pluggy.HookimplMarker('mqsf')


@hookimpl
def run_task(job_config, log_callback):
    """Run the workload"""
    return
