import pluggy

from mqsf.status_levels import SUCCESS

hookimpl = pluggy.HookimplMarker('mqsf')


@hookimpl
def run_task(job_config, log_callback):
    """Run the workload"""
    return SUCCESS, job_config
