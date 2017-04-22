#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  activity.py
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
import subprocess

from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import StopButton
from sugar3.graphics.toolbutton import ToolButton
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.graphics.alert import NotifyAlert

from gi.repository import Gtk

from Widgets import XoIcon

from gettext import gettext as _

SUGAR_ICON_PATH = 'sugar/scalable/device'
DEFAULT_ICON = 'computer-xo'
CONTROL_PANEL_ICON = 'module-about_me'


class IconChangeActivity(activity.Activity):

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
        self.max_participants = 1

        self.toolbar_box = ToolbarBox()
        self.toolbar = self.toolbar_box.toolbar

        activity_button = ActivityToolbarButton(self)
        self.toolbar.insert(activity_button, 0)
        activity_button.show()

        self.confirm_button = ToolButton('dialog-ok')
        self.confirm_button.set_tooltip(_('Apply changes'))
        self.confirm_button.connect('clicked', self.apply_changes)
        self.toolbar.insert(self.confirm_button, -1)

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        self.toolbar.insert(separator, -1)

        stop_button = StopButton(self)
        self.toolbar.insert(stop_button, -1)

        # We need: ~/.icons/sugar/scalabale/device/
        #          ~/.icons/computer-xo.svg
        #          ~/.icons/sugar/index.theme
        root_path = os.path.join(os.path.expanduser('~'), '.icons')
        if not os.path.exists(os.path.join(root_path)):
            subprocess.check_output(['mkdir', os.path.join(root_path)])
        if not os.path.exists(os.path.join(root_path, 'sugar')):
            subprocess.check_output(['mkdir',
                                     os.path.join(root_path, 'sugar')])
        if not os.path.exists(os.path.join(root_path, 'sugar', 'scalable')):
            subprocess.check_output(['mkdir',
                                     os.path.join(root_path, 'sugar',
                                                  'scalable')])
        if not os.path.exists(os.path.join(root_path, 'sugar', 'scalable',
                                           'device')):
            subprocess.check_output(['mkdir', os.path.join(root_path, 'sugar',
                                                           'scalable',
                                                           'device')])
        if not os.path.exists(os.path.join(root_path, DEFAULT_ICON + '.svg')):
            from_path = os.path.join(activity.get_bundle_path(),
                                     'icons', DEFAULT_ICON + '.svg')
            subprocess.check_output(['cp', from_path, root_path])
        if not os.path.exists(os.path.join(root_path, 'sugar', 'index.theme')):
            subprocess.check_output(['cp',
                                     os.path.join(activity.get_bundle_path(),
                                                  'index.theme'),
                                     os.path.join(root_path, 'sugar')])

        # Copy example icons to ~/.icons
        list_icons = os.listdir(os.path.join(activity.get_bundle_path(),
                                                    "icons_example"))
        list_icons.sort()

        for icon in list_icons:
            icon_path = os.path.join(activity.get_bundle_path(),
                                                    "icons_example", icon)
            icon_path_icon = os.path.join(root_path, icon)
            if not os.path.exists(icon_path_icon):
                command = ['cp', icon_path, icon_path_icon]
                subprocess.check_output(command)

        # Computer-xo -> original
        icon_path = os.path.join(activity.get_bundle_path(), "icons",
            "computer-xo.svg")
        icon_path_icon = os.path.join(root_path, "computer-xo-default.svg")

        command = ['cp', icon_path, icon_path_icon]
        subprocess.check_output(command)

        # Check if icon is = to computer-xo of activity/icons/computer-xo.svg

        current_xoicon = os.path.join(root_path, 'sugar', 'scalable',
                'device', DEFAULT_ICON + '.svg')
        computer_xo = os.path.join(activity.get_bundle_path(), 'icons',
                DEFAULT_ICON + '.svg')
        is_default = False
        if os.path.exists(current_xoicon):
            xoicon = open(current_xoicon, 'r')
            icon = xoicon.read()
            xoicon.close()

            xoicon = open(computer_xo, 'r')
            icon_two = xoicon.read()
            xoicon.close()

            if icon != icon_two:
                pass
            else:
                is_default = True

        self.canvas = XoIcon(activity.get_bundle_path(), is_default)

        self.set_toolbar_box(self.toolbar_box)
        self.set_canvas(self.canvas)
        self.show_all()

    def apply_changes(self, widget):
        self.write(self.canvas.get_icon())
        self.notify_alert()

    def write(self, icon):
        root_path = os.path.join(os.path.expanduser('~'), '.icons')
        to_path = os.path.join(root_path, SUGAR_ICON_PATH,
                               DEFAULT_ICON + '.svg')
        to_path_two = os.path.join(root_path, SUGAR_ICON_PATH,
                                        CONTROL_PANEL_ICON + ".svg")
        if icon == DEFAULT_ICON:
            command = ['rm', to_path]
            command_two = ['rm', to_path_two]
        else:
            from_path = os.path.join(root_path, icon + '.svg')
            command = ['cp', from_path, to_path]
            command_two = ['cp', from_path, to_path_two]
        subprocess.check_output(command)
        subprocess.check_output(command_two)
        return True

    def notify_alert(self):
        alert = NotifyAlert()
        alert.props.title = _('Saving icon...')
        msg = _('A restart is required before your new icon will appear.')
        alert.props.msg = msg

        def remove_alert(alert, response_id):
            self.remove_alert(alert)

        alert.connect('response', remove_alert)
        self.add_alert(alert)
