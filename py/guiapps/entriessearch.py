import subprocess
from utils import windowcontrol
from guiapps import defaultapp
from gui import keycodes
from gui.components import entriestree


class EntriesSearch(defaultapp.DefaultApp):
    def __init__(self, *args, **kwrags):
        defaultapp.DefaultApp.__init__(self, *args, **kwrags)

    def handle_key_Ctrl_Equals(self):
        """Add selected tab as bookmark"""
        self._choose_parent_dir_for_adding_bookmark()

    def handle_key_Ctrl_Hyphen(self):
        """Remove selected bookmark from bookmarks"""
        self._remove_bookmark()

    def _choose_parent_dir_for_adding_bookmark(self):
        # Get the tab dict in which url and title are stored
        tab_id = self._switcher_window._entriestree.get_value_of_selected_row(entriestree.COL_NR_ENTRY_ID_INT2)
        window_id = self._switcher_window._entriestree.get_value_of_selected_row(entriestree.COL_NR_ENTRY_ID_INT)
        window_pid = self._switcher_window._windows[window_id].get_pid()

        # Find tab by ID
        matching_tabs = [tab for tab in self._switcher_window._entriestree._tabs[window_pid] if tab['id'] == tab_id]
        if not matching_tabs:
            raise ValueError("Did not find a matching tab", tab_id, self._entriestree._tabs[window_pid])
        elif len(matching_tabs) > 1:
            raise ValueError("More than one matching tabs", tab_id, self._entriestree._tabs[window_pid])
        tab = matching_tabs[0]

        # Call switcher to add this as bookmark
        self._switch_app("choose_parent_bookmarks_dir_app", tab['title'], tab['url'])

    def handle_entry_activation(self):
        window_id = self._switcher_window._entriestree.get_value_of_selected_row(entriestree.COL_NR_ENTRY_ID_INT)
        if window_id is None:
            return
        try:
            windowcontrol.focus_on_window(window_id)
            # Setting the window to not visible causes Alt+Tab to avoid switcher (which is good)
            self._switcher_window.set_visible(False)
        except subprocess.CalledProcessError:
            # Actual window list has changed since last reload
            self.async_list_windows()
        tab_id = self._switcher_window._entriestree.get_value_of_selected_row(entriestree.COL_NR_ENTRY_ID_INT2)
        is_tab = tab_id >= 0
        if is_tab:
            window = self._switcher_window._entriestree._windows[window_id]
            self._entries_model._tabcontrol.async_move_to_tab(tab_id, window.get_pid())

    def handle_entry_selection(self):
        record_type = self._switcher_window._entriestree.get_value_of_selected_row(entriestree.COL_NR_RECORD_TYPE)
        if record_type in (entriestree.RECORD_TYPE_BOOKMARK_ENTRY, entriestree.RECORD_TYPE_BOOKMARKS_DIR):
            self._switch_app("bookmarks_search")

    def _remove_bookmark(self):
        record_type = self._switcher_window._entriestree.get_value_of_selected_row(entriestree.COL_NR_RECORD_TYPE)
        if record_type == entriestree.RECORD_TYPE_BOOKMARK_ENTRY:
            bookmark_id = self._switcher_window._entriestree.get_value_of_selected_row(entriestree.COL_NR_ENTRY_ID_STR)
            self._entries_model._bookmark_store.remove(bookmark_id)
            self._switcher_window._status_label.set_text("Removing bookmark...")
