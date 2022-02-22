# -*- coding: utf-8 -*-
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#  Author: Mauro Soria

from lib.core.settings import NEW_LINE, INSECURE_CSV_CHARS
from lib.reports.base import FileBaseReport


class CSVReport(FileBaseReport):
    def generate_header(self):
        if self.header_written is False:
            self.header_written = True
            return "URL,Status,Size,Redirection" + NEW_LINE
        else:
            return ''

    # Preventing CSV injection. More info: https://www.exploit-db.com/exploits/49370
    def clear_csv_attr(self, text):
        if text.startswith(INSECURE_CSV_CHARS):
            text = "'" + text

        return text.replace('"', '""')

    def generate(self):
        result = self.generate_header()

        for entry in self.entries:
            for result in entry.results:
                if (entry.protocol, entry.host, entry.port, entry.base_path, result.path) not in self.written_entries:
                    path = result.path
                    status = result.status
                    content_length = result.response.length
                    redirect = result.response.redirect

                    result += "{.protocol}://{.host}:{.port}/{.base_path}{path},".format(entry, path=path)
                    result += f"{status},"
                    result += f"{content_length},"

                    if redirect:
                        result += f'"{self.clean_csv_attr(redirect)}"'

                    result += NEW_LINE
                    self.written_entries.append((entry.protocol, entry.host, entry.port, entry.base_path, result.path))

        return result
