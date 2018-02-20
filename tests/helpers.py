def menu_action(menu, name):
    for action in menu.actions():
        if action.text() == name:
            return action
