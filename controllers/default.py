# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

# ---- example index page ----
def index():
    rows = None
    word = None
    exemplo = False
    if request.vars.busca:
        # response.flash = 'busca: ' + request.vars.busca
        word = request.vars.busca
        rows = db.executesql(f"""
                        SELECT entrada, sinal, exemplo_uso, video_sinal, video_exemplo,  ts_rank_cd(tsv_word, q) AS rank
                        FROM lexeme, plainto_tsquery('portuguese','{word}') AS q
                        WHERE q @@ tsv_word
                        and ts_rank_cd(tsv_word, q) >= 0.00001
                        and video_sinal is not null
                        and video_exemplo is not null
                        ORDER BY rank DESC
                        ;
                """, as_dict=True)
        if len(rows) < 1:
            rows = db.executesql(f"""
                        SELECT entrada, sinal, exemplo_uso, video_sinal, video_exemplo,  ts_rank_cd(tsv_frase, q) AS rank
                        FROM lexeme, plainto_tsquery('portuguese','{word}') AS q
                        WHERE q @@ tsv_frase
                        and ts_rank_cd(tsv_frase    , q) >= 0.00001
                        and video_sinal is not null
                        and video_exemplo is not null
                        ORDER BY rank DESC
                        ;
                """, as_dict=True)
            exemplo = True
    return locals()

def make_upload():
    response.view = 'generic.html' # use a generic view
    if request.args(0):
        import os
        word = request.args(0)
        row = db(db.lexeme.entrada == word).select().first()
        if not row:
            row = db(db.lexeme.sinal == word.upper()).select().first()
            if row:
                row.update_record(entrada=word)
                db.commit()
                response.flash = f'{word} foi atualizado'

        if row:
            video_word = os.path.join(request.folder, 'files', 'LemaLibras',word, f"{word}.mp4")

            video_exemplo = os.path.join(request.folder, 'files','LemaLibras', word, f"{word}_exemplo.mp4")
            if not video_exemplo:
                video_exemplo = os.path.join(request.folder, 'files','LemaLibras', word, f"{word}.exemplo.mp4")

            response.flash = f'{video_word} e {video_exemplo} existem'
            # return locals()
            if os.path.exists(video_word) and os.path.exists(video_exemplo):
                response.flash = f'{video_word} e {video_exemplo} existem'
                # return locals()

                with open(video_word, 'rb') as stream:

                    row.update_record(video_sinal=stream)
                    db.commit()

                with open(video_exemplo, 'rb') as stream:

                    row.update_record(video_exemplo=stream)
                    db.commit()        
                response.flash = f'{video_word} e {video_exemplo} foram salvos'
                return locals()
            else:
                response.flash = f'{video_word} e {video_exemplo} não existem'
                return locals()
        else:
            response.flash = f'{word} não existe na tabela lexeme'
            return locals()
    else:
        response.flash = 'não tem argumento'
        return locals()
# ---- API (example) -----
@auth.requires_login()
def api_get_user_email():
    if not request.env.request_method == 'GET': raise HTTP(403)
    return response.json({'status':'success', 'email':auth.user.email})

# ---- Smart Grid (example) -----
@auth.requires_membership('admin') # can only be accessed by members of admin groupd
def grid():
    response.view = 'generic.html' # use a generic view
    tablename = request.args(0)
    if not tablename in db.tables: raise HTTP(403)
    grid = SQLFORM.smartgrid(db[tablename], args=[tablename], deletable=False, editable=False)
    return dict(grid=grid)

# ---- Embedded wiki (example) ----
def wiki():
    auth.wikimenu() # add the wiki to the menu
    return auth.wiki() 

# ---- Action for login/register/etc (required for auth) -----
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())

# ---- action to server uploaded static content (required) ---
@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)

@auth.requires_login()
def lexemes():
    grid = SQLFORM.grid(db.lexeme, user_signature=False)
    return locals()


@auth.requires_membership('admin')
def usuarios():   
    db.auth_user.registration_key.writable=True
    # make_log(f"post vars {request.post_vars} ")
    
    if request.post_vars.email and not request.post_vars.password:
        import random
        import string

        def get_random_string(length):
            # choose from all lowercase letter
            letters = string.ascii_lowercase
            result_str = ''.join(random.choice(letters) for i in range(length))
            logger.debug("Random string of length", length, "is:", result_str)
            return result_str

        request.post_vars.password = get_random_string(8)
    # make_log(f"post vars {request.post_vars} ")
    form = SQLFORM.smartgrid(db.auth_user, linked_tables=['auth_membership'],
        fields=[
        db.auth_user.id,
        db.auth_user.first_name,
        db.auth_user.last_name,
        db.auth_user.email,
        ],      
        maxtextlength=300,
        details=False,
    )
    response.view='generic.html'
    return locals()