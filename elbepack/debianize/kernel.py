# ELBE - Debian Based Embedded Rootfilesystem Builder
# Copyright (c) 2016-2017 John Ogness <john.ogness@linutronix.de>
# Copyright (c) 2016-2017 Manuel Traut <manut@linutronix.de>
# Copyright (c) 2017 Torben Hohn <torben.hohn@linutronix.de>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os

from shutil import copyfile

from npyscreen import TitleText, TitleSelectOne

from elbepack.directories import mako_template_dir
from elbepack.debianize.base import DebianizeBase, template


class Kernel (DebianizeBase):

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-ancestors

    name = "kernel"
    files = ['Kbuild', 'Kconfig', 'MAINTAINERS', 'kernel/futex.c']

    def __init__(self):
        self.imgtypes = ["bzImage", "zImage", "uImage", "Image"]
        self.imgtypes_install = ["install", "zinstall", "uinstall", "install"]
        DebianizeBase.__init__(self)

        self.loadaddr = None
        self.defconfig = None
        self.imgtype = None
        self.cross = None
        self.k_version = None

    def gui(self):
        self.loadaddr = self.add_widget_intelligent(
            TitleText, name="Loadaddress:", value="0x800800")

        self.defconfig = self.add_widget_intelligent(
            TitleText, name="defconfig:", value="omap2plus_defconfig")

        self.imgtype = self.add_widget_intelligent(
            TitleSelectOne,
            name="Image Format:",
            values=self.imgtypes,
            value=[0],
            scroll_exit=True)

        self.cross = self.add_widget_intelligent(
            TitleText, name="CROSS_COMPILE", value="arm-linux-gnueabihf-")

        self.k_version = self.add_widget_intelligent(
            TitleText, name="Kernelversion", value="4.4")

    def debianize(self):
        if self.deb['p_arch'] == 'armhf':
            self.deb['k_arch'] = 'arm'
        elif self.deb['p_arch'] == 'armel':
            self.deb['k_arch'] = 'arm'
        elif self.deb['p_arch'] == 'amd64':
            self.deb['k_arch'] = 'x86_64'
        else:
            self.deb['k_arch'] = self.deb['p_arch']

        self.deb['loadaddr'] = self.loadaddr.get_value()
        self.deb['defconfig'] = self.defconfig.get_value()
        self.deb['imgtype'] = self.imgtypes[self.imgtype.get_value()[0]]
        self.deb['imgtype_install'] = self.imgtypes_install[
                self.imgtype.get_value()[0]]
        self.deb['cross_compile'] = self.cross.get_value()
        self.deb['k_version'] = self.k_version.get_value()

        self.tmpl_dir = os.path.join(mako_template_dir, 'debianize/kernel')
        pkg_name = self.deb['p_name'] + '-' + self.deb['k_version']

        for tmpl in [
            'control',
            'rules',
            'preinst',
            'postinst',
            'prerm',
                'postrm']:
            with open(os.path.join('debian/', tmpl), 'w') as f:
                mako = os.path.join(self.tmpl_dir, tmpl + '.mako')
                f.write(template(mako, self.deb))

        cmd = 'dch --package linux-' + pkg_name + \
            ' -v ' + self.deb['p_version'] + \
            ' --create -M -D ' + self.deb['release'] + \
            ' "generated by elbe debianize"'
        os.system(cmd)

        copyfile(os.path.join(self.tmpl_dir, 'linux-image.install'),
                 'debian/linux-image-' + pkg_name + '.install')
        copyfile(os.path.join(self.tmpl_dir, 'linux-headers.install'),
                 'debian/linux-headers-' + pkg_name + '.install')

        self.hint = "use 'dpkg-buildpackage -a%s' to build the package" % (
                self.deb['p_arch'])


DebianizeBase.register(Kernel)
