import sys
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QTabWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QCheckBox,
    QSpinBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from pyclashbot.interface.pyqt_themes import THEMES

print("Available themes:")
for title, theme in THEMES.items():
    print(f"{title}")

theme = THEMES["midnight_blue_theme"]

# Constants defining initial checkbox states for each job
JOB_DEFAULT_STATES = {
    "Request": True,
    "Donate": False,
    "Buy shop offers": True,
    "Upgrade your deck": True,
    "Buy from the season shop": False,
    "Open chests": True,
    "Collect battlepass": False,
    "Colled card mastery": True,
    "Collect daily rewards": False,
    "Collect level up chest": True,
    "Collect Bannerbox": False,
    "Collect Trophy Rewards": True,
    "Fight trophy road battle": False,
    "Fight goblin queen battle": True,
    "Fight path of legends battle": False,
    "Fight 2v2 battle": True,
    "Fight war battle": False,
    "Randomize deck": True,
    "Random plays": False,
    "Disable win/loss tracking": True,
    "Skip fighting when full chests": False,
}

tabName2jobList = {
    "Card Jobs": [
        "Request",
        "Donate",
        "Buy shop offers",
        "Upgrade your deck",
        "Buy from the season shop",
    ],
    "Rewards Jobs": [
        "Open chests",
        "Collect battlepass",
        "Colled card mastery",
        "Collect daily rewards",
        "Collect level up chest",
        "Collect Bannerbox",
        "Collect Trophy Rewards",
    ],
    "Fight Jobs": [
        "Fight trophy road battle",
        "Fight goblin queen battle",
        "Fight path of legends battle",
        "Fight 2v2 battle",
        "Fight war battle",
        "Randomize deck",
        "Random plays",
        "Disable win/loss tracking",
        "Skip fighting when full chests",
    ],
}

botStatsDict = {
    "Bot Failures": 0,
    "Runtime": "00:00.00",
}
battleStatsDict = {
    "Wins": 0,
    "Losses": 0,
    "Win rate": 0,
    "Cards played": 0,
    "Path of legends fights": 0,
    "Trophy fights": 0,
    "Queens 1v1 fights": 0,
    "2v2 fights": 0,
    "War fights": 0,
    "Deck randomization": 0,
}
collectionStatsDict = {
    "Requests": 0,
    "Shop purchases": 0,
    "Donates": 0,
    "Chests unlocked": 0,
    "Daily rewards": 0,
    "Card mastery collects": 0,
    "Bannerbox collects": 0,
    "Cards upgraded": 0,
    "Battlepass collects": 0,
    "Level up collects": 0,
    "War chest collects": 0,
    "Season shop purchases": 0,
}


class FrontEnd(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Py-ClashBot")
        self.resize(800, 600)  # Set the window size to 800x600

        layout = QHBoxLayout()  # Use QHBoxLayout for horizontal alignment

        # Add title text
        title_label = QLabel("Py-ClashBot")
        title_font = QFont("Arial", 24, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Add a stretch to push the buttons to the right
        layout.addStretch()

        # Add Discord button
        discord_button = QPushButton("Discord")
        discord_color = QColor(114, 137, 218)  # Discord's blue-purple hue
        discord_button.setStyleSheet(
            f"background-color: {discord_color.lighter(150).name()}; color: white; font-size: 16px; padding: 10px;"
        )
        discord_button.setFixedSize(100, 50)
        discord_button.clicked.connect(lambda: self.print_button_pressed("Discord"))

        # Add START button
        start_button = QPushButton("START")
        start_button.setStyleSheet(
            "background-color: #9ACD32; color: white; font-size: 16px; padding: 10px;"
        )  # Pastel green
        start_button.setFixedSize(100, 50)
        start_button.clicked.connect(lambda: self.print_button_pressed("START"))

        # Add Bug Report button
        bug_report_button = QPushButton("Bug Report")
        bug_report_button.setStyleSheet(
            "background-color: #FF6347; color: white; font-size: 16px; padding: 10px;"
        )  # Pastel red
        bug_report_button.setFixedSize(100, 50)
        bug_report_button.clicked.connect(
            lambda: self.print_button_pressed("Bug Report")
        )

        # Add Upload Log button
        upload_log_button = QPushButton("Upload Log")
        upload_log_button.setStyleSheet(
            "background-color: #87CEFA; color: white; font-size: 16px; padding: 10px;"
        )  # Pastel blue
        upload_log_button.setFixedSize(100, 50)
        upload_log_button.clicked.connect(
            lambda: self.print_button_pressed("Upload Log")
        )

        # Add all the buttons to the layout
        layout.addWidget(start_button)
        layout.addWidget(discord_button)
        layout.addWidget(bug_report_button)
        layout.addWidget(upload_log_button)

        # Create a vertical layout for the tabs
        main_layout = QVBoxLayout()

        tab_widget = QTabWidget()

        # Create first tab (General Settings)
        tab1 = QWidget()
        general_settings_tab_layout = QVBoxLayout()

        # Add placeholder text
        placeholder_text = QLabel(
            "This is placeholder text. This is placeholder text. This is placeholder text. "
            "This is placeholder text. This is placeholder text. This is placeholder text."
        )
        placeholder_text.setWordWrap(True)
        general_settings_tab_layout.addWidget(placeholder_text)

        # Add 'enable docking' checkbox
        enable_docking_checkbox = QCheckBox("Enable docking")
        general_settings_tab_layout.addWidget(enable_docking_checkbox)

        # add 'enable analytics' checkbox
        enable_analytics_checkbox = QCheckBox("Enable Analytics")
        general_settings_tab_layout.addWidget(enable_analytics_checkbox)

        tab1.setLayout(general_settings_tab_layout)

        # Create second tab (Bot Settings)
        bot_settings_tab = QWidget()
        bot_settings_layout = QVBoxLayout()
        bot_settings_page_text = QLabel("Stuff to show on bot settings page")
        bot_settings_layout.addWidget(bot_settings_page_text)

        self.nested_tab_widget = QTabWidget()
        self.nested_tab_bar = self.nested_tab_widget.tabBar()

        # Create nested tabs
        self.create_nested_tab("Bot #1 Settings")
        self.create_nested_tab("Bot #2 Settings")
        self.create_nested_tab("Bot #3 Settings")

        # Add "plus" button to add new tabs
        self.plus_button = QPushButton("+")
        self.plus_button.setFixedSize(30, 30)
        self.plus_button.clicked.connect(self.add_new_tab)
        self.nested_tab_bar.setMovable(True)
        self.nested_tab_bar.setTabsClosable(False)
        self.nested_tab_bar.setExpanding(True)

        self.nested_tab_widget.setCornerWidget(
            self.plus_button, Qt.Corner.TopRightCorner
        )

        bot_settings_layout.addWidget(self.nested_tab_widget)
        bot_settings_tab.setLayout(bot_settings_layout)

        # Create third tab (Runtime Statistics)
        tab3 = QWidget()
        tab3_layout = QVBoxLayout()

        # Create tables for statistics
        bot_stats_table = self.create_stats_table(botStatsDict, "Bot statistics")
        battle_stats_table = self.create_stats_table(
            battleStatsDict, "Battle statistics"
        )
        collection_stats_table = self.create_stats_table(
            collectionStatsDict, "Collection statistics"
        )

        # Add tables to horizontal layout
        table_layout = QHBoxLayout()  # Change to QHBoxLayout to align tables in a row

        # Add titles and tables to the layout
        bot_stats_layout = QVBoxLayout()
        bot_stats_layout.addWidget(QLabel("Bot statistics"))
        bot_stats_layout.addWidget(bot_stats_table)

        battle_stats_layout = QVBoxLayout()
        battle_stats_layout.addWidget(QLabel("Battle statistics"))
        battle_stats_layout.addWidget(battle_stats_table)

        collection_stats_layout = QVBoxLayout()
        collection_stats_layout.addWidget(QLabel("Collection statistics"))
        collection_stats_layout.addWidget(collection_stats_table)

        # Add the vertical layouts to the horizontal layout
        table_layout.addLayout(bot_stats_layout)
        table_layout.addLayout(battle_stats_layout)
        table_layout.addLayout(collection_stats_layout)

        # Add the horizontal layout to the vertical tab layout
        tab3_layout.addLayout(table_layout)

        tab3.setLayout(tab3_layout)

        # Add tabs to the QTabWidget
        tab_widget.addTab(tab1, "General Settings")
        tab_widget.addTab(bot_settings_tab, "Bot Settings")
        tab_widget.addTab(tab3, "Runtime Statistics")

        main_layout.addLayout(layout)
        main_layout.addWidget(tab_widget)

        self.setLayout(main_layout)

        # Apply a dark theme
        self.setStyleSheet(theme)

    def create_nested_tab(self, title):
        nested_tab = QWidget()
        nested_tab_layout = QVBoxLayout()

        bot_enable_text = str(title).replace(" Settings", "")
        enable_bot_checkbox = QCheckBox(f"Enable {bot_enable_text}")
        enable_bot_checkbox.setChecked(True)
        nested_tab_layout.addWidget(enable_bot_checkbox)

        inner_tab_widget = QTabWidget()

        # Create tabs using tabName2jobList
        for tab_name, job_list in tabName2jobList.items():
            tab = QWidget()
            tab_layout = QVBoxLayout()
            tab_layout.addWidget(QLabel(f"{tab_name} Job Settings"))

            # Add 'Enable Bot #{}' checkbox
            tab_index = (
                self.nested_tab_widget.count() + 1
            )  # Calculate tab index dynamically
            enable_bot_checkbox = QCheckBox(f"Enable Bot #{tab_index}")
            tab_layout.addWidget(enable_bot_checkbox)

            # Add job toggle inputs based on job_list
            for job_name in job_list:
                row_layout = QHBoxLayout()
                checkbox = QCheckBox("Enable")
                checkbox.setChecked(JOB_DEFAULT_STATES.get(job_name, False))
                checkbox.setFont(QFont("Arial", 10))  # Increase font size
                input_label = QLabel(f"{job_name} every")
                input_label.setFont(QFont("Arial", 10))  # Increase font size
                spin_box = QSpinBox()
                spin_box.setRange(1, 100)  # Example range
                battles_label = QLabel("battles")
                battles_label.setFont(QFont("Arial", 10))  # Increase font size

                # Align widgets in the row
                row_layout.addWidget(checkbox)
                row_layout.addWidget(input_label)
                row_layout.addWidget(spin_box)
                row_layout.addWidget(battles_label)
                row_layout.addStretch(1)  # Add stretch to align from the left

                tab_layout.addLayout(row_layout)

            tab.setLayout(tab_layout)
            inner_tab_widget.addTab(tab, tab_name)

        nested_tab_layout.addWidget(inner_tab_widget)
        nested_tab.setLayout(nested_tab_layout)
        self.nested_tab_widget.addTab(nested_tab, title)

    def create_stats_table(self, stats_dict, title):
        table = QTableWidget()
        table.setRowCount(len(stats_dict))
        table.setColumnCount(2)

        row = 0
        for key, value in stats_dict.items():
            metric_item = QTableWidgetItem(key)
            value_item = QTableWidgetItem(str(value))

            # Set item flags to make it read-only
            metric_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            value_item.setFlags(Qt.ItemFlag.ItemIsEnabled)

            table.setItem(row, 0, metric_item)
            table.setItem(row, 1, value_item)
            row += 1

        # Hide headers
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)

        # Set column widths based on content
        table.resizeColumnToContents(0)

        # Set horizontal stretch for the second column to fill available space
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        table.setWindowTitle(title)
        return table

    def add_new_tab(self):
        new_tab_index = self.nested_tab_widget.count() + 1
        self.create_nested_tab(f"Bot #{new_tab_index} Settings")

    def print_button_pressed(self, button_name):
        print(f"Button pressed: {button_name}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = FrontEnd()
    ex.show()
    sys.exit(app.exec())