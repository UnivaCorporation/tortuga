from ..installer import ComponentInstallerBase, KitInstallerBase


class KitActionBase:
    def __init__(self, kit_installer: KitInstallerBase):
        self.kit_installer = kit_installer

    def is_runnable(self, *args, **kwargs):
        """
        Tests to see if this action is runnable.

        :param args:
        :param kwargs:

        :return: True if it is runnable, false otherwise

        """
        return True

    def do_action(self, *args, **kwargs):
        """
        Does the action. Override this in your implementations.

        """
        pass

    def __call__(self, *args, **kwargs):
        """
        Runs this action.

        """
        if self.is_runnable(*args, **kwargs):
            return self.do_action(*args, **kwargs)



class ComponentActionBase:
    def __init__(self, kit_installer: KitInstallerBase,
                 component_installer: ComponentInstallerBase):
        self.kit_installer = kit_installer
        self.component_installer = component_installer

    def is_runnable(self, *args, **kwargs):
        """
        Tests to see if this action is runnable.

        :return: True if it is runnable, false otherwise

        """
        return True

    def do_action(self, *args, **kwargs):
        """
        Does the action. Override this in your implementations.

        """
        pass

    def __call__(self, *args, **kwargs):
        """
        Runs this action.

        """
        if self.is_runnable(*args, **kwargs):
            return self.do_action(*args, **kwargs)
