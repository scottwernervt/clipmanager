from clipmanager.ui.historylist import HistoryListView


def test_history_list(qtbot, model):
    history_view = HistoryListView()
    history_view.setModel(model)
    history_view.show()
    qtbot.addWidget(history_view)

    assert history_view.model().rowCount() > 0
