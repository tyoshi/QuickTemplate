import sublime
import sublime_plugin
import os
import sys
import errno
import yaml
import jinja2

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from inflection import inflection

"""
TODO:
1. ドキュメント整備
2. 公開方法調査
"""


def plugin_loaded():
    # Create plugin template, data default location
    FileHelper.mkdir_p(os.path.join(sublime.packages_path(), 'User', 'QuickTemplate', 'template'))
    FileHelper.mkdir_p(os.path.join(sublime.packages_path(), 'User', 'QuickTemplate', 'data'))


class QuickTemplateCommand(sublime_plugin.TextCommand):
    """
    List and execute various commands
    """
    def run(self, edit):
        view = self.view
        command_titles = [
            'QuickTemplate: Apply template',
            'QuickTemplate: Create new template file',
            'QuickTemplate: Create new data file',
            'QuickTemplate: Open template file',
            'QuickTemplate: Open data file']
        commands = [
            'quick_template_apply_template',
            'quick_template_create_template',
            'quick_template_create_data',
            'quick_template_open_template',
            'quick_template_open_data']
        view.window().show_quick_panel(command_titles, lambda index: view.run_command(commands[index]) if index >= 0 else None)


class QuickTemplateApplyTemplateCommand(sublime_plugin.TextCommand):
    """
    A command that applies data to a template and generates text
    """
    def run(self, edit):
        QuickTemplateSourceLoader(self.view).show_selector(self.render)

    def render(self, selected_files):
        template = selected_files.template()
        data = selected_files.data()
        data['inflection'] = inflection
        content = template.render(data)
        print("content="+content)
        # runの終了後にeditを使うとエラーになるため、新たにコマンドを実行
        self.view.run_command('quick_template_render', {'content':content})


class QuickTemplateRenderCommand(sublime_plugin.TextCommand):
    """
    Command to export text to the screen
    Invoked by callback after synthesizing template and data
    """
    def run(self, edit, content=None):
        view = self.view
        view.insert(edit, view.sel()[0].begin(), content)
        self.view.window().status_message('Insert ' + str(len(content)) + 'chars')


class QuickTemplateCreateTemplateCommand(sublime_plugin.TextCommand):
    """
    Command to create a new template
    """
    def run(self, edit):
        window = self.view.window()
        template_path = QuickTemplateSettings(window).template_path()
        QuickTemplateNewFileCreator(window, template_path).enter_filename('Enter a path for new template file')


class QuickTemplateCreateDataCommand(sublime_plugin.TextCommand):
    """
    Command to create a new data
    """
    def run(self, edit):
        window = self.view.window()
        data_path = QuickTemplateSettings(window).data_path()
        QuickTemplateNewFileCreator(window, data_path).enter_filename('Enter a path for new data file')


class QuickTemplateOpenTemplateCommand(sublime_plugin.TextCommand):
    """
    Command to open template
    """
    def run(self, edit):
        window = self.view.window()
        path = QuickTemplateSettings(window).template_path()
        FileSelector(window).show_selector(path, lambda file_path: window.open_file(file_path))


class QuickTemplateOpenDataCommand(sublime_plugin.TextCommand):
    """
    Command to open data
    """
    def run(self, edit):
        window = self.view.window()
        path = QuickTemplateSettings(window).data_path()
        FileSelector(window).show_selector(path, lambda file_path: window.open_file(file_path))




class QuickTemplateSourceLoader:
    """
    A utility class that loads templates and data from a given directory
    """
    def __init__(self, view):
        self.view = view
        self.settings = QuickTemplateSettings(view.window())
        self.file_selector = FileSelector(self.view.window())

    def show_selector(self, on_all_files_selected):
        self._on_all_files_selected = on_all_files_selected
        self.view.window().status_message("choise template file")
        self.file_selector.show_selector(self.settings.template_path(), self._after_select_template_file)

    def template(self):
        return self._template

    def data(self):
        return self._data

    def _after_select_template_file(self, file):
        if file is not None:
            self._template = self._load_template(file)
            self.view.window().status_message("choise data file")
            self.file_selector.show_selector(self.settings.data_path(), self._after_select_data_file)

    def _after_select_data_file(self, file):
        if file is not None:
            self._data = self._load_data(file)
            self._on_all_files_selected(self)

    def _load_template(self, file):
        content = FileHelper.read_file(file)
        try:
            return jinja2.Template(content)
        except jinja2.exceptions.TemplateSyntaxError as err:
            sublime.message_dialog("Template Syntax Error\n{0}".format(err))
            raise err

    def _load_data(self, file):
        content = FileHelper.read_file(file)
        if file.endswith(".py"):
            scope = {}
            exec(content, scope)
            data = scope['data']
        else:
            data = yaml.load(content) #suppor yaml and json
        if not isinstance(data,dict):
            sublime.message_dialog("Data Error\n"+
                "data must be instance of Object(json) or Dict(python)\n"+
                "data="+data)
            raise RuntimeError("Data must be instance of Dict(python)")
        return data


class FileSelector:
    def __init__(self, window):
        self.window = window

    def show_selector(self, path, on_done, no_file_message='There is no file in {path}'):
        files = list(FileHelper.find_files(path))
        if not files:
            sublime.message_dialog(no_file_message.format(path=path))
        self.window.show_quick_panel(files, lambda index: on_done(files[index][1]) if index >= 0 else on_done(None))


class QuickTemplateNewFileCreator:
    """
    A utility class that creates a new file in the path entered by the user
    """
    def __init__(self, window, root_path):
        self.window = window
        self.root_path = root_path

    def enter_filename(self, message):
        self.window.show_input_panel(message, '', self._on_success, self._on_edit, None)

    def _on_success(self, path):
        file_path = os.path.join(self.root_path, path)
        FileHelper.create_empty_file(file_path)
        self.window.open_file(file_path)

    def _on_edit(self, path):
        file_path = os.path.join(self.root_path, path)
        self.window.status_message(file_path)


class QuickTemplateSettings:
    """
    Class providing setting value
    """
    settings = sublime.load_settings('QuickTemplate.sublime-settings')
    def __init__(self, window):
        variables = window.extract_variables()
        self.project_name = variables.get('project_base_name')

    def template_path(self):
        path = self.get('template_path')
        return self._make_path(path)

    def data_path(self):
        path = self.get('data_path')
        return self._make_path(path)

    def get(self, name):
        """
        Acquire setting value
        We will honor the project settings of QuickTemplate.sublime-settings preferentially
        """
        project_settings = QuickTemplateSettings.settings.get('project_settings')
        current_project_settings = None if project_settings is None else project_settings.get(name)
        value = None if current_project_settings is None else current_project_settings.get(name)
        return QuickTemplateSettings.settings.get(name) if value is None else value

    def _make_path(self, path):
        """
        Return absolute path
        In the case of a relative path, absolute pass is made based on the
        Packages/User/QuickTemplate directory of SublimeText
        """
        return path if os.path.isabs(path) else os.path.join(sublime.packages_path(), 'User', 'QuickTemplate', path)


class FileHelper:
    """
    Class providing file related utility methods
    """
    def find_files(path):
        """
        Return Generator targeting array of names and paths of all files under the specified path
        However, excluding directories
        """
        path_len = len(path) + (0 if path[-1] in (os.path.sep, '\\', '/') else 1)
        for root, dirs, files in os.walk(path):
            for file in files:
                full_path = os.path.join(root, file)
                sub_path = full_path[path_len:]
                yield [sub_path, full_path]

    def read_file(path):
        if(path is None):
            return None
        with open(path, 'r') as f:
            return f.read()

    def mkdir_p(path):
        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    def create_empty_file(path):
        FileHelper.mkdir_p(os.path.dirname(path))
        if not os.path.exists(path):
            open(path, 'w').close()

