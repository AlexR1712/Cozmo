#
# Copyright (C) 2016 Kamran Mackey and contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import re

import requests
from lxml import etree
from requests.utils import quote
from telegram import ChatAction, ParseMode

# Block network access and resolve entities
# for security reasons.
parser = etree.XMLParser(resolve_entities=False, no_network=True)

api_prefix = "https://en.wikipedia.org/w/api.php"
search_url = api_prefix + "?action=opensearch&format=xml"
random_url = api_prefix + "?action=query&format=xml&list=random&rnlimit=1&rnnamespace=0"

paren_re = re.compile('\s*\(.*\)$')


def wiki(_, update, args):
    """
    Plugin used for retrieving articles from
    Wikipedia.
    """
    args = ' '.join(args)

    try:
        request = requests.get(search_url, params={'search': args.strip()})
        request.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        update.message.reply_text(parse_mode='Markdown',
                                  text="Could not get Wikipedia page: {}".format(e))
    x = etree.fromstring(request.text, parser=parser)

    ns = '{http://opensearch.org/searchsuggest2}'
    items = x.findall(ns + 'Section/' + ns + 'Item')

    if not items:
        if x.find('error') is not None:
            update.message.chat.send_action(action=ChatAction.TYPING)
            update.message.reply_text(parse_mode=ParseMode.MARKDOWN,
                                      text='Could not get Wikipedia article  due to an error.\n\n'
                                           '*Error*: `%(code)s: %(info)s`' % x.find('error').attrib)
        else:
            update.message.chat.send_action(action=ChatAction.TYPING)
            update.message.reply_text(parse_mode=ParseMode.MARKDOWN,
                                      text='No results found.')

    def extract(item):
        return [item.find(ns + i).text for i in
                ('Text', 'Description', 'Url')]

    title, description, url = extract(items[0])

    if 'may refer to' in description:
        title, description, url = extract(items[1])

    title = paren_re.sub('', title)

    if title.lower() not in description.lower():
        description = title + description

    # Remove excess spaces from the output.
    description = ' '.join(description.split())
    description = description

    update.message.chat.send_action(ChatAction.TYPING)
    update.message.reply_text(parse_mode=ParseMode.HTML,
                              disable_web_page_preview=True,
                              text='<b>Wikipedia information for {}</b>:\n\n'
                                   '<i>{}</i>\n\n'
                                   '<b>View article on Wikipedia</b>: {}'.format(args,
                                                                                 description,
                                                                                 quote(url,
                                                                                       ':/%')))
