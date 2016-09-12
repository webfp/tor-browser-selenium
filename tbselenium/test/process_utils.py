import psutil


def get_fx_proc_from_geckodriver_service(driver):
    """Get TB process by iterating over geckodriver's child processes."""
    gecko_drv_proc = psutil.Process(driver.service.process.pid)
    for child in gecko_drv_proc.children():
        if child.name() == "firefox":
            return child
