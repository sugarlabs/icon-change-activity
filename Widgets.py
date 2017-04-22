#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Widgets.py
#
#  Copyright 2013 Ignacio Rodríguez <ignacio@sugarlabs.org>
#   SugarLabs - CeibalJAM! - Python Joven 2013
#
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
#

import os
import math
import mimetypes
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GConf
from gi.repository import GObject

from sugar3.graphics.icon import Icon
from sugar3.graphics.xocolor import XoColor
from sugar3.graphics import style

SUGAR_ICONS = ['activity-web', 'activity-pippy', 'activity-turtleart',
               'activity-read', 'activity-write']


def get_current_icon():
    client = GConf.Client.get_default()
    path = '/desktop/sugar/user/icon'
    value = client.get_string(path)
    if value:
        return value
    else:
        return 'computer-xo'


def get_icons(path):
    if not os.path.exists(path):
        os.mkdir(path)

    icon_theme = Gtk.IconTheme.get_default()
    if not path in icon_theme.get_search_path():
        icon_theme.append_search_path(path)

    list_icons = os.listdir(path)
    list_icons.sort()

    icons = ['computer-xo']
    for icon in list_icons:
        icon_path = os.path.join(path, icon)
        if not icon_path or os.path.isdir(icon_path) or \
                not os.path.exists(icon_path):
            continue
        computer_xo_path = os.path.join(path, "sugar", "scalable",
                                                    "device", "computer-xo.svg")
        same_file = False
        if os.path.exists(computer_xo_path):
            computer_xo = open(computer_xo_path, "r")
            xoicon = computer_xo.read()
            computer_xo.close()
            icon_f = open(icon_path, "r")
            xoicon_two = icon_f.read()
            icon_f.close()
            if xoicon == xoicon_two:
                same_file = True

        mimetype = mimetypes.guess_type(icon_path)[0]
        if 'svg' in mimetype:
            icon_name = icon[:-4]
            if not icon_name in icons \
            and icon_name != "computer-xo-default" \
            and not same_file:
                icons.append(icon_name)
    return icons


class XoHome(Gtk.Fixed):
    '''
    Simulate XO Home with custom icon.
    '''
    def __init__(self, icon, activity_path):
        super(XoHome, self).__init__()

        radius = min(Gdk.Screen.width(), Gdk.Screen.height())
        radius /= 4
        angle = 0
        for svg in SUGAR_ICONS:
            image = Icon(icon_name=svg, xo_color=xocolor,
                pixel_size=style.MEDIUM_ICON_SIZE)
            x = math.sin(angle) * radius
            y = math.cos(angle) * radius
            x += (Gdk.Screen.width() / 2) - style.LARGE_ICON_SIZE / 2
            y += (Gdk.Screen.height() / 2) - style.LARGE_ICON_SIZE
            self.put(image, int(x), int(y))
            angle += math.pi * 2 / len(SUGAR_ICONS)

        self.last_icon = icon
        self.update(None, icon)

        self.show_all()

    def update(self, widget, icon):
        self.remove(self.last_icon)
        self.last_icon = icon

        x = x = int(Gdk.Screen.width() - style.XLARGE_ICON_SIZE) / 2
        y = (Gdk.Screen.height() / 2) - style.XLARGE_ICON_SIZE
        self.put(icon, x, y)
        self.show_all()


class XoIcons(Gtk.Box):

    __gsignals__ = {
        'icon_changed': (GObject.SIGNAL_RUN_FIRST,
                         GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,))}

    def __init__(self, default):
        super(XoIcons, self).__init__(orientation=Gtk.Orientation.HORIZONTAL)

        path = os.path.join(os.path.expanduser('~'), '.icons')
        self.is_default = default
        self.list_icons = get_icons(path)
        self.icons = {}
        self.fill_list(self.list_icons)
        self.show_all()

    def fill_list(self, icons):

        client = GConf.Client.get_default()
        path = '/desktop/sugar/user/color'
        color = client.get_string(path)
        global xocolor
        xocolor = XoColor(color)
        current = get_current_icon()
        if not self.is_default:
                    icons.append("computer-xo-default")

        for icon_name in icons:
            icon = Icon(icon_name=icon_name, xo_color=xocolor,
                        pixel_size=style.MEDIUM_ICON_SIZE)

            icon_box = Gtk.EventBox()
            icon_box.add(icon)
            icon_box.connect('button-press-event', self.update)
            size = style.MEDIUM_ICON_SIZE + 20
            icon_box.set_size_request(size, size)

            icon_fixed = Icon(icon_name=icon_name, xo_color=xocolor,
                              pixel_size=style.XLARGE_ICON_SIZE)
            icon_fixed.set_tooltip_text(icon_name)
            icon_fixed.set_property('has-tooltip', False)

            icon_box.set_tooltip_text(icon_name)
            icon_box.set_property('has-tooltip', False)

            self.pack_start(icon_box, False, False, 0)
            self.pack_start(Gtk.VSeparator(), False, False, 3)

            if icon_name == current:
                self.icon = icon_fixed
                self.icon_real = icon_box
                icon_box.set_sensitive(False)
            self.icons[icon_box] = icon_fixed

    def get_icon(self):
        return self.icon

    def update(self, widget, event):
        self.emit('icon_changed', self.icons[widget])
        self.icon_real.set_sensitive(True)

        self.icon = self.icons[widget]

        self.icon_real = widget
        self.icon_real.set_sensitive(False)


class XoIcon(Gtk.Box):

    def __init__(self, activity_path, default):
        super(XoIcon, self).__init__(orientation=Gtk.Orientation.VERTICAL)

        self.icons = XoIcons(default)
        self.home = XoHome(self.icons.get_icon(), activity_path)

        self.icons.connect('icon_changed', self.home.update)

        self.home_box = Gtk.EventBox()
        self.home_box.modify_bg(Gtk.StateType.NORMAL,
                                Gdk.color_parse('white'))
        self.home_box.add(self.home)

        self.icons_box = Gtk.EventBox()
        self.icons_box.modify_bg(Gtk.StateType.NORMAL,
                                 Gdk.color_parse('white'))
        self.icons_box.add(self.icons)

        self.icons_scroll = Gtk.ScrolledWindow()
        self.icons_scroll.set_policy(Gtk.PolicyType.AUTOMATIC,
                                     Gtk.PolicyType.AUTOMATIC)
        self.icons_scroll.add_with_viewport(self.icons_box)

        self.icons_scroll.set_size_request(-1, style.MEDIUM_ICON_SIZE + 30)

        self.pack_start(self.home_box, True, True, 0)
        self.pack_start(Gtk.HSeparator(), False, False, 0)
        self.pack_start(self.icons_scroll, False, False, 0)

        self.show_all()

    def get_icon(self):
        return self.icons.get_icon().get_tooltip_text()
