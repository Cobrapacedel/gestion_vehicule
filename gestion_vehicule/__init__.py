import django.core.files.locks

# Disable file locking by overriding the lock/unlock functions
def dummy_lock(*args, **kwargs):
    pass

def dummy_unlock(*args, **kwargs):
    pass

django.core.files.locks.lock = dummy_lock
django.core.files.locks.unlock = dummy_unlock