# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# ----------------------------------------------------------------------------------------------------------------------
# this is the main application menu add/remove items as required
# ----------------------------------------------------------------------------------------------------------------------

response.menu = [
    (T('Home'), False, URL('default', 'index'), [])
]

if auth.is_logged_in():
        response.menu += [
        (T('Lexemes'), False, URL('default', 'lexemes'), []),
        ]
        if auth.has_membership('admin'):
                response.menu += [
                        (T('Usuarios'), False, URL(c='default', f='grid',args=['auth_user']), []),
                ]

# ----------------------------------------------------------------------------------------------------------------------
# provide shortcuts for development. you can remove everything below in production
# ----------------------------------------------------------------------------------------------------------------------

