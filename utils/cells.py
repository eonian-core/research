class StopExecution(Exception):
    def _render_traceback_(self):
        pass


def stop(): raise StopExecution
