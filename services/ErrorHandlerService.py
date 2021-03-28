from datetime import datetime
from configManager import ConfigManager


class ErrorHandlerService:
    # check if bfs_nr contains only numbers and does not exceed the length of 4
    @staticmethod
    def check_bfs_nr_format(bfs_nr):
        return bfs_nr.isdecimal() and len(bfs_nr) <= 4

    # check if date is in the correct format (yyyy-MM-dd)
    @staticmethod
    def check_date_format(date):
        if not date:
            return True

        try:
            datetime.strptime(date, ConfigManager.get_instance().get_required_date_format())
            return True
        except ValueError:
            return False

    # TBD
    @staticmethod
    def check_date_sematic(date_from, date_to):
        if not date_from or not date_to:
            return True

        return date_from <= date_to
