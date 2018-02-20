from clipmanager.singleinstance import SingleInstance


def test_single_instance():
    app = SingleInstance()
    assert not app.is_running()
    app.destroy()


def test_duplicate_instance():
    app_a, app_b = SingleInstance(), SingleInstance()
    assert not app_a.is_running()
    assert app_b.is_running()
    app_a.destroy()
    app_b.destroy()
