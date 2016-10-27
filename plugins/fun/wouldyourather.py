#
# Copyright (C) 2016 Kamran Mackey and contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].

import json

import requests


def wouldyourather(_, update):
    """
    Sends a message containing a question
    from the rrrather website.
    """
    wyr_url = "https://www.rrrather.com/botapi"

    wyr_request = requests.get(wyr_url).text
    wyr_json = json.loads(wyr_request)

    # Variables
    title = wyr_json["title"].capitalize().replace(" :", "")
    choice_a = wyr_json["choicea"]
    choice_b = wyr_json["choiceb"].replace("?", "")
    votes = '{0:,}'.format(wyr_json["votes"])
    tags = wyr_json["tags"].replace(",", ", ")
    link = wyr_json["link"].replace("http", "https")

    # Message text
    view_text = "*View question on rrrather*"
    try:
        update.message.reply_text(parse_mode='Markdown',
                                  disable_web_page_preview=True,
                                  text="{}:\n"
                                       "*Choice A*: {}\n"
                                       "*Choice B*: {}\n\n"
                                       "*Votes*: {}\n"
                                       "*Tags*: {}\n"
                                       "{}: {}".format(title,
                                                       choice_a,
                                                       choice_b,
                                                       votes,
                                                       tags,
                                                       view_text,
                                                       link))
    except AttributeError:
        update.message.reply_text(text="`Error trying to retrieve a question from "
                                       "rrather. Please try again.`")
