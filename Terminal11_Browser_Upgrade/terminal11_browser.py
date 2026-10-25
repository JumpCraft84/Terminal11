#!/usr/bin/env python3
"""Terminal 11 Browser — Qt WebEngine (Chromium-based)."""
import json
import sys
from pathlib import Path
from urllib.parse import quote_plus

try:
    from PySide6.QtCore import QUrl, Qt
    from PySide6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QToolBar,
                                   QLineEdit, QMessageBox, QMenu, QFileDialog)
    from PySide6.QtGui import QAction
    from PySide6.QtWebEngineWidgets import QWebEngineView
    from PySide6.QtWebEngineCore import QWebEngineProfile
except ImportError as exc:
    print('Terminal 11 Browser needs PySide6 and PySide6-Addons (Qt WebEngine).')
    print('Install with: python -m pip install PySide6')
    print('On Raspberry Pi OS, Qt WebEngine wheel availability may vary.')
    print(f'Details: {exc}')
    sys.exit(1)

DATA = Path.home() / '.terminal11' / 'browser'
DATA.mkdir(parents=True, exist_ok=True)
BOOKMARKS = DATA / 'bookmarks.json'
HOME = 'https://www.wikipedia.org'


def normalize(value):
    value = value.strip()
    if not value:
        return HOME
    if value.startswith(('https://', 'http://')):
        return value
    if ' ' in value or '.' not in value:
        return 'https://www.google.com/search?q=' + quote_plus(value)
    return 'https://' + value


class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Terminal 11 Browser')
        self.resize(1200, 800)
        self.bookmarks = self.read_bookmarks()
        self.setStyleSheet('QMainWindow {background:#152136;} QToolBar {background:#24324a; spacing:6px; padding:6px;} QLineEdit {padding:7px; background:#f8fafc; border-radius:5px;} QTabWidget::pane {border:0;}')
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_address)
        self.setCentralWidget(self.tabs)
        bar = QToolBar('Navigation')
        bar.setMovable(False)
        self.addToolBar(bar)
        self.add_action(bar, '←', lambda: self.current().back())
        self.add_action(bar, '→', lambda: self.current().forward())
        self.add_action(bar, '⟳', lambda: self.current().reload())
        self.add_action(bar, '⌂', lambda: self.current().setUrl(QUrl(HOME)))
        self.address = QLineEdit()
        self.address.setPlaceholderText('Search or enter a website')
        self.address.returnPressed.connect(self.go)
        bar.addWidget(self.address)
        self.add_action(bar, 'Go', self.go)
        self.add_action(bar, '+ Tab', lambda: self.new_tab(HOME))
        self.add_action(bar, '☆', self.bookmark_current)
        bookmark_menu = QMenu('Bookmarks', self)
        bookmark_menu.aboutToShow.connect(lambda: self.fill_bookmarks(bookmark_menu))
        bar.addAction(bookmark_menu.menuAction())
        self.statusBar().showMessage('Ready')
        profile = QWebEngineProfile.defaultProfile()
        profile.setDownloadPath(str(Path.home() / 'Downloads'))
        profile.downloadRequested.connect(self.download_requested)
        self.new_tab(sys.argv[1] if len(sys.argv) > 1 else HOME)

    def add_action(self, toolbar, label, callback):
        action = QAction(label, self)
        action.triggered.connect(callback)
        toolbar.addAction(action)

    def current(self):
        return self.tabs.currentWidget()

    def new_tab(self, url=HOME):
        view = QWebEngineView()
        index = self.tabs.addTab(view, 'New Tab')
        self.tabs.setCurrentIndex(index)
        view.titleChanged.connect(lambda title, v=view: self.set_tab_title(v, title))
        view.urlChanged.connect(lambda _url, v=view: self.update_address() if self.current() is v else None)
        view.loadProgress.connect(lambda percent: self.statusBar().showMessage(f'Loading {percent}%'))
        view.loadFinished.connect(lambda ok: self.statusBar().showMessage('Ready' if ok else 'Page could not be loaded'))
        # Open target=_blank and window.open links in new browser tabs.
        view.createWindow = lambda _type: self.create_popup_tab()
        view.setUrl(QUrl(normalize(url)))
        return view

    def create_popup_tab(self):
        return self.new_tab('about:blank')

    def set_tab_title(self, view, title):
        idx = self.tabs.indexOf(view)
        if idx >= 0:
            self.tabs.setTabText(idx, (title or 'New Tab')[:28])
            if self.current() is view:
                self.setWindowTitle(f'{title or "New Tab"} — Terminal 11 Browser')

    def update_address(self, *_):
        view = self.current()
        if view:
            self.address.setText(view.url().toString())

    def go(self):
        self.current().setUrl(QUrl(normalize(self.address.text())))

    def close_tab(self, index):
        if self.tabs.count() == 1:
            self.close()
            return
        view = self.tabs.widget(index)
        self.tabs.removeTab(index)
        view.deleteLater()

    def read_bookmarks(self):
        try:
            data = json.loads(BOOKMARKS.read_text(encoding='utf-8'))
            return data if isinstance(data, list) else []
        except (OSError, ValueError):
            return []

    def bookmark_current(self):
        url = self.current().url().toString()
        if url not in self.bookmarks:
            self.bookmarks.append(url)
            BOOKMARKS.write_text(json.dumps(self.bookmarks, indent=2), encoding='utf-8')
            self.statusBar().showMessage('Bookmark saved', 3000)

    def fill_bookmarks(self, menu):
        menu.clear()
        if not self.bookmarks:
            item = menu.addAction('No bookmarks yet')
            item.setEnabled(False)
        for url in self.bookmarks:
            action = menu.addAction(url[:65])
            action.triggered.connect(lambda checked=False, u=url: self.current().setUrl(QUrl(u)))

    def download_requested(self, download):
        suggested = download.downloadFileName()
        target, _ = QFileDialog.getSaveFileName(self, 'Save download', str(Path.home() / 'Downloads' / suggested))
        if target:
            path = Path(target)
            download.setDownloadDirectory(str(path.parent))
            download.setDownloadFileName(path.name)
            download.accept()
            self.statusBar().showMessage('Downloading ' + path.name, 5000)
        else:
            download.cancel()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName('Terminal 11 Browser')
    browser = Browser()
    browser.show()
    sys.exit(app.exec())
