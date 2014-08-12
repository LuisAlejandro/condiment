#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Luis Alejandro Martínez Faneyth
#
# This file is part of Condiment.
#
# Condiment is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Condiment is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""

condiment.common.setup.install
===========================


"""

import os
import cssmin
import slimit

from distutils.cmd import Command
from distutils.command.build import build as base_build
from docutils.core import Publisher
from docutils.writers import manpage
from sphinx.setup_command import BuildDoc as base_build_sphinx
from babel.messages.frontend import compile_catalog as base_compile_catalog

from condiment.config.base import BASEDIR, DOCDIR
from condiment.common.utils import get_path, find_files, list_files, list_items
from condiment.common.logger import get_logger

log = get_logger()


class build_css(Command):
    description = 'Compress CSS files.'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        log.debug('[%s.%s] Compressing CSS.' % (__name__,
                                                self.__class__.__name__))

        CSSFULL_DIR = get_path([BASEDIR, 'condiment', 'data', 'static', 'css',
                                'full'])
        CSSMIN_DIR = get_path([BASEDIR, 'condiment', 'data', 'static', 'css',
                               'min'])

        try:
            os.makedirs(CSSMIN_DIR)
        except Exception as e:
            print e

        for CSS_FILE in find_files(path=CSSFULL_DIR, pattern='*.css'):

            CSSMIN_FILE = get_path([CSSMIN_DIR, os.path.basename(CSS_FILE)])

            try:

                with open(CSSMIN_FILE, 'w') as _file:
                    _file.write(cssmin.cssmin(open(CSS_FILE).read()))
                    _file.close()

            except Exception as e:
                print e

            log.debug('[%s.%s] %s > %s.' % (__name__, self.__class__.__name__,
                                            CSS_FILE, CSSMIN_FILE))


class build_js(Command):
    description = 'Compress JS files.'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        log.debug(
            "[%s.%s] Compressing JS." %
            (__name__, self.__class__.__name__))

        JSFULL_DIR = get_path(
            [BASEDIR,
             'condiment',
             'data',
             'static',
             'js',
             'full'])
        JSMIN_DIR = get_path(
            [BASEDIR,
             'condiment',
             'data',
             'static',
             'js',
             'min'])

        try:
            os.makedirs(JSMIN_DIR)
        except Exception as e:
            print e

        for JS_FILE in find_files(path=JSFULL_DIR, pattern='*.js'):

            JSMIN_FILE = get_path([JSMIN_DIR, os.path.basename(JS_FILE)])

            try:

                with open(JSMIN_FILE, 'w') as _file:
                    _file.write(slimit.minify(open(JS_FILE).read()))
                    _file.close()

            except Exception as e:
                print e

            log.debug("[%s.%s] %s > %s." % (__name__, self.__class__.__name__,
                                            JS_FILE, JSMIN_FILE))


class build_man(Command):
    description = 'Compile .po files into .mo files'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        log.debug("[%s.%s] Compiling manual from RST sources." % (__name__,
                                                                  self.__class__.__name__))
        pub = Publisher(writer=manpage.Writer())
        pub.set_components(
            reader_name='standalone', parser_name='restructuredtext',
            writer_name='pseudoxml')
        pub.publish(argv=[u'%s' % get_path([DOCDIR, 'man', 'condiment.rst']),
                          u'%s' % get_path([DOCDIR, 'man', 'condiment.1'])])


class build_sphinx(base_build_sphinx):

    def get_sphinx_locale_list(self):
        return set(filter(None, list_items(path=get_path([DOCDIR, 'rst', 'i18n']), dirs=True, files=False))) - set(['pot'])

    def run(self):
        # for locale in self.get_sphinx_locale_list():
        base_build_sphinx.run(self)

        try:
            shutil.rmtree(doctreedir)
        except Exception as e:
            print e


class compile_catalog(base_compile_catalog):

    def get_sphinx_pot_list(self):
        return filter(None, list_files(get_path([DOCDIR, 'rst', 'i18n', 'pot'])))

    def run(self):
        base_compile_catalog.run(self)

        for potfile in self.get_sphinx_pot_list():
            base_compile_catalog.initialize_options(self)
            self.domain = os.path.splitext(os.path.basename(potfile))[0]
            self.directory = get_path(
                [DOCDIR, 'rst', 'i18n']).replace(BASEDIR + os.sep, '')
            self.use_fuzzy = True
            base_compile_catalog.run(self)


class build(base_build):

    def run(self):
        self.run_command('clean')
        self.run_command('update_catalog')
        self.run_command('compile_catalog')
        self.run_command('build_sphinx')
        self.run_command('build_man')
        base_build.run(self)